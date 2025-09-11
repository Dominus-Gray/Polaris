#!/usr/bin/env python3
"""
Test suite for the public OpenAPI endpoint implementation.

This test ensures that:
1. The public OpenAPI spec is accessible without authentication
2. Sensitive endpoints are properly filtered out
3. Version information includes commit SHA
4. Proper caching headers are set
5. OpenAPI spec structure is valid
"""

import os
import pytest
from fastapi.testclient import TestClient

# Set up test environment
os.environ['MONGO_URL'] = 'mongodb://localhost:27017'
os.environ['DB_NAME'] = 'polaris_test'
os.environ['ENVIRONMENT'] = 'development'

# Create log directory to avoid errors
os.makedirs('/var/log/polaris', exist_ok=True)

from backend.server import app


class TestPublicOpenAPI:
    """Test cases for the public OpenAPI endpoint"""
    
    @pytest.fixture
    def client(self):
        """Create test client with proper headers"""
        return TestClient(app)
    
    def test_public_openapi_endpoint_accessible(self, client):
        """Test that the public OpenAPI endpoint is accessible"""
        response = client.get(
            "/openapi/public/v1/openapi.json",
            headers={"host": "localhost"}
        )
        
        assert response.status_code == 200
        assert response.headers.get('content-type') == 'application/json'
    
    def test_openapi_structure_valid(self, client):
        """Test that the returned OpenAPI spec has valid structure"""
        response = client.get(
            "/openapi/public/v1/openapi.json",
            headers={"host": "localhost"}
        )
        
        spec = response.json()
        
        # Check required OpenAPI 3.x fields
        assert 'openapi' in spec
        assert 'info' in spec
        assert 'paths' in spec
        assert spec['openapi'].startswith('3.')
        
        # Check info section
        info = spec['info']
        assert 'title' in info
        assert 'version' in info
        assert 'description' in info
        
        # Check that title matches application
        assert 'Polaris' in info['title']
    
    def test_enhanced_version_format(self, client):
        """Test that version includes semantic version + commit SHA"""
        response = client.get(
            "/openapi/public/v1/openapi.json",
            headers={"host": "localhost"}
        )
        
        spec = response.json()
        version = spec['info']['version']
        
        # Version should be in format: semantic_version+commit_sha
        assert '+' in version, f"Version should contain commit SHA: {version}"
        
        base_version, commit_sha = version.split('+', 1)
        assert len(commit_sha) >= 7, f"Commit SHA should be at least 7 characters: {commit_sha}"
        assert '.' in base_version, f"Base version should be semantic: {base_version}"
    
    def test_caching_headers(self, client):
        """Test that proper caching headers are set"""
        response = client.get(
            "/openapi/public/v1/openapi.json",
            headers={"host": "localhost"}
        )
        
        # Check Cache-Control header
        cache_control = response.headers.get('cache-control')
        assert cache_control is not None, "Missing Cache-Control header"
        assert 'public' in cache_control, "Cache-Control should include 'public'"
        assert 'max-age' in cache_control, "Cache-Control should include 'max-age'"
        
        # Check ETag header
        etag = response.headers.get('etag')
        assert etag is not None, "Missing ETag header"
        assert etag.startswith('"') and etag.endswith('"'), "ETag should be quoted"
    
    def test_sensitive_endpoints_filtered(self, client):
        """Test that sensitive endpoints are not exposed in public spec"""
        response = client.get(
            "/openapi/public/v1/openapi.json",
            headers={"host": "localhost"}
        )
        
        spec = response.json()
        paths = list(spec['paths'].keys())
        
        # Define sensitive patterns that should NOT appear in public spec
        sensitive_patterns = [
            '/auth/',      # Authentication endpoints
            '/admin/',     # Admin endpoints
            '/internal/',  # Internal endpoints
            '/debug/',     # Debug endpoints
            '/system/',    # System endpoints
        ]
        
        found_sensitive = []
        for path in paths:
            for pattern in sensitive_patterns:
                if pattern in path:
                    found_sensitive.append(path)
        
        assert len(found_sensitive) == 0, f"Found sensitive endpoints in public spec: {found_sensitive}"
    
    def test_filtering_effectiveness(self, client):
        """Test that filtering significantly reduces exposed endpoints"""
        # Get public spec
        public_response = client.get(
            "/openapi/public/v1/openapi.json",
            headers={"host": "localhost"}
        )
        public_spec = public_response.json()
        public_paths = len(public_spec['paths'])
        
        # Get full spec for comparison
        full_response = client.get(
            "/openapi.json",
            headers={"host": "localhost"}
        )
        
        if full_response.status_code == 200:
            full_spec = full_response.json()
            full_paths = len(full_spec['paths'])
            
            # Public spec should have significantly fewer endpoints
            assert public_paths < full_paths, "Public spec should have fewer endpoints than full spec"
            
            # Should filter out at least 80% of endpoints for security
            filter_ratio = (full_paths - public_paths) / full_paths
            assert filter_ratio > 0.8, f"Should filter out at least 80% of endpoints, got {filter_ratio:.2%}"
    
    def test_security_schemes_excluded(self, client):
        """Test that security schemes are not included in public spec"""
        response = client.get(
            "/openapi/public/v1/openapi.json",
            headers={"host": "localhost"}
        )
        
        spec = response.json()
        components = spec.get('components', {})
        security_schemes = components.get('securitySchemes', {})
        
        assert len(security_schemes) == 0, f"Public spec should not contain security schemes: {security_schemes}"
    
    def test_public_endpoints_included(self, client):
        """Test that expected public endpoints are included"""
        response = client.get(
            "/openapi/public/v1/openapi.json",
            headers={"host": "localhost"}
        )
        
        spec = response.json()
        paths = list(spec['paths'].keys())
        
        # Should include health and public endpoints
        expected_patterns = ['/health', '/public/']
        found_expected = []
        
        for path in paths:
            for pattern in expected_patterns:
                if pattern in path:
                    found_expected.append(path)
        
        assert len(found_expected) > 0, f"Should include public endpoints, found: {found_expected}"
    
    def test_description_appropriate_for_public(self, client):
        """Test that the description is appropriate for public consumption"""
        response = client.get(
            "/openapi/public/v1/openapi.json",
            headers={"host": "localhost"}
        )
        
        spec = response.json()
        description = spec['info']['description']
        
        # Should mention it's public and filtered
        assert 'public' in description.lower(), "Description should mention this is for public use"
        assert 'authentication' in description.lower(), "Description should mention authentication status"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])