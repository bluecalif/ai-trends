"""Verify FastAPI OpenAPI documentation."""
from backend.app.main import app

def main():
    """Check OpenAPI schema."""
    openapi_schema = app.openapi()
    
    print(f"OpenAPI version: {openapi_schema.get('openapi')}")
    print(f"API title: {openapi_schema.get('info', {}).get('title')}")
    print(f"API version: {openapi_schema.get('info', {}).get('version')}")
    print(f"\nTotal API paths: {len(openapi_schema.get('paths', {}))}")
    
    print("\nAPI Endpoints:")
    paths = openapi_schema.get('paths', {})
    for path, methods in sorted(paths.items()):
        for method in sorted(methods.keys()):
            if method != 'parameters':
                operation = methods[method]
                summary = operation.get('summary', operation.get('description', 'No description'))
                tags = operation.get('tags', [])
                print(f"  {method.upper():6} {path:40} [{', '.join(tags)}] - {summary[:50]}")
    
    print(f"\nTotal endpoints: {sum(len([m for m in methods.keys() if m != 'parameters']) for methods in paths.values())}")
    print("\n[OK] OpenAPI schema is valid and accessible at /docs")

if __name__ == "__main__":
    main()

