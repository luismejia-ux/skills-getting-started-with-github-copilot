import pytest


def test_get_activities(client, reset_activities):
    """Test fetching all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, dict)
    assert "Basketball" in data
    assert "Soccer" in data
    assert len(data) == 9
    
    # Check activity structure
    basketball = data["Basketball"]
    assert "description" in basketball
    assert "schedule" in basketball
    assert "max_participants" in basketball
    assert "participants" in basketball


def test_signup_new_participant(client, reset_activities):
    """Test signing up a new participant for an activity"""
    response = client.post(
        "/activities/Basketball/signup?email=newstudent@mergington.edu"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "newstudent@mergington.edu" in data["message"]
    
    # Verify participant was added
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert "newstudent@mergington.edu" in activities["Basketball"]["participants"]


def test_signup_existing_participant(client, reset_activities):
    """Test that signing up an already registered participant fails"""
    response = client.post(
        "/activities/Basketball/signup?email=alex@mergington.edu"
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"]


def test_signup_nonexistent_activity(client, reset_activities):
    """Test signing up for a non-existent activity"""
    response = client.post(
        "/activities/NonExistent/signup?email=test@mergington.edu"
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"]


def test_unregister_participant(client, reset_activities):
    """Test unregistering a participant from an activity"""
    # First sign up
    client.post("/activities/Basketball/signup?email=newstudent@mergington.edu")
    
    # Then unregister
    response = client.delete(
        "/activities/Basketball/unregister?email=newstudent@mergington.edu"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered" in data["message"]
    
    # Verify participant was removed
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert "newstudent@mergington.edu" not in activities["Basketball"]["participants"]


def test_unregister_nonexistent_participant(client, reset_activities):
    """Test unregistering a participant who is not registered"""
    response = client.delete(
        "/activities/Basketball/unregister?email=notregistered@mergington.edu"
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "not registered" in data["detail"]


def test_unregister_nonexistent_activity(client, reset_activities):
    """Test unregistering from a non-existent activity"""
    response = client.delete(
        "/activities/NonExistent/unregister?email=test@mergington.edu"
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"]


def test_available_spots(client, reset_activities):
    """Test that available spots are calculated correctly"""
    response = client.get("/activities")
    activities = response.json()
    
    # Basketball has max 15, 1 participant, so 14 spots left
    basketball = activities["Basketball"]
    spots_left = basketball["max_participants"] - len(basketball["participants"])
    assert spots_left == 14
    
    # Soccer has max 22, 2 participants, so 20 spots left
    soccer = activities["Soccer"]
    spots_left = soccer["max_participants"] - len(soccer["participants"])
    assert spots_left == 20


def test_multiple_signups(client, reset_activities):
    """Test signing up multiple users to the same activity"""
    emails = [
        "user1@mergington.edu",
        "user2@mergington.edu",
        "user3@mergington.edu"
    ]
    
    for email in emails:
        response = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response.status_code == 200
    
    # Verify all were added
    response = client.get("/activities")
    activities = response.json()
    chess_participants = activities["Chess Club"]["participants"]
    
    for email in emails:
        assert email in chess_participants


def test_root_redirect(client):
    """Test that root redirects to static files"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert "/static/index.html" in response.headers.get("location", "")
