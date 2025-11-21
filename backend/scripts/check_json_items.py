"""Check items in Phase 1.3 JSON result."""
import json
from pathlib import Path

def main():
    f = Path('backend/tests/results/pipeline_phase1_3_collection_20251117_134812.json')
    data = json.loads(f.read_text(encoding='utf-8'))
    
    print(f'Total items in JSON: {len(data.get("items", []))}')
    print(f'Items in window (summary): {data["summary"]["items_in_window"]}')
    if data.get("items"):
        print(f'First item: {data["items"][0]["title"][:60]}')
        print(f'Last item: {data["items"][-1]["title"][:60]}')
        print(f'\nSample item structure:')
        sample = data["items"][0]
        for key in sample.keys():
            value = sample[key]
            if isinstance(value, str) and len(value) > 50:
                value = value[:50] + "..."
            print(f'  {key}: {value}')

if __name__ == "__main__":
    main()





