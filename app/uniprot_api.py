import logging
from io import StringIO

import requests
from Bio import SeqIO
from requests import RequestException
from retry_decorator import retry

from app import settings

logger = logging.getLogger(__name__)


class _UniprotClient:
    """Wrapper around UniProt REST API."""

    def __init__(self):
        self.base_url: str = settings.UNIPROT_RESTAPI_ENDPOINT

    @retry((RequestException,), tries=3)
    def fetch_sequence_by_uniprot_id(self, uniprot_id: str) -> str:
        """Fetch and return protein sequence for the given UniProt Id.

        :param uniprot_id: UniProt accession, e.g. A0A3G5A511
        :return: protein sequence
        """
        request_url = self.base_url + f"/uniprotkb/{uniprot_id}"
        response = self._send_request(request_url, result_format="fasta")
        if response.status_code == requests.codes.ok:
            try:
                with StringIO(response.text) as handler:
                    records = list(SeqIO.parse(handler, "fasta"))
                if len(records) == 1:
                    return str(records[0].seq)
            except BaseException as err:
                logger.exception(f"Unexpected {err=}, {type(err)=}")
                raise
        else:
            logger.error(f"Request failed with the following status code: {response.status_code}")

    @staticmethod
    def _send_request(request_url: str, result_format: str) -> requests.Response:
        response = requests.get(
            request_url,
            params={
                "format": f"{result_format}",
            },
        )
        if response.status_code in (
            requests.codes.no_content,
            requests.codes.not_found,
        ):
            logger.warning("Entry not found in REST API")
        elif response.status_code in (
            requests.codes.unauthorized,
            requests.codes.forbidden,
        ):
            logger.error("Request not authorized.")
        elif response.status_code == requests.codes.internal_server_error:
            logger.error("Request failed with an internal server error!")
        return response


uniprot_client = _UniprotClient()


if __name__ == "__main__":
    logger.info(uniprot_client.fetch_sequence_by_uniprot_id("A0A3G5A511"))
