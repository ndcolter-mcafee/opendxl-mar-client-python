from dxlmarclient import *
from tests.test_base import BaseMarClientTest
from tests.test_value_constants import *
from tests.mock_marserver import MockMarServer

class TestApiSearch(BaseMarClientTest):

    def test_search(self):
        search_expected_results = {
            "items": [
                {
                    "count": 1,
                    "id": "{1=[{'HostInfo|ip_address': '" + MAR_HOST_IP_ADDRESS_1 + "'}]}",
                    "output": {
                        "HostInfo|ip_address": MAR_HOST_IP_ADDRESS_1
                    }
                },
                {
                    "count": 1,
                    "id": "{1=[{'HostInfo|ip_address': '" + MAR_HOST_IP_ADDRESS_2 + "'}]}",
                    "output": {
                        "HostInfo|ip_address": MAR_HOST_IP_ADDRESS_2
                    }
                }
            ]
        }

        with self.create_client(max_retries=0) as dxl_client:
            # Set up client, and register mock service
            mar_client = MarClient(dxl_client)
            mock_mar_server = MockMarServer(dxl_client)
            dxl_client.connect()
            mock_mar_server.start_service()

            result_context = \
                mar_client.search(
                    projections=[{
                        "name": "HostInfo",
                        "outputs": ["ip_address"]
                    }]
                )

            results_dict = result_context.get_results()

            for item_index in results_dict["items"]:
                if "created_at" in item_index:
                    item_index.pop("created_at", None)

            self.assertDictEqual(
                results_dict,
                search_expected_results
            )

            # End test
            mock_mar_server.stop_service()
            dxl_client.disconnect()

    def test_invokesearchapi(self):
        direct_invoke_search_expected = {
            "body": {
                "id": MAR_SEARCHID
            },
            "code": 200
        }

        with self.create_client(max_retries=0) as dxl_client:
            # Set up client, and register mock service
            mar_client = MarClient(dxl_client)
            mock_mar_server = MockMarServer(dxl_client)
            dxl_client.connect()
            mock_mar_server.start_service()

            response_dict = mar_client._invoke_mar_search_api(MAR_DIRECT_INVOKE_SEARCH_POST)

            self.assertDictEqual(
                response_dict,
                direct_invoke_search_expected
            )

            # End test
            mock_mar_server.stop_service()
            dxl_client.disconnect()


class TestPollInterval(BaseMarClientTest):

    def test_pollinterval(self):
        with self.create_client(max_retries=0) as dxl_client:
            # Set up client, and register mock service
            mar_client = MarClient(dxl_client)

            self.assertEqual(mar_client.poll_interval, 5)

            mar_client.poll_interval = 10

            self.assertEqual(mar_client.poll_interval, 10)


    def test_pollinterval_invalid(self):
        with self.create_client(max_retries=0) as dxl_client:
            # Set up client, and register mock service
            mar_client = MarClient(dxl_client)

            try:
                mar_client.poll_interval = 1
            except Exception as ex:
                self.assertIn("Poll interval must be greater than or equal to ", str(ex))

            self.assertEqual(mar_client.poll_interval, 5)
