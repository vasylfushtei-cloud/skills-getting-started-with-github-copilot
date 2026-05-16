from copy import deepcopy
from urllib.parse import quote

from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)
_original_activities = deepcopy(activities)


def setup_function():
    activities.clear()
    activities.update(deepcopy(_original_activities))


def test_get_activities_returns_all_activities():
    # Arrange
    url = "/activities"

    # Act
    response = client.get(url)

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert isinstance(payload["Chess Club"], dict)
    assert isinstance(payload["Chess Club"]["participants"], list)


def test_signup_adds_new_participant():
    # Arrange
    activity_name = "Science Club"
    email = "newstudent@mergington.edu"
    url = f"/activities/{quote(activity_name, safe='')}/signup?email={quote(email, safe='')}"

    # Act
    response = client.post(url)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate_returns_400():
    # Arrange
    activity_name = "Science Club"
    email = "mia@mergington.edu"
    url = f"/activities/{quote(activity_name, safe='')}/signup?email={quote(email, safe='')}"

    # Act
    response = client.post(url)

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_unsubscribes_student():
    # Arrange
    activity_name = "Science Club"
    email = "mia@mergington.edu"
    url = f"/activities/{quote(activity_name, safe='')}/participants?email={quote(email, safe='')}"

    # Act
    response = client.delete(url)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"
    assert email not in activities[activity_name]["participants"]
