"""Integration tests for POST /encounters endpoint."""

import pytest
from fastapi.testclient import TestClient

from app.app import app

client = TestClient(app)

API_KEY = "dev-api-key"
HEADERS = {"X-API-Key": API_KEY}


class TestCreateEncounterValidation:
    """Table tests for validation errors."""

    @pytest.mark.parametrize(
        "payload,expected_field,expected_msg",
        [
            pytest.param(
                {
                    "providerId": "PRV-456",
                    "encounterDate": "2024-01-15T10:30:00Z",
                    "encounterType": "follow_up",
                },
                "patientId",
                "Field required",
                id="missing_patient_id",
            ),
            pytest.param(
                {
                    "patientId": "PAT-123",
                    "encounterDate": "2024-01-15T10:30:00Z",
                    "encounterType": "follow_up",
                },
                "providerId",
                "Field required",
                id="missing_provider_id",
            ),
            pytest.param(
                {
                    "patientId": "PAT-123",
                    "providerId": "PRV-456",
                    "encounterType": "follow_up",
                },
                "encounterDate",
                "Field required",
                id="missing_encounter_date",
            ),
            pytest.param(
                {
                    "patientId": "PAT-123",
                    "providerId": "PRV-456",
                    "encounterDate": "2024-01-15T10:30:00Z",
                },
                "encounterType",
                "Field required",
                id="missing_encounter_type",
            ),
            pytest.param(
                {
                    "patientId": "PAT-123",
                    "providerId": "PRV-456",
                    "encounterDate": "2024-01-15T10:30:00Z",
                    "encounterType": "invalid_type",
                },
                "encounterType",
                "Must be one of:",
                id="invalid_encounter_type",
            ),
            pytest.param(
                {
                    "patientId": "",
                    "providerId": "PRV-456",
                    "encounterDate": "2024-01-15T10:30:00Z",
                    "encounterType": "follow_up",
                },
                "patientId",
                "at least 1",
                id="empty_patient_id",
            ),
        ],
    )
    def test_validation_error(self, payload, expected_field, expected_msg):
        """Test that invalid payloads return 422 with correct error details."""
        response = client.post("/encounters", headers=HEADERS, json=payload)

        assert response.status_code == 422
        errors = response.json()["detail"]
        assert len(errors) >= 1

        error = errors[0]
        assert expected_field in error["loc"]
        assert expected_msg in error["msg"]


class TestCreateEncounterHappyPath:
    """Happy path tests for creating encounters."""

    def test_create_encounter_success(self):
        """Test successful encounter creation."""
        payload = {
            "patientId": "PAT-123",
            "providerId": "PRV-456",
            "encounterDate": "2024-01-15T10:30:00Z",
            "encounterType": "follow_up",
            "clinicalData": {"notes": "Patient presents with..."},
        }

        response = client.post("/encounters", headers=HEADERS, json=payload)

        assert response.status_code == 200
        data = response.json()

        # Server-generated fields
        assert "encounterId" in data
        assert "createdAt" in data
        assert "updatedAt" in data
        assert data["createdBy"] == "dev-user"

        # Client-provided fields preserved
        assert data["patientId"] == "PAT-123"
        assert data["providerId"] == "PRV-456"
        assert data["encounterType"] == "follow_up"
        assert data["clinicalData"] == {"notes": "Patient presents with..."}

    def test_create_encounter_minimal(self):
        """Test encounter creation with minimal required fields."""
        payload = {
            "patientId": "PAT-999",
            "providerId": "PRV-999",
            "encounterDate": "2024-06-01T09:00:00Z",
            "encounterType": "initial_assessment",
        }

        response = client.post("/encounters", headers=HEADERS, json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["clinicalData"] == {}

    def test_create_encounter_requires_auth(self):
        """Test that endpoint requires authentication."""
        payload = {
            "patientId": "PAT-123",
            "providerId": "PRV-456",
            "encounterDate": "2024-01-15T10:30:00Z",
            "encounterType": "follow_up",
        }

        response = client.post("/encounters", json=payload)

        assert response.status_code == 422  # Missing header

    def test_create_encounter_invalid_api_key(self):
        """Test that invalid API key is rejected."""
        payload = {
            "patientId": "PAT-123",
            "providerId": "PRV-456",
            "encounterDate": "2024-01-15T10:30:00Z",
            "encounterType": "follow_up",
        }

        response = client.post(
            "/encounters", headers={"X-API-Key": "wrong-key"}, json=payload
        )

        assert response.status_code == 401
