from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_homepage():
    r = client.get("/")
    assert r.status_code == 200
    assert "ComicCraft" in r.text


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_docs():
    assert client.get("/docs").status_code == 200


def test_generate_validation():
    r = client.post("/generate-comic/json", json={
        "story_prompt": "x",
        "character_name": "Maya",
        "setting": "School",
        "tone": "Funny",
        "art_style": "Comic Book",
    })
    assert r.status_code == 422
