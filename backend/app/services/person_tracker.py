"""Person tracking service for matching items to persons using watch rules."""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_

from backend.app.models.item import Item
from backend.app.models.person import Person
from backend.app.models.person_timeline import PersonTimeline
from backend.app.models.watch_rule import WatchRule
from backend.app.models.entity import Entity
from backend.app.models.item_entity import item_entities


class PersonTracker:
    """Service for tracking persons based on watch rules."""
    
    def __init__(self, db: Session):
        """Initialize PersonTracker with database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    def match_item(self, item: Item) -> List[Person]:
        """Match an item to persons based on watch rules.
        
        Args:
            item: Item to match against watch rules
            
        Returns:
            List of matched Person objects (no duplicates)
        """
        matched_persons = []
        matched_person_ids = set()  # Track matched person IDs to avoid duplicates
        
        # Get all watch rules with person_id
        rules = self.db.query(WatchRule).filter(
            WatchRule.person_id.isnot(None)
        ).order_by(WatchRule.priority.desc()).all()
        
        # Prepare text for matching (title + summary)
        text = f"{item.title or ''} {item.summary_short or ''}".lower()
        
        for rule in rules:
            if self._matches_rule(text, rule):
                person = self.db.query(Person).filter(
                    Person.id == rule.person_id
                ).first()
                if person and person.id not in matched_person_ids:
                    matched_persons.append(person)
                    matched_person_ids.add(person.id)
                    self._add_timeline_event(item, person, rule)
        
        return matched_persons
    
    def _matches_rule(self, text: str, rule: WatchRule) -> bool:
        """Check if text matches watch rule.
        
        Args:
            text: Text to match (lowercase)
            rule: WatchRule to match against
            
        Returns:
            True if text matches rule, False otherwise
        """
        # Include rules: at least one keyword must match (OR condition)
        include_match = False
        if rule.include_rules:
            include_match = any(
                keyword.lower() in text
                for keyword in rule.include_rules
            )
        else:
            # If no include_rules, always match (unless excluded)
            include_match = True
        
        # Exclude rules: if any keyword matches, exclude
        exclude_match = False
        if rule.exclude_rules:
            exclude_match = any(
                keyword.lower() in text
                for keyword in rule.exclude_rules
            )
        
        return include_match and not exclude_match
    
    def _add_timeline_event(
        self,
        item: Item,
        person: Person,
        rule: WatchRule
    ):
        """Add timeline event for matched person and item.
        
        Args:
            item: Matched item
            person: Matched person
            rule: Watch rule that matched
        """
        # Infer event type from item content
        event_type = self._infer_event_type(item.title or "", item.summary_short or "")
        
        # Check for existing timeline event (avoid duplicates)
        existing = self.db.query(PersonTimeline).filter(
            and_(
                PersonTimeline.person_id == person.id,
                PersonTimeline.item_id == item.id
            )
        ).first()
        
        if not existing:
            description = f"{item.title or 'Untitled'}"
            if item.summary_short:
                description += f" - {item.summary_short[:200]}"
            
            event = PersonTimeline(
                person_id=person.id,
                item_id=item.id,
                event_type=event_type,
                description=description
            )
            self.db.add(event)
            self.db.commit()
    
    def _infer_event_type(self, title: str, summary: str) -> str:
        """Infer event type from item title and summary.
        
        Args:
            title: Item title
            summary: Item summary
            
        Returns:
            Event type string: 'paper', 'product', 'investment', 'organization', or 'research_direction'
        """
        text = f"{title} {summary}".lower()
        
        # Check for organization movement keywords first (more specific)
        if any(kw in text for kw in ["join", "leave", "move", "appoint", "hire", "depart", "resign", "hired", "joined"]):
            return "organization"
        
        # Check for investment/funding keywords
        elif any(kw in text for kw in ["investment", "funding", "acquire", "raise", "fund", "series", "round", "acquired"]):
            return "investment"
        
        # Check for product/launch keywords
        elif any(kw in text for kw in ["launch", "release", "announce", "product", "unveil", "introduce", "announced"]):
            return "product"
        
        # Check for paper/publication keywords (less specific, check last)
        elif any(kw in text for kw in ["paper", "published", "arxiv", "research paper", "study", "journal"]):
            return "paper"
        
        # Default to research_direction
        else:
            return "research_direction"
    
    def build_relationship_graph(self, person_id: int) -> Dict:
        """Build relationship graph for a person.
        
        Creates a graph showing connections between:
        - Person -> Items (via timeline events)
        - Items -> Entities (via item_entities)
        
        Args:
            person_id: Person ID to build graph for
            
        Returns:
            Dictionary with person, items, entities, and connections
        """
        person = self.db.query(Person).filter(Person.id == person_id).first()
        if not person:
            return {}
        
        # Get all timeline events for this person
        timeline_events = self.db.query(PersonTimeline).filter(
            PersonTimeline.person_id == person_id
        ).all()
        
        # Get all items from timeline events
        item_ids = [event.item_id for event in timeline_events]
        if not item_ids:
            return {
                "person": person,
                "items": [],
                "entities": [],
                "connections": []
            }
        
        items = self.db.query(Item).filter(Item.id.in_(item_ids)).all()
        
        # Get all entities connected to these items
        entities_dict = {}
        for item in items:
            # Use relationship if loaded, otherwise query
            if hasattr(item, "entities") and item.entities:
                for entity in item.entities:
                    entities_dict[entity.id] = entity
            else:
                # Query item_entities table directly
                from sqlalchemy import select
                rels = self.db.execute(
                    select(item_entities).where(item_entities.c.item_id == item.id)
                ).all()
                for rel in rels:
                    entity = self.db.query(Entity).filter(Entity.id == rel.entity_id).first()
                    if entity:
                        entities_dict[entity.id] = entity
        
        # Build connections
        connections = []
        
        # Person -> Item connections
        for event in timeline_events:
            connections.append({
                "from": f"person_{person.id}",
                "to": f"item_{event.item_id}",
                "type": "mentioned_in",
                "event_type": event.event_type
            })
        
        # Item -> Entity connections
        for item in items:
            item_entity_ids = set()
            if hasattr(item, "entities") and item.entities:
                item_entity_ids = {e.id for e in item.entities}
            else:
                from sqlalchemy import select
                rels = self.db.execute(
                    select(item_entities).where(item_entities.c.item_id == item.id)
                ).all()
                item_entity_ids = {rel.entity_id for rel in rels}
            
            for entity_id in item_entity_ids:
                connections.append({
                    "from": f"item_{item.id}",
                    "to": f"entity_{entity_id}",
                    "type": "contains"
                })
        
        return {
            "person": person,
            "items": items,
            "entities": list(entities_dict.values()),
            "connections": connections
        }
    
    def process_new_items(self, items: List[Item]) -> Dict[str, int]:
        """Process a batch of new items and match them to persons.
        
        Args:
            items: List of items to process
            
        Returns:
            Dictionary with statistics: total_items, matched_items, total_matches
        """
        total_items = len(items)
        matched_items = 0
        total_matches = 0
        
        for item in items:
            matched = self.match_item(item)
            if matched:
                matched_items += 1
                total_matches += len(matched)
        
        return {
            "total_items": total_items,
            "matched_items": matched_items,
            "total_matches": total_matches
        }

