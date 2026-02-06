"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add the src directory to the path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

client = TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    from app import activities
    
    # Store the original state
    original_activities = {
        "Frisbee Club": {
            "description": "Ultimate frisbee competition and casual disc golf - the only sport where you throw things and call it athletic",
            "schedule": "Saturdays, 10:00 AM - 12:00 PM",
            "max_participants": 16,
            "participants": ["alex@mergington.edu"]
        },
        "Volleyball": {
            "description": "Competitive volleyball training and intramural tournaments",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 14,
            "participants": ["sophia@mergington.edu"]
        },
        "Tennis Team": {
            "description": "Tennis skills development and match play",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["james@mergington.edu"]
        },
        "Drama Club": {
            "description": "Stage acting, theater production, and performing arts",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["isabella@mergington.edu", "lucas@mergington.edu"]
        },
        "Visual Arts": {
            "description": "Painting, drawing, sculpture, and digital art creation",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["mia@mergington.edu"]
        },
        "Debate Team": {
            "description": "Competitive debate, public speaking, and argumentation skills",
            "schedule": "Mondays and Fridays, 3:30 PM - 4:30 PM",
            "max_participants": 15,
            "participants": ["noah@mergington.edu", "ava@mergington.edu"]
        },
        "Science Club": {
            "description": "Hands-on experiments, STEM projects, and scientific inquiry",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["ethan@mergington.edu"]
        },
        "Chess Club1": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 2,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Chess Club2": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
    
    # Clear and reset
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Reset after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities(self, reset_activities):
        """Test getting all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert "Frisbee Club" in data
        assert "Volleyball" in data
        assert len(data) == 11
    
    def test_activity_structure(self, reset_activities):
        """Test that activities have correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        activity = data["Frisbee Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, reset_activities):
        """Test successful signup"""
        response = client.post(
            "/activities/Frisbee Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "signed up" in data["message"].lower()
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Frisbee Club"]["participants"]
    
    def test_signup_activity_not_found(self, reset_activities):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": "test@mergington.edu"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_signup_already_registered(self, reset_activities):
        """Test signup when already registered"""
        response = client.post(
            "/activities/Frisbee Club/signup",
            params={"email": "alex@mergington.edu"}
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()
    
    def test_signup_activity_full(self, reset_activities):
        """Test signup when activity is at capacity"""
        # Chess Club1 has max 2 participants and is already full
        response = client.post(
            "/activities/Chess Club1/signup",
            params={"email": "fullstudent@mergington.edu"}
        )
        assert response.status_code == 400
        assert "full" in response.json()["detail"].lower()


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_success(self, reset_activities):
        """Test successful unregister"""
        response = client.delete(
            "/activities/Frisbee Club/unregister",
            params={"email": "alex@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "unregistered" in data["message"].lower()
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "alex@mergington.edu" not in activities_data["Frisbee Club"]["participants"]
    
    def test_unregister_activity_not_found(self, reset_activities):
        """Test unregister from non-existent activity"""
        response = client.delete(
            "/activities/Nonexistent Activity/unregister",
            params={"email": "test@mergington.edu"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_unregister_not_registered(self, reset_activities):
        """Test unregister when not registered"""
        response = client.delete(
            "/activities/Frisbee Club/unregister",
            params={"email": "notregistered@mergington.edu"}
        )
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"].lower()


class TestSignupAndUnregisterFlow:
    """Integration tests for signup and unregister flows"""
    
    def test_signup_then_unregister(self, reset_activities):
        """Test signing up and then unregistering"""
        email = "flowtest@mergington.edu"
        
        # Sign up
        signup_response = client.post(
            "/activities/Volleyball/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200
        
        # Verify signup
        activities_response = client.get("/activities")
        assert email in activities_response.json()["Volleyball"]["participants"]
        
        # Unregister
        unregister_response = client.delete(
            "/activities/Volleyball/unregister",
            params={"email": email}
        )
        assert unregister_response.status_code == 200
        
        # Verify unregister
        final_response = client.get("/activities")
        assert email not in final_response.json()["Volleyball"]["participants"]
    
    def test_signup_opens_spot_for_others(self, reset_activities):
        """Test that unregistering opens up a spot"""
        # Chess Club1 is full with max 2 participants
        # Remove one participant
        client.delete(
            "/activities/Chess Club1/unregister",
            params={"email": "michael@mergington.edu"}
        )
        
        # Now we should be able to sign up
        response = client.post(
            "/activities/Chess Club1/signup",
            params={"email": "newperson@mergington.edu"}
        )
        assert response.status_code == 200
