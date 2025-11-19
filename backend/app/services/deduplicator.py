"""Deduplication and event grouping service.

Features (MVP):
- Exact duplicate check by link.
- Text similarity via TF-IDF cosine (fallback to Jaccard on tokens if sklearn not available).
- Assign dup_group_id for near-duplicates within a recent lookback window.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy.orm import Session

from backend.app.models.item import Item
from backend.app.models.dup_group_meta import DupGroupMeta

try:
    # Optional dependency; fallback if unavailable
    from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore
    from sklearn.metrics.pairwise import cosine_similarity  # type: ignore
    _HAS_SKLEARN = True
except Exception:  # pragma: no cover - only used when sklearn missing
    _HAS_SKLEARN = False


class Deduplicator:
    """Provides duplicate detection and grouping for Items."""

    def __init__(self, db: Session, similarity_threshold: float = 0.7, lookback_days: int = 7, verbose: bool = False):
        self.db = db
        self.similarity_threshold = similarity_threshold
        self.lookback_days = lookback_days
        self.verbose = verbose

    # -------- Core API --------
    def check_exact_duplicate(self, link: str, exclude_id: Optional[int] = None) -> bool:
        """Return True if an item with the same link already exists (excluding optional self id)."""
        q = self.db.query(Item.id).filter(Item.link == link)
        if exclude_id is not None:
            q = q.filter(Item.id != exclude_id)
        exists = self.db.query(q.exists()).scalar()
        if self.verbose:
            try:
                print(f"[Dedup] exact_check link={link!r} exclude_id={exclude_id} -> {bool(exists)}")
            except Exception:
                pass
        return bool(exists)

    def process_new_item(self, item: Item) -> Optional[int]:
        """Check for exact/near duplicates and set dup_group_id if found.

        Returns:
            group_id if a near-duplicate group is assigned, else None.
        """
        if not item.link:
            return None

        # Exact duplicate by link (exclude self if already flushed and has id)
        if self.check_exact_duplicate(item.link, exclude_id=item.id):
            if self.verbose:
                try:
                    print(f"[Dedup] Early exit: exact dup for link={item.link!r}")
                except Exception:
                    pass
            return None

        cutoff = (item.published_at or datetime.utcnow()) - timedelta(days=self.lookback_days)
        recent_items: List[Item] = (
            self.db.query(Item)
            .filter(Item.published_at != None)  # noqa: E711
            .filter(Item.published_at >= cutoff)
            .order_by(Item.published_at.desc())
            .all()
        )
        if self.verbose:
            try:
                print(f"[Dedup] Recent candidates: {len(recent_items)} (cutoff>={cutoff.isoformat()})")
            except Exception:
                pass

        # Build candidate text corpus
        target_text = self._compose_text(item)
        # 1st stage candidate filtering: title 3-gram overlap and (if present) entity/tag overlap
        target_shingles = _title_shingles(item.title or "")
        target_entities = {getattr(e, "name", "").strip().lower() for e in getattr(item, "entities", []) if getattr(e, "name", None)} if hasattr(item, "entities") else set()
        target_tags = set((item.custom_tags or []) if isinstance(item.custom_tags, list) else [])

        best_sim = 0.0
        best_item: Optional[Item] = None

        for cand in recent_items:
            if not cand.link or cand.id == (item.id or -1):
                continue
            # Filter by title shingles
            cand_shingles = _title_shingles(cand.title or "")
            if target_shingles and cand_shingles and len(target_shingles & cand_shingles) == 0:
                continue
            # Optional: entity/tag overlap when available
            try:
                cand_entities = {getattr(e, "name", "").strip().lower() for e in getattr(cand, "entities", []) if getattr(e, "name", None)}
            except Exception:
                cand_entities = set()
            cand_tags = set((cand.custom_tags or []) if isinstance(cand.custom_tags, list) else [])
            if target_entities and cand_entities and len(target_entities & cand_entities) == 0 and target_tags and cand_tags and len(target_tags & cand_tags) == 0:
                # if both sides have signals, require at least one overlap
                continue
            sim = self._augmented_similarity(item, cand, target_text, self._compose_text(cand))
            if self.verbose:
                try:
                    print(f"[Dedup] sim to cand#{cand.id} ~ {sim:.4f}")
                except Exception:
                    pass
            if sim > best_sim:
                best_sim = sim
                best_item = cand

        if best_item and best_sim >= self.similarity_threshold:
            group_id = best_item.dup_group_id or best_item.id
            item.dup_group_id = group_id
            self.db.add(item)
            self.db.commit()
            self.db.refresh(item)
            # Meta sync: update last_updated_at and count
            try:
                meta = self.db.query(DupGroupMeta).filter(DupGroupMeta.dup_group_id == group_id).first()
                now = datetime.utcnow()
                if meta:
                    meta.last_updated_at = now
                    meta.member_count = (meta.member_count or 1) + 1
                    self.db.add(meta)
                    self.db.commit()
                else:
                    # create meta with first_seen_at based on earliest item time available
                    first_seen = best_item.published_at or now
                    self.db.add(DupGroupMeta(dup_group_id=group_id, first_seen_at=first_seen, last_updated_at=now, member_count=2))
                    self.db.commit()
            except Exception as e:
                try:
                    print(f"[Dedup] Meta sync error for group {group_id}: {e}")
                except Exception:
                    pass
            if self.verbose:
                try:
                    print(f"[Dedup] GROUPED item#{item.id} -> group_id={group_id} (best_sim={best_sim:.4f})")
                except Exception:
                    pass
            return group_id

        # No near-duplicate found; do not assign group id here (could become a seed later)
        # Make this item a seed and create meta if missing
        try:
            item.dup_group_id = item.id
            self.db.add(item)
            self.db.commit()
            now = datetime.utcnow()
            first_seen = item.published_at or now
            meta = self.db.query(DupGroupMeta).filter(DupGroupMeta.dup_group_id == item.id).first()
            if not meta:
                self.db.add(DupGroupMeta(dup_group_id=item.id, first_seen_at=first_seen, last_updated_at=first_seen, member_count=1))
                self.db.commit()
            if self.verbose:
                try:
                    print(f"[Dedup] Seeded item#{item.id} as new group (best_sim={best_sim:.4f})")
                except Exception:
                    pass
        except Exception as e:
            try:
                print(f"[Dedup] Seed/meta error for item {item.id}: {e}")
            except Exception:
                pass
        return item.id

    # -------- Helpers --------
    @staticmethod
    def _compose_text(item: Item) -> str:
        parts = [item.title or ""]
        if item.summary_short:
            parts.append(item.summary_short)
        return " ".join(parts).strip()

    def _similarity(self, a: str, b: str) -> float:
        """Compute similarity between two strings.
        Prefer TF-IDF + cosine; fallback to token Jaccard similarity.
        """
        a = (a or "").strip().lower()
        b = (b or "").strip().lower()
        if not a or not b:
            return 0.0
        if _HAS_SKLEARN:
            try:
                vec = TfidfVectorizer(max_features=1000, ngram_range=(1, 2), stop_words="english")
                X = vec.fit_transform([a, b])
                sim = float(cosine_similarity(X[0:1], X[1:2])[0][0])
                if self.verbose:
                    try:
                        print(f"[Dedup] TFIDF sim={sim:.4f}")
                    except Exception:
                        pass
                return max(0.0, min(1.0, sim))
            except Exception as e:
                if self.verbose:
                    try:
                        print(f"[Dedup] TFIDF error: {e} -> fallback Jaccard")
                    except Exception:
                        pass
        # Fallback: Jaccard on tokens
        ta = set(_simple_tokens(a))
        tb = set(_simple_tokens(b))
        if not ta or not tb:
            return 0.0
        inter = len(ta & tb)
        union = len(ta | tb)
        sim = (inter / union) if union else 0.0
        if self.verbose:
            try:
                print(f"[Dedup] Jaccard sim={sim:.4f} | |A|={len(ta)} |B|={len(tb)} inter={inter} union={union}")
            except Exception:
                pass
        return sim

    # -------- Augmented similarity (entities/tags/time) --------
    def _augmented_similarity(self, a_item: Item, b_item: Item, a_text: Optional[str] = None, b_text: Optional[str] = None) -> float:
        """Augment base text similarity with entities/custom_tags overlap and time proximity.

        This improves practical grouping of continued coverage (evolution) while
        keeping behavior backward compatible for base similarity.
        """
        base = self._similarity(a_text if a_text is not None else self._compose_text(a_item),
                                b_text if b_text is not None else self._compose_text(b_item))

        bonus = 0.0

        # Entities overlap bonus
        try:
            a_entities = {getattr(e, "name", "").strip().lower() for e in getattr(a_item, "entities", []) if getattr(e, "name", None)}
            b_entities = {getattr(e, "name", "").strip().lower() for e in getattr(b_item, "entities", []) if getattr(e, "name", None)}
            ent_overlap = len(a_entities & b_entities)
        except Exception:
            a_entities = set()
            b_entities = set()
            ent_overlap = 0
        if ent_overlap >= 2:
            bonus += 0.15
        elif ent_overlap == 1:
            bonus += 0.10

        # Custom tag overlap bonus
        try:
            a_tags = set((a_item.custom_tags or []) if isinstance(a_item.custom_tags, list) else [])
            b_tags = set((b_item.custom_tags or []) if isinstance(b_item.custom_tags, list) else [])
        except Exception:
            a_tags = set()
            b_tags = set()
        tag_overlap = len(a_tags & b_tags)
        if tag_overlap > 0:
            bonus += min(0.10, 0.05 * tag_overlap)

        # Time proximity bonus
        try:
            if a_item.published_at and b_item.published_at:
                dt = abs((a_item.published_at - b_item.published_at).total_seconds())
                hours = dt / 3600.0
                if hours <= 24:
                    bonus += 0.05
                elif hours <= 72:
                    bonus += 0.03
        except Exception:
            pass

        total = max(0.0, min(1.0, base + bonus))
        if self.verbose:
            try:
                print(f"[Dedup] base={base:.4f} bonus={bonus:.4f} ent_overlap={ent_overlap} tag_overlap={tag_overlap}")
            except Exception:
                pass
        return total


def _simple_tokens(s: str) -> List[str]:
    # simple tokenization by non-alnum split, filter short tokens
    import re

    return [t for t in re.split(r"[^a-z0-9]+", s.lower()) if len(t) > 1]


def _title_shingles(title: str, n: int = 3) -> set:
    tokens = _simple_tokens(title)
    if len(tokens) < n:
        return set(tokens)  # fallback to tokens for very short titles
    return {tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)}

