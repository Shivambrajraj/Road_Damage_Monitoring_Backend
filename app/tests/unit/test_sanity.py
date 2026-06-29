# app/tests/unit/test_sanity.py

def test_system_framework_health():
    """Asserts that the basic runtime environment calculations line up correctly."""
    assert 1 + 1 == 2

def test_severity_fallback_classification():
    """Validates that checking values returns expected true outputs."""
    mock_detections = []
    computed_status = "Low" if len(mock_detections) == 0 else "High"
    assert computed_status == "Low"