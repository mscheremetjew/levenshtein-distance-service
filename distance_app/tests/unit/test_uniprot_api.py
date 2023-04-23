"""Tests for UniProt api client."""
from unittest.mock import call

import pytest

from distance_app.uniprot_api import uniprot_client


@pytest.mark.parametrize(
    "uniprot_id, expected_call_kwargs, expected_result",
    [
        (
            "A0A3G5A511",
            {"params": {"format": "fasta"}},
            "MIDVLRTSLDECKNEKGLKILTQEDALEYLMTKMRVIKKYSETDKNVRQQQKRLHLKTLLETGFIPHVENDM",
        ),
    ],
)
def test_fetch_sequence_by_uniprot_id_should_succeed(
    mock_valid_uniprot_client_request, uniprot_id, expected_call_kwargs, expected_result
):
    """Test 'fetch_sequence_by_uniprot_id' method should succeed and return expected result."""
    # ... given
    # ... a UniProt API client

    # when ... we call `fetch_sequence_by_uniprot_id`
    actual = uniprot_client.fetch_sequence_by_uniprot_id(uniprot_id)

    # then ... the request should be constructed correctly
    actual_call_kwargs = mock_valid_uniprot_client_request.call_args.kwargs
    assert actual_call_kwargs == expected_call_kwargs

    # and return the expected result
    assert actual == expected_result


@pytest.mark.parametrize(
    "uniprot_id",
    [
        "A0A3G5A511",
    ],
)
def test_fetch_sequence_by_uniprot_id_should_fail(
    mock_invalid_uniprot_client_request,
    mock_logger_uniprot_api,
    uniprot_id,
):
    """Test 'fetch_sequence_by_uniprot_id' method should fail and log error message."""
    # ... given
    # ... a UniProt API client

    # when ... we call `fetch_sequence_by_uniprot_id`
    actual = uniprot_client.fetch_sequence_by_uniprot_id(uniprot_id)

    # then the result should be None
    assert not actual
    # and the expected log messages should be called
    mock_logger_uniprot_api.error.assert_has_calls(
        [
            call("Request failed with an internal server error!"),
            call("Request failed with the following status code: 500"),
        ]
    )
