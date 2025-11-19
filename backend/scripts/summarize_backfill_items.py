"""Summarize backfill items from JSON file."""
import sys
import io
import json
from pathlib import Path

# Fix Windows PowerShell encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def main():
    results_dir = Path(__file__).parent.parent / "tests" / "results"
    json_file = results_dir / "backfill_all_items_20251117_130133.json"
    
    if not json_file.exists():
        print(f"File not found: {json_file}")
        return
    
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    print(f"\n[Backfill Items Summary]")
    print(f"File: {json_file}")
    print(f"Window: {data['window']['start'][:10]} to {data['window']['end'][:10]} ({data['window']['days']} days)")
    print(f"\nSummary:")
    print(f"  Total items: {data['summary']['total_items']}")
    print(f"  Grouped items: {data['summary']['grouped_items']}")
    print(f"  Ungrouped items: {data['summary']['ungrouped_items']}")
    print(f"  Unique groups: {data['summary']['unique_groups']}")
    print(f"  Groups with 2+ members: {data['summary']['groups_with_multiple']}")
    
    # Show groups with multiple members
    if 'groups' in data:
        multi_groups = {gid: info for gid, info in data['groups'].items() if info['member_count'] > 1}
        if multi_groups:
            print(f"\n[Groups with multiple members]")
            for gid, info in sorted(multi_groups.items(), key=lambda x: x[1]['member_count'], reverse=True):
                print(f"\n  Group {gid}: {info['member_count']} members")
                print(f"    Meta count: {info.get('meta_member_count', 'N/A')}")
                for item in info['items']:
                    print(f"    - [{item['published_at'][:10]}] {item['title'][:70]}")
                    print(f"      Source: {item['source']}")
    
    # Show sample items by source
    print(f"\n[Items by source]")
    source_counts = {}
    for item in data['items']:
        source = item.get('source_title', 'Unknown')
        source_counts[source] = source_counts.get(source, 0) + 1
    
    for source, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {source}: {count} items")
    
    print(f"\n[Full details available in JSON file]")
    print(f"  Path: {json_file}")

if __name__ == "__main__":
    main()

