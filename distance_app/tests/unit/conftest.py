"""Fixtures for app unit tests."""
import pytest
from faker import Faker

fake = Faker()


@pytest.fixture
def mock_protein_sequence():
    return "MIDVLRTSLDECKNEKGLKILTQEDALEYLMTKMRVIKKYSETDKNVRQQQKRLHLKTLLETGFIPHVENDM"


@pytest.fixture
def mock_fasta_formatted_sequence(mock_protein_sequence):
    fasta_header = ">tr|A0A3G5A511|A0A3G5A511_9VIRU DNA-directed RNA polymerase OS=Harvfovirus sp OX=2487768 GN=Harvfovirus44_2 PE=3 SV=1"
    return fasta_header + f"\n{mock_protein_sequence}"


@pytest.fixture
def mock_valid_uniprot_client_request(mocker, mock_fasta_formatted_sequence):
    """Mock requests.get method to return 200 status code and valid text."""

    class MockResponse:
        def __init__(self, text, status_code):
            self.text = text
            self.status_code = status_code

        def text(self):
            return self.text()

    return mocker.patch(
        "distance_app.uniprot_api.requests.get", return_value=MockResponse(mock_fasta_formatted_sequence, 200)
    )


@pytest.fixture
def mock_invalid_uniprot_client_request(mocker):
    """Mock requests.get method to return 500 status code."""

    class MockResponse:
        def __init__(self, text, status_code):
            self.text = text
            self.status_code = status_code

        def text(self):
            return self.text()

    return mocker.patch("distance_app.uniprot_api.requests.get", return_value=MockResponse("", 500))


@pytest.fixture
def mock_logger_uniprot_api(mocker):  # noqa: D103
    return mocker.patch("distance_app.uniprot_api.logger")
