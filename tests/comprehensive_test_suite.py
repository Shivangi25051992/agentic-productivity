#!/usr/bin/env python3
"""
Comprehensive End-to-End Test Suite
Covers all user flows, edge cases, and error scenarios
"""

import pytest
import requests
from datetime import datetime
import time

API_BASE = "http://localhost:8000"

# ============================================================================
# 1. AUTHENTICATION TESTS
# ============================================================================

class TestAuthentication:
    """Test all authentication flows"""
    
    def test_signup_valid_user(self):
        """Positive: Valid signup"""
        response = requests.post(f"{API_BASE}/auth/signup", json={
            "email": f"test{int(time.time())}@example.com",
            "password": "SecurePass123!",
            "name": "Test User"
        })
        assert response.status_code == 200
        assert "token" in response.json() or "uid" in response.json()
    
    def test_signup_invalid_email(self):
        """Negative: Invalid email format"""
        response = requests.post(f"{API_BASE}/auth/signup", json={
            "email": "invalid-email",
            "password": "SecurePass123!",
            "name": "Test User"
        })
        assert response.status_code in [400, 422]
        assert "email" in response.text.lower()
    
    def test_signup_weak_password(self):
        """Negative: Weak password"""
        response = requests.post(f"{API_BASE}/auth/signup", json={
            "email": "test@example.com",
            "password": "123",  # Too short
            "name": "Test User"
        })
        assert response.status_code in [400, 422]
    
    def test_signup_duplicate_email(self):
        """Negative: Duplicate email"""
        email = f"duplicate{int(time.time())}@example.com"
        
        # First signup
        requests.post(f"{API_BASE}/auth/signup", json={
            "email": email,
            "password": "SecurePass123!",
            "name": "Test User"
        })
        
        # Second signup with same email
        response = requests.post(f"{API_BASE}/auth/signup", json={
            "email": email,
            "password": "SecurePass123!",
            "name": "Test User 2"
        })
        assert response.status_code in [400, 409]
    
    def test_login_valid_credentials(self):
        """Positive: Valid login"""
        # Use existing test user
        response = requests.post(f"{API_BASE}/auth/login", json={
            "id_token": "valid_token_here"  # Replace with actual token
        })
        # Note: This will fail without proper token - needs Firebase integration
    
    def test_login_invalid_token(self):
        """Negative: Invalid token"""
        response = requests.post(f"{API_BASE}/auth/login", json={
            "id_token": "invalid_token"
        })
        assert response.status_code == 401
    
    def test_login_expired_token(self):
        """Negative: Expired token"""
        # Test with expired token
        pass  # Implement with actual expired token
    
    def test_unauthorized_access(self):
        """Negative: Access protected endpoint without auth"""
        response = requests.get(f"{API_BASE}/auth/me")
        assert response.status_code == 401

# ============================================================================
# 2. CHAT/MEAL LOGGING TESTS
# ============================================================================

class TestChatMealLogging:
    """Test AI chat and meal logging"""
    
    @pytest.fixture
    def auth_headers(self):
        """Get auth headers for authenticated requests"""
        # Return headers with valid token
        return {"Authorization": "Bearer test_token"}
    
    def test_log_simple_meal(self, auth_headers):
        """Positive: Log simple meal"""
        response = requests.post(
            f"{API_BASE}/chat",
            json={"user_input": "2 eggs"},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data['items']) > 0
        assert data['items'][0]['category'] == 'meal'
        assert data['items'][0]['data']['calories'] > 0
    
    def test_log_multi_food(self, auth_headers):
        """Positive: Log multiple foods"""
        response = requests.post(
            f"{API_BASE}/chat",
            json={"user_input": "2 eggs, 1 bowl rice, 5 pistachios"},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data['items']) == 3  # Should parse into 3 items
    
    def test_ambiguous_input_clarification(self, auth_headers):
        """Positive: Ambiguous input triggers clarification"""
        response = requests.post(
            f"{API_BASE}/chat",
            json={"user_input": "eggs"},  # No quantity
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get('needs_clarification') == True
        assert 'how many' in data.get('clarification_question', '').lower()
    
    def test_empty_input(self, auth_headers):
        """Negative: Empty input"""
        response = requests.post(
            f"{API_BASE}/chat",
            json={"user_input": ""},
            headers=auth_headers
        )
        assert response.status_code in [400, 422]
    
    def test_very_long_input(self, auth_headers):
        """Negative: Input exceeds max length"""
        response = requests.post(
            f"{API_BASE}/chat",
            json={"user_input": "a" * 10000},  # 10k characters
            headers=auth_headers
        )
        assert response.status_code in [400, 422]
    
    def test_special_characters(self, auth_headers):
        """Edge: Special characters in input"""
        response = requests.post(
            f"{API_BASE}/chat",
            json={"user_input": "<script>alert('xss')</script>"},
            headers=auth_headers
        )
        # Should sanitize and not execute
        assert response.status_code in [200, 400]
    
    def test_sql_injection_attempt(self, auth_headers):
        """Security: SQL injection attempt"""
        response = requests.post(
            f"{API_BASE}/chat",
            json={"user_input": "'; DROP TABLE users; --"},
            headers=auth_headers
        )
        # Should be safely handled
        assert response.status_code in [200, 400]
    
    def test_unknown_food(self, auth_headers):
        """Edge: Unknown food item"""
        response = requests.post(
            f"{API_BASE}/chat",
            json={"user_input": "xyzabc123 food"},
            headers=auth_headers
        )
        assert response.status_code == 200
        # Should handle gracefully with estimation or clarification

# ============================================================================
# 3. DASHBOARD/PROFILE TESTS
# ============================================================================

class TestDashboard:
    """Test dashboard and profile functionality"""
    
    def test_get_dashboard_data(self, auth_headers):
        """Positive: Get dashboard data"""
        response = requests.get(
            f"{API_BASE}/dashboard",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert 'calories' in data
        assert 'protein' in data
    
    def test_get_profile(self, auth_headers):
        """Positive: Get user profile"""
        response = requests.get(
            f"{API_BASE}/auth/me",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert 'email' in data
        assert 'name' in data
    
    def test_update_profile(self, auth_headers):
        """Positive: Update profile"""
        response = requests.put(
            f"{API_BASE}/profile",
            json={"name": "Updated Name"},
            headers=auth_headers
        )
        assert response.status_code == 200

# ============================================================================
# 4. ERROR HANDLING TESTS
# ============================================================================

class TestErrorHandling:
    """Test error scenarios"""
    
    def test_network_timeout(self):
        """Negative: Network timeout"""
        try:
            response = requests.get(f"{API_BASE}/health", timeout=0.001)
        except requests.exceptions.Timeout:
            pass  # Expected
    
    def test_invalid_endpoint(self):
        """Negative: Invalid endpoint"""
        response = requests.get(f"{API_BASE}/invalid-endpoint")
        assert response.status_code == 404
    
    def test_malformed_json(self, auth_headers):
        """Negative: Malformed JSON"""
        response = requests.post(
            f"{API_BASE}/chat",
            data="invalid json",
            headers={**auth_headers, "Content-Type": "application/json"}
        )
        assert response.status_code in [400, 422]
    
    def test_missing_required_fields(self, auth_headers):
        """Negative: Missing required fields"""
        response = requests.post(
            f"{API_BASE}/chat",
            json={},  # Missing user_input
            headers=auth_headers
        )
        assert response.status_code in [400, 422]
    
    def test_server_error_recovery(self):
        """Edge: Server error returns friendly message"""
        # Simulate server error
        pass  # Implement with mock

# ============================================================================
# 5. PERFORMANCE TESTS
# ============================================================================

class TestPerformance:
    """Test performance and scalability"""
    
    def test_response_time_under_200ms(self, auth_headers):
        """Performance: API response < 200ms"""
        start = time.time()
        response = requests.get(f"{API_BASE}/health")
        elapsed = (time.time() - start) * 1000
        
        assert response.status_code == 200
        assert elapsed < 200, f"Response took {elapsed}ms (> 200ms)"
    
    def test_concurrent_requests(self, auth_headers):
        """Load: Handle concurrent requests"""
        import concurrent.futures
        
        def make_request():
            return requests.post(
                f"{API_BASE}/chat",
                json={"user_input": "2 eggs"},
                headers=auth_headers
            )
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in futures]
        
        # All should succeed
        assert all(r.status_code == 200 for r in results)
    
    def test_rate_limiting(self, auth_headers):
        """Security: Rate limiting works"""
        # Make 100 requests rapidly
        responses = []
        for _ in range(100):
            response = requests.post(
                f"{API_BASE}/chat",
                json={"user_input": "test"},
                headers=auth_headers
            )
            responses.append(response)
        
        # Should see 429 (Too Many Requests) at some point
        status_codes = [r.status_code for r in responses]
        assert 429 in status_codes, "Rate limiting not working"

# ============================================================================
# 6. DATA INTEGRITY TESTS
# ============================================================================

class TestDataIntegrity:
    """Test data consistency and integrity"""
    
    def test_meal_log_persists(self, auth_headers):
        """Data: Logged meal persists"""
        # Log meal
        response1 = requests.post(
            f"{API_BASE}/chat",
            json={"user_input": "2 eggs"},
            headers=auth_headers
        )
        assert response1.status_code == 200
        
        # Verify it appears in history
        time.sleep(1)  # Allow time for write
        response2 = requests.get(
            f"{API_BASE}/chat/history",
            headers=auth_headers
        )
        assert response2.status_code == 200
        history = response2.json()
        assert len(history['messages']) > 0
    
    def test_concurrent_writes_no_data_loss(self, auth_headers):
        """Data: Concurrent writes don't lose data"""
        import concurrent.futures
        
        def log_meal(meal_id):
            return requests.post(
                f"{API_BASE}/chat",
                json={"user_input": f"meal {meal_id}"},
                headers=auth_headers
            )
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(log_meal, i) for i in range(5)]
            results = [f.result() for f in futures]
        
        # All should succeed
        assert all(r.status_code == 200 for r in results)
        
        # Verify all 5 meals in history
        time.sleep(2)
        response = requests.get(
            f"{API_BASE}/chat/history",
            headers=auth_headers
        )
        # Should have at least 5 new messages
        assert len(response.json()['messages']) >= 5

# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

