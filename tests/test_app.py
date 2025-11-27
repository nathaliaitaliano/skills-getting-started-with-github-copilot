import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

client = TestClient(app)


class TestActivitiesEndpoint:
    """Tests for the /activities endpoint"""

    def test_get_activities_returns_all_activities(self):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        
        # Check that we have the expected activities
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        assert "Basketball Team" in data
        assert "Tennis Club" in data
        assert "Art Studio" in data
        assert "Drama Club" in data
        assert "Debate Team" in data
        assert "Science Club" in data

    def test_activities_have_required_fields(self):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignupEndpoint:
    """Tests for the /activities/{activity_name}/signup endpoint"""

    def test_signup_new_participant(self):
        """Test signing up a new participant for an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=test@example.com"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up test@example.com for Chess Club" in data["message"]

    def test_signup_duplicate_participant_fails(self):
        """Test that signing up the same participant twice fails"""
        email = "duplicate@example.com"
        
        # First signup should succeed
        response1 = client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Second signup with same email should fail
        response2 = client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]

    def test_signup_nonexistent_activity_fails(self):
        """Test that signing up for nonexistent activity fails"""
        response = client.post(
            "/activities/NonexistentActivity/signup?email=test@example.com"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_increases_participant_count(self):
        """Test that signup increases the participant count"""
        email = "newparticipant@example.com"
        
        # Get initial participant count
        activities_before = client.get("/activities").json()
        initial_count = len(activities_before["Basketball Team"]["participants"])
        
        # Signup
        response = client.post(
            f"/activities/Basketball%20Team/signup?email={email}"
        )
        assert response.status_code == 200
        
        # Get updated participant count
        activities_after = client.get("/activities").json()
        updated_count = len(activities_after["Basketball Team"]["participants"])
        
        assert updated_count == initial_count + 1
        assert email in activities_after["Basketball Team"]["participants"]


class TestUnregisterEndpoint:
    """Tests for the /activities/{activity_name}/unregister endpoint"""

    def test_unregister_existing_participant(self):
        """Test unregistering an existing participant"""
        email = "unregister@example.com"
        
        # First, signup
        client.post(f"/activities/Drama%20Club/signup?email={email}")
        
        # Then unregister
        response = client.delete(
            f"/activities/Drama%20Club/unregister?email={email}"
        )
        assert response.status_code == 200
        data = response.json()
        assert f"Unregistered {email} from Drama Club" in data["message"]

    def test_unregister_nonexistent_participant_fails(self):
        """Test that unregistering non-existent participant fails"""
        response = client.delete(
            "/activities/Science%20Club/unregister?email=nonexistent@example.com"
        )
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]

    def test_unregister_nonexistent_activity_fails(self):
        """Test that unregistering from nonexistent activity fails"""
        response = client.delete(
            "/activities/NonexistentActivity/unregister?email=test@example.com"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_decreases_participant_count(self):
        """Test that unregister decreases the participant count"""
        email = "toremove@example.com"
        
        # Signup first
        client.post(f"/activities/Art%20Studio/signup?email={email}")
        
        # Get count before unregister
        activities_before = client.get("/activities").json()
        count_before = len(activities_before["Art Studio"]["participants"])
        
        # Unregister
        response = client.delete(
            f"/activities/Art%20Studio/unregister?email={email}"
        )
        assert response.status_code == 200
        
        # Get count after unregister
        activities_after = client.get("/activities").json()
        count_after = len(activities_after["Art Studio"]["participants"])
        
        assert count_after == count_before - 1
        assert email not in activities_after["Art Studio"]["participants"]


class TestRootEndpoint:
    """Tests for the root endpoint"""

    def test_root_redirects_to_static(self):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
