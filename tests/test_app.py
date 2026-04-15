import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from src.app import app, activities, get_activities, signup_for_activity, unregister_from_activity


client = TestClient(app)


def test_get_activities_returns_all_activities():
    # Arrange
    expected_activity_names = {
        "Chess Club",
        "Programming Class",
        "Gym Class",
        "Soccer Team",
        "Basketball Club",
        "Art Club",
        "Drama Club",
        "Debate Team",
        "Math Olympiad",
    }

    # Act
    result = get_activities()

    # Assert
    assert set(result) == expected_activity_names
    assert result["Chess Club"]["max_participants"] == 12


def test_signup_for_activity_adds_student_to_participants():
    # Arrange
    activity_name = "Soccer Team"
    email = "new.student@mergington.edu"

    # Act
    result = signup_for_activity(activity_name, email)

    # Assert
    assert result == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]


def test_signup_for_activity_raises_for_unknown_activity():
    # Arrange
    activity_name = "Robotics Club"
    email = "student@mergington.edu"

    # Act
    with pytest.raises(HTTPException) as exc_info:
        signup_for_activity(activity_name, email)

    # Assert
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Activity not found"


def test_signup_for_activity_raises_when_student_is_already_signed_up():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    with pytest.raises(HTTPException) as exc_info:
        signup_for_activity(activity_name, email)

    # Assert
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Student already signed up for this activity"


def test_unregister_from_activity_removes_student_from_participants():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    result = unregister_from_activity(activity_name, email)

    # Assert
    assert result == {"message": f"Unregistered {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]


def test_unregister_from_activity_raises_for_unknown_activity():
    # Arrange
    activity_name = "Robotics Club"
    email = "student@mergington.edu"

    # Act
    with pytest.raises(HTTPException) as exc_info:
        unregister_from_activity(activity_name, email)

    # Assert
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Activity not found"


def test_unregister_from_activity_raises_when_student_is_not_registered():
    # Arrange
    activity_name = "Soccer Team"
    email = "student@mergington.edu"

    # Act
    with pytest.raises(HTTPException) as exc_info:
        unregister_from_activity(activity_name, email)

    # Assert
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Student not registered for this activity"


def test_root_redirects_to_static_index():
    # Arrange

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_endpoint_returns_activity_payload():
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert payload["Chess Club"]["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
    assert payload["Drama Club"]["participants"] == []


def test_signup_endpoint_adds_student_via_http():
    # Arrange
    activity_name = "Soccer Team"
    email = "new.student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]


def test_signup_endpoint_rejects_unknown_activity_via_http():
    # Arrange
    activity_name = "Robotics Club"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_endpoint_removes_student_via_http():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]


def test_unregister_endpoint_rejects_non_participant_via_http():
    # Arrange
    activity_name = "Soccer Team"
    email = "student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student not registered for this activity"}