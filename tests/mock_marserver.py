from dxlclient.service import ServiceRegistrationInfo
from tests.mock_requesthandlers import *

class MockMarServer(object):
    def __init__(self, client):
        self._client = client

        # Create DXL Service Registration object
        self._service_registration_info = ServiceRegistrationInfo(
            self._client,
            "/opendxl/mockmarserver"
        )

    def start_service(self):
        mock_callback = FakeMarApiSearchRequestCallback(self._client)

        self._service_registration_info.add_topic(
            mock_callback.MAR_API_SEARCH_TOPIC,
            mock_callback
        )

        self._service_registration_info.ttl = 5

        self._client.register_service_sync(self._service_registration_info, 10)

    def stop_service(self):
        self._client.unregister_service_sync(self._service_registration_info, 10)
