import copy

def test_root_redirect(client):
    # TestClient follows redirects by default, so disable it
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code in (307, 302)
    assert "index.html" in resp.headers.get("location", "")

def test_get_activities(client):
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # at least one of the known activities present
    assert "Chess Club" in data

def test_signup_and_duplicate(client):
    # choose an activity and a fresh email
    email = "newstudent@mergington.edu"
    activity = "Chess Club"
    # make sure email not already there
    assert email not in client.app.state.activities[activity]["participants"]

    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200

    resp2 = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp2.status_code == 400
    assert "already" in resp2.json().get("detail", "").lower()

def test_remove_participant(client):
    email = "toremove@mergington.edu"
    activity = "Programming Class"
    # sign up first
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200

    # now remove
    resp2 = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp2.status_code == 200

    # removing again should 404
    resp3 = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp3.status_code == 404


# pytest fixtures
import pytest
from fastapi.testclient import TestClient
from src import app as app_module

@pytest.fixture(autouse=True)
def reset_activities():
    # deep copy the original dataset before tests run
    original = copy.deepcopy(app_module.activities)
    yield
    # restore after each test
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(original))

@pytest.fixture

def client():
    # also store on client.app.state for easier access in tests
    test_client = TestClient(app_module.app)
    test_client.app.state.activities = app_module.activities
    return test_client
