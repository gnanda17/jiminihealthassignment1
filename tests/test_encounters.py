"""Integration tests for /encounters endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.app import app

client = TestClient(app)

API_KEY = "dev-api-key"
HEADERS = {"X-API-Key": API_KEY}


class TestCreateEncounter:
    """Tests for POST /encounters."""

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

    def test_success(self):
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

    def test_minimal_fields(self):
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

    def test_requires_auth(self):
        """Test that endpoint requires authentication."""
        payload = {
            "patientId": "PAT-123",
            "providerId": "PRV-456",
            "encounterDate": "2024-01-15T10:30:00Z",
            "encounterType": "follow_up",
        }

        response = client.post("/encounters", json=payload)

        assert response.status_code == 422  # Missing header

    def test_invalid_api_key(self):
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


class TestListEncounters:
    """Tests for GET /encounters."""

    @pytest.fixture(autouse=True)
    def seed_encounters(self):
        """Seed test encounters for filter tests."""
        encounters = [
            {
                "patientId": "PAT-ALICE",
                "providerId": "PRV-DOC1",
                "encounterDate": "2024-01-10T10:00:00Z",
                "encounterType": "initial_assessment",
            },
            {
                "patientId": "PAT-ALICE",
                "providerId": "PRV-DOC2",
                "encounterDate": "2024-01-20T14:00:00Z",
                "encounterType": "follow_up",
            },
            {
                "patientId": "PAT-BOB",
                "providerId": "PRV-DOC1",
                "encounterDate": "2024-02-15T09:00:00Z",
                "encounterType": "follow_up",
            },
        ]
        for enc in encounters:
            client.post("/encounters", headers=HEADERS, json=enc)

    @pytest.mark.parametrize(
        "query_params,expected_field",
        [
            pytest.param(
                {"dateFrom": "not-a-date"},
                "dateFrom",
                id="invalid_date_from_format",
            ),
            pytest.param(
                {"dateTo": "2024-13-45"},
                "dateTo",
                id="invalid_date_to_format",
            ),
        ],
    )
    def test_validation_error(self, query_params, expected_field):
        """Test that invalid query params return 422."""
        response = client.get("/encounters", headers=HEADERS, params=query_params)

        assert response.status_code == 422
        errors = response.json()["detail"]
        assert len(errors) >= 1
        assert expected_field in str(errors)

    @pytest.mark.parametrize(
        "query_params,expected_patient_ids",
        [
            pytest.param(
                {"patientId": "PAT-ALICE"},
                ["PAT-ALICE", "PAT-ALICE"],
                id="filter_by_patient_id",
            ),
            pytest.param(
                {"providerId": "PRV-DOC1"},
                ["PAT-ALICE", "PAT-BOB"],
                id="filter_by_provider_id",
            ),
            pytest.param(
                {"encounterType": "follow_up"},
                ["PAT-ALICE", "PAT-BOB"],
                id="filter_by_encounter_type",
            ),
            pytest.param(
                {"dateFrom": "2024-01-15T00:00:00Z"},
                ["PAT-ALICE", "PAT-BOB"],
                id="filter_by_date_from",
            ),
            pytest.param(
                {"dateTo": "2024-01-15T00:00:00Z"},
                ["PAT-ALICE"],
                id="filter_by_date_to",
            ),
            pytest.param(
                {"patientId": "PAT-ALICE", "encounterType": "follow_up"},
                ["PAT-ALICE"],
                id="filter_by_multiple_params",
            ),
            pytest.param(
                {"patientId": "PAT-NONEXISTENT"},
                [],
                id="filter_returns_empty",
            ),
        ],
    )
    def test_filter(self, query_params, expected_patient_ids):
        """Test that filters return correct encounters."""
        response = client.get("/encounters", headers=HEADERS, params=query_params)

        assert response.status_code == 200
        data = response.json()
        actual_patient_ids = [enc["patientId"] for enc in data]

        for patient_id in expected_patient_ids:
            assert patient_id in actual_patient_ids

    def test_requires_auth(self):
        """Test that endpoint requires authentication."""
        response = client.get("/encounters")

        assert response.status_code == 422  # Missing header

    def test_invalid_api_key(self):
        """Test that invalid API key is rejected."""
        response = client.get("/encounters", headers={"X-API-Key": "wrong-key"})

        assert response.status_code == 401


class TestGetEncounter:
    """Tests for GET /encounters/{encounter_id}."""

    def test_success(self):
        """Test retrieving a specific encounter."""
        payload = {
            "patientId": "PAT-GET-TEST",
            "providerId": "PRV-456",
            "encounterDate": "2024-01-15T10:30:00Z",
            "encounterType": "initial_assessment",
        }
        create_response = client.post("/encounters", headers=HEADERS, json=payload)
        encounter_id = create_response.json()["encounterId"]

        response = client.get(f"/encounters/{encounter_id}", headers=HEADERS)

        assert response.status_code == 200
        data = response.json()
        assert data["encounterId"] == encounter_id
        assert data["patientId"] == "PAT-GET-TEST"

    def test_not_found(self):
        """Test that non-existent encounter returns 404."""
        response = client.get("/encounters/non-existent-id", headers=HEADERS)

        assert response.status_code == 404
        assert response.json()["detail"] == "Encounter not found"

    def test_requires_auth(self):
        """Test that endpoint requires authentication."""
        response = client.get("/encounters/some-id")

        assert response.status_code == 422  # Missing header

    def test_invalid_api_key(self):
        """Test that invalid API key is rejected."""
        response = client.get("/encounters/some-id", headers={"X-API-Key": "wrong-key"})

        assert response.status_code == 401
