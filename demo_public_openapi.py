#!/usr/bin/env python3
"""
Demo script showing how to use the public OpenAPI endpoint

This script demonstrates:
1. Fetching the public OpenAPI specification
2. Parsing version information
3. Listing available public endpoints
4. Comparing with the full API specification
"""

import requests
import json
import sys
from urllib.parse import urljoin

def demo_public_openapi(base_url="http://localhost:8000"):
    """
    Demonstrate the public OpenAPI endpoint functionality
    """
    print("🔍 Polaris Public OpenAPI Demo")
    print("=" * 50)
    
    public_url = urljoin(base_url, "/openapi/public/v1/openapi.json")
    full_url = urljoin(base_url, "/openapi.json")
    
    try:
        # Fetch public OpenAPI spec
        print(f"📡 Fetching public spec from: {public_url}")
        response = requests.get(public_url, timeout=10)
        
        if response.status_code == 200:
            public_spec = response.json()
            print("✅ Successfully retrieved public OpenAPI specification")
            
            # Display basic information
            info = public_spec.get('info', {})
            print(f"📋 Title: {info.get('title', 'N/A')}")
            print(f"🏷️  Version: {info.get('version', 'N/A')}")
            print(f"📝 Description: {info.get('description', 'N/A')[:100]}...")
            
            # Parse version information
            version = info.get('version', '')
            if '+' in version:
                base_version, commit_sha = version.split('+', 1)
                print(f"🔄 Base Version: {base_version}")
                print(f"🏗️  Commit SHA: {commit_sha}")
            
            # Show caching headers
            print(f"⚡ Cache-Control: {response.headers.get('cache-control', 'N/A')}")
            print(f"🏷️  ETag: {response.headers.get('etag', 'N/A')}")
            
            # List public endpoints
            paths = public_spec.get('paths', {})
            print(f"\\n🌐 Public Endpoints ({len(paths)} total):")
            for path, methods in paths.items():
                method_list = [m.upper() for m in methods.keys() if m.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']]
                print(f"   {', '.join(method_list):15} {path}")
            
            # Try to compare with full spec (if accessible)
            print(f"\\n📊 Comparing with full API specification...")
            try:
                full_response = requests.get(full_url, timeout=5)
                if full_response.status_code == 200:
                    full_spec = full_response.json()
                    full_paths = len(full_spec.get('paths', {}))
                    public_paths = len(paths)
                    filtered_count = full_paths - public_paths
                    filter_ratio = (filtered_count / full_paths) * 100 if full_paths > 0 else 0
                    
                    print(f"   📈 Full API endpoints: {full_paths}")
                    print(f"   🌐 Public endpoints: {public_paths}")
                    print(f"   🛡️  Filtered out: {filtered_count} ({filter_ratio:.1f}%)")
                    print(f"   ✅ Filtering ratio: {filter_ratio:.1f}% (recommended: >80%)")
                else:
                    print(f"   ⚠️  Full API spec not accessible (status: {full_response.status_code})")
            except Exception as e:
                print(f"   ⚠️  Could not fetch full API spec: {e}")
            
            # Show example usage
            print(f"\\n💡 Example Usage:")
            print(f"   curl -X GET '{public_url}'")
            print(f"   curl -H 'If-None-Match: {response.headers.get('etag', '')}' '{public_url}'")
            
            # Save spec for inspection
            output_file = "/tmp/polaris_public_openapi.json"
            with open(output_file, 'w') as f:
                json.dump(public_spec, f, indent=2)
            print(f"\\n💾 Saved specification to: {output_file}")
            
            return True
            
        else:
            print(f"❌ Failed to fetch public spec: HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        print(f"   Make sure the Polaris server is running at {base_url}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON response: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main demo function"""
    # Default to localhost, but accept command line argument
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    success = demo_public_openapi(base_url)
    
    if success:
        print("\\n🎉 Demo completed successfully!")
        print("\\n📚 Next steps:")
        print("   • Use the OpenAPI spec to generate client SDKs")
        print("   • Integrate with API documentation tools")
        print("   • Set up monitoring for the public endpoints")
        print("   • Configure CDN caching for the specification")
    else:
        print("\\n💥 Demo failed. Check server status and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()