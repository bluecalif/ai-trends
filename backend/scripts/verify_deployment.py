"""Verify deployment endpoints and system health."""
import sys
import io
import json
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

# Fix Windows PowerShell encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def test_endpoint(url: str, description: str) -> dict:
    """Test an API endpoint and return result."""
    try:
        req = Request(url, headers={"User-Agent": "ai-trend-verification/1.0"})
        with urlopen(req, timeout=10) as response:
            status_code = response.getcode()
            body = response.read().decode('utf-8')
            try:
                response_data = json.loads(body)
            except json.JSONDecodeError:
                response_data = body
            
            return {
                "url": url,
                "description": description,
                "status_code": status_code,
                "success": status_code == 200,
                "response": response_data if status_code == 200 else None,
                "error": None
            }
    except HTTPError as e:
        return {
            "url": url,
            "description": description,
            "status_code": e.code,
            "success": False,
            "response": None,
            "error": f"HTTP {e.code}: {e.reason}"
        }
    except URLError as e:
        return {
            "url": url,
            "description": description,
            "status_code": None,
            "success": False,
            "response": None,
            "error": str(e.reason) if hasattr(e, 'reason') else str(e)
        }
    except Exception as e:
        return {
            "url": url,
            "description": description,
            "status_code": None,
            "success": False,
            "response": None,
            "error": str(e)
        }

def main():
    import os
    from backend.app.core.config import get_settings
    
    settings = get_settings()
    
    # Get API URL from environment or use default
    api_url = os.getenv("API_URL") or "http://localhost:8000"
    if not api_url.startswith("http"):
        api_url = f"https://{api_url}"
    
    print(f"\n[Deployment Verification] Testing API: {api_url}\n")
    
    # Test endpoints
    endpoints = [
        ("/", "Root endpoint"),
        ("/health", "Health check"),
        ("/api/items?page=1&page_size=5", "Items list (with pagination)"),
        ("/api/items?field=research&page=1&page_size=5", "Items filtered by field (research)"),
        ("/api/sources", "Sources list"),
        ("/api/persons", "Persons list"),
        ("/api/constants/fields", "Constants: fields"),
        ("/api/constants/custom-tags", "Constants: custom tags"),
    ]
    
    results = []
    for path, description in endpoints:
        url = f"{api_url.rstrip('/')}{path}"
        result = test_endpoint(url, description)
        results.append(result)
        
        # Print result
        status_icon = "[OK]" if result["success"] else "[FAIL]"
        print(f"{status_icon} {description}")
        print(f"   URL: {url}")
        if result["success"]:
            print(f"   Status: {result['status_code']}")
            if result["response"]:
                if isinstance(result["response"], dict):
                    # Show key fields
                    if "status" in result["response"]:
                        print(f"   Response: status={result['response'].get('status')}")
                    elif "items" in result["response"]:
                        items_count = len(result["response"].get("items", []))
                        total = result["response"].get("total", 0)
                        print(f"   Response: {items_count} items (total: {total})")
                    elif isinstance(result["response"], list):
                        print(f"   Response: {len(result['response'])} items")
                    else:
                        print(f"   Response: {str(result['response'])[:100]}")
        else:
            error_msg = result['error'] or f"Status {result['status_code']}"
            print(f"   Error: {error_msg}")
        print()
    
    # Summary
    successful = sum(1 for r in results if r["success"])
    total = len(results)
    
    print(f"\n[Deployment Verification] ===== Summary =====")
    print(f"Successful: {successful}/{total}")
    print(f"Failed: {total - successful}/{total}")
    
    if successful == total:
        print("\n[Deployment Verification] All endpoints are working correctly! ✅")
    else:
        print("\n[Deployment Verification] Some endpoints failed. Please check the errors above. ⚠️")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

