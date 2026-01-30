"""Tests for middleware PHI redaction."""

import pytest

from app.middleware import redact_query_params


class TestRedactQueryParams:
    """Tests for PHI query param redaction."""

    @pytest.mark.parametrize(
        "input_query,expected",
        [
            pytest.param(
                "patientId=PAT-123",
                "patientId=[REDACTED]",
                id="patient_id_camel",
            ),
            pytest.param(
                "patient_id=PAT-123",
                "patient_id=[REDACTED]",
                id="patient_id_snake",
            ),
            pytest.param(
                "patientId=PAT-123&providerId=PRV-456",
                "patientId=[REDACTED]&providerId=PRV-456",
                id="mixed_params",
            ),
            pytest.param(
                "providerId=PRV-456&encounterType=follow_up",
                "providerId=PRV-456&encounterType=follow_up",
                id="no_phi_params",
            ),
            pytest.param(
                "",
                "",
                id="empty_string",
            ),
        ],
    )
    def test_redact(self, input_query, expected):
        """Test that PHI query params are redacted."""
        assert redact_query_params(input_query) == expected
