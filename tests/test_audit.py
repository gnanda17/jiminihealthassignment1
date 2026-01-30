"""Integration tests for /audit endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.app import app

client = TestClient(app)

API_KEY = "dev-api-key"
HEADERS = {"X-API-Key": API_KEY}


class TestListAuditLogs:
    """Tests for GET /audit/encounters."""

    @pytest.fixture(autouse=True)
    def seed_audit_logs(self):
        """Seed encounters and access them to generate audit logs."""
        encounters = [
            {
                "patientId": "PAT-AUDIT-1",
                "providerId": "PRV-001",
                "encounterDate": "2024-01-10T10:00:00Z",
                "encounterType": "initial_assessment",
            },
            {
                "patientId": "PAT-AUDIT-2",
                "providerId": "PRV-002",
                "encounterDate": "2024-01-20T14:00:00Z",
                "encounterType": "follow_up",
            },
        ]
        self.encounter_ids = []
        for enc in encounters:
            resp = client.post("/encounters", headers=HEADERS, json=enc)
            self.encounter_ids.append(resp.json()["encounterId"])

        # Access encounters to generate audit logs
        for enc_id in self.encounter_ids:
            client.get(f"/encounters/{enc_id}", headers=HEADERS)

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
        response = client.get("/audit/encounters", headers=HEADERS, params=query_params)

        assert response.status_code == 422
        errors = response.json()["detail"]
        assert len(errors) >= 1
        assert expected_field in str(errors)

    def test_success(self):
        """Test listing audit logs returns correct structure."""
        response = client.get("/audit/encounters", headers=HEADERS)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2

        log = data[0]
        assert "auditId" in log
        assert "encounterId" in log
        assert "userId" in log
        assert "timestamp" in log

    @pytest.mark.parametrize(
        "filter_key,filter_value_attr,check_field",
        [
            pytest.param(
                "encounterId",
                "encounter_ids",
                "encounterId",
                id="filter_by_encounter_id",
            ),
            pytest.param(
                "userId",
                None,
                "userId",
                id="filter_by_user_id",
            ),
        ],
    )
    def test_filter(self, filter_key, filter_value_attr, check_field):
        """Test that filters return correct audit logs."""
        if filter_value_attr:
            filter_value = getattr(self, filter_value_attr)[0]
        else:
            filter_value = "dev-user"

        response = client.get(
            "/audit/encounters", headers=HEADERS, params={filter_key: filter_value}
        )

        assert response.status_code == 200
        data = response.json()
        assert all(log[check_field] == filter_value for log in data)

    def test_filter_by_date_range(self):
        """Test filtering by date range."""
        response = client.get(
            "/audit/encounters",
            headers=HEADERS,
            params={
                "dateFrom": "2020-01-01T00:00:00Z",
                "dateTo": "2030-01-01T00:00:00Z",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2

    def test_filter_returns_empty(self):
        """Test filter with no matches returns empty list."""
        response = client.get(
            "/audit/encounters",
            headers=HEADERS,
            params={"encounterId": "nonexistent-id"},
        )

        assert response.status_code == 200
        assert response.json() == []

    def test_requires_auth(self):
        """Test that endpoint requires authentication."""
        response = client.get("/audit/encounters")

        assert response.status_code == 422  # Missing header

    def test_invalid_api_key(self):
        """Test that invalid API key is rejected."""
        response = client.get("/audit/encounters", headers={"X-API-Key": "wrong-key"})

        assert response.status_code == 401
