"""
Basic API tests for the admin panel
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.main import app
from app.database import SessionLocal, init_db
from app.models import User
from app.auth import get_password_hash

client = TestClient(app)

# Test credentials
TEST_ADMIN_EMAIL = "test_admin@test.com"
TEST_ADMIN_PASSWORD = "testpass123"
TEST_TOKEN = None


@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    """Setup test database"""
    init_db()
    db = SessionLocal()
    
    # Create test admin user
    test_admin = User(
        name="Test Admin",
        email=TEST_ADMIN_EMAIL,
        password_hash=get_password_hash(TEST_ADMIN_PASSWORD),
        role="admin"
    )
    db.add(test_admin)
    db.commit()
    db.close()
    
    yield
    
    # Cleanup
    db = SessionLocal()
    db.query(User).filter(User.email == TEST_ADMIN_EMAIL).delete()
    db.commit()
    db.close()


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_login_success():
    """Test successful login"""
    global TEST_TOKEN
    
    response = client.post(
        "/api/auth/login",
        json={
            "email": TEST_ADMIN_EMAIL,
            "password": TEST_ADMIN_PASSWORD
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    
    TEST_TOKEN = data["data"]["access_token"]


def test_login_failure():
    """Test failed login with wrong credentials"""
    response = client.post(
        "/api/auth/login",
        json={
            "email": TEST_ADMIN_EMAIL,
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False


def test_get_current_user():
    """Test getting current user info"""
    if not TEST_TOKEN:
        pytest.skip("No token available")
    
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {TEST_TOKEN}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["email"] == TEST_ADMIN_EMAIL


def test_get_bot_config():
    """Test getting bot configuration (public endpoint)"""
    response = client.get("/api/bot-config")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "greeting_message" in data["data"]


def test_get_faqs_unauthorized():
    """Test accessing FAQs without token should fail"""
    response = client.get("/api/kb/faqs")
    assert response.status_code == 403


def test_get_faqs_authorized():
    """Test accessing FAQs with token"""
    if not TEST_TOKEN:
        pytest.skip("No token available")
    
    response = client.get(
        "/api/kb/faqs",
        headers={"Authorization": f"Bearer {TEST_TOKEN}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "faqs" in data["data"]


def test_create_faq():
    """Test creating a new FAQ"""
    if not TEST_TOKEN:
        pytest.skip("No token available")
    
    response = client.post(
        "/api/kb/faqs",
        headers={"Authorization": f"Bearer {TEST_TOKEN}"},
        json={
            "question": "Test question?",
            "answer": "Test answer",
            "subject_id": None,
            "tag_ids": []
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "id" in data["data"]


def test_get_tags():
    """Test getting all tags"""
    if not TEST_TOKEN:
        pytest.skip("No token available")
    
    response = client.get(
        "/api/kb/tags",
        headers={"Authorization": f"Bearer {TEST_TOKEN}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_get_subjects():
    """Test getting all subjects"""
    if not TEST_TOKEN:
        pytest.skip("No token available")
    
    response = client.get(
        "/api/subjects",
        headers={"Authorization": f"Bearer {TEST_TOKEN}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_get_dashboard_stats():
    """Test getting dashboard statistics"""
    if not TEST_TOKEN:
        pytest.skip("No token available")
    
    response = client.get(
        "/api/analytics/dashboard",
        headers={"Authorization": f"Bearer {TEST_TOKEN}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "stats" in data["data"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
