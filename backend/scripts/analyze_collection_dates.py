"""Analyze date distribution in collection results."""
import json
from collections import Counter
from pathlib import Path

def analyze_dates(json_file: str):
    """Analyze date distribution from collection JSON."""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    window = data['window']
    items = data.get('items', [])
    
    # Extract dates
    dates = []
    for item in items:
        pub_date = item.get('published_at', '')
        if pub_date:
            dates.append(pub_date[:10])  # YYYY-MM-DD
    
    date_counts = Counter(dates)
    
    print(f"윈도우: {window['start'][:10]} ~ {window['end'][:10]} ({window['days']}일)")
    print(f"총 아이템: {len(items)}개")
    print(f"\n날짜별 수집 개수:")
    for date, count in sorted(date_counts.items()):
        print(f"  {date}: {count}개")
    
    # Find date range
    if dates:
        min_date = min(dates)
        max_date = max(dates)
        print(f"\n실제 수집 기간: {min_date} ~ {max_date}")
        
        # Calculate days
        from datetime import datetime
        start = datetime.fromisoformat(window['start'][:10])
        end = datetime.fromisoformat(window['end'][:10])
        min_dt = datetime.fromisoformat(min_date)
        max_dt = datetime.fromisoformat(max_date)
        
        window_days = (end - start).days + 1
        actual_days = (max_dt - min_dt).days + 1
        
        print(f"윈도우 기간: {window_days}일")
        print(f"실제 수집 기간: {actual_days}일")
        print(f"누락된 기간: {window_days - actual_days}일")
    
    # Source-wise analysis
    print(f"\n소스별 날짜 분포:")
    if 'item_statistics' in data and 'items_by_source_and_date' in data['item_statistics']:
        for source, date_dict in data['item_statistics']['items_by_source_and_date'].items():
            dates_list = sorted(date_dict.keys())
            if dates_list:
                print(f"  {source}:")
                print(f"    기간: {dates_list[0]} ~ {dates_list[-1]} ({len(dates_list)}일)")
                print(f"    총 개수: {sum(date_dict.values())}개")

if __name__ == "__main__":
    json_file = "backend/tests/results/pipeline_phase1_3_collection_20251117_135315.json"
    analyze_dates(json_file)

