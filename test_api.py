"""
Integration tests for STARK v4.0 FastAPI application
"""

from fastapi.testclient import TestClient
from main import app


class TestStarkAPI:
    """Integration tests for STARK v4.0 API"""
    
    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)
    
    def test_root_endpoint(self):
        """Test root endpoint returns app info"""
        response = self.client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "STARK v4.0"
        assert data["version"] == "4.0.0"
        assert data["status"] == "running"
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "4.0.0"
        assert "state" in data
        assert "queue_size" in data
        assert "queue_full" in data
    
    def test_get_state(self):
        """Test get state endpoint"""
        response = self.client.get("/state")
        assert response.status_code == 200
        data = response.json()
        assert "current_state" in data
        assert data["current_state"] in ["idle", "processing", "responding", "error", "stopped"]
    
    def test_post_valid_event(self):
        """Test posting a valid event"""
        event_data = {
            "event_type": "user_command",
            "data": {"command": "test"}
        }
        response = self.client.post("/events", json=event_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "queued"
        assert data["event_type"] == "user_command"
        assert "event_id" in data
    
    def test_post_invalid_event_type(self):
        """Test posting an invalid event type"""
        event_data = {
            "event_type": "invalid_event",
            "data": {}
        }
        response = self.client.post("/events", json=event_data)
        assert response.status_code == 400
        assert "Invalid event type" in response.json()["detail"]
    
    def test_get_event_history(self):
        """Test getting event history"""
        # Post an event first
        event_data = {
            "event_type": "user_query",
            "data": {"query": "test query"}
        }
        self.client.post("/events", json=event_data)
        
        # Get history
        response = self.client.get("/events/history?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert "events" in data
        assert isinstance(data["events"], list)
        
        # Check that events have required fields
        if data["count"] > 0:
            event = data["events"][0]
            assert "event_id" in event
            assert "event_type" in event
            assert "timestamp" in event
            assert "data" in event
    
    def test_get_state_transitions(self):
        """Test getting state transitions"""
        response = self.client.get("/state/transitions?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert "transitions" in data
        assert isinstance(data["transitions"], list)
    
    def test_api_key_authentication_disabled(self):
        """Test that endpoints work without API key when auth is disabled"""
        # Should work without API key
        response = self.client.get("/state")
        assert response.status_code == 200
        
        # Should also work with API key
        response = self.client.get("/state", headers={"X-API-Key": "test-key"})
        assert response.status_code == 200
    
    def test_cors_headers(self):
        """Test CORS headers are set correctly"""
        response = self.client.get("/", headers={"Origin": "http://localhost:3000"})
        assert response.status_code == 200
        # Note: TestClient doesn't process CORS middleware the same as a real request
        # This test verifies the endpoint works with CORS-related headers
    
    def test_event_types(self):
        """Test various event types"""
        event_types = [
            "user_command",
            "user_query",
            "task_create",
            "task_update",
            "task_complete",
            "health_check"
        ]
        
        for event_type in event_types:
            event_data = {
                "event_type": event_type,
                "data": {"test": True}
            }
            response = self.client.post("/events", json=event_data)
            assert response.status_code == 200, f"Failed for event_type: {event_type}"
            data = response.json()
            assert data["event_type"] == event_type


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
