import re
import time

from dxlclient.callbacks import RequestCallback
from dxlclient.message import Response, ErrorResponse
from dxlbootstrap.util import MessageUtils
from tests.test_value_constants import *

def _make_output_item(output):
    return {"count": 1,
            "created_at": time.strftime('%Y-%M-%dT%H:%M:%SZ'),
            "id": "{1=[" + str(output) + "]}",
            "output": output}


def _make_output_items(output_id, output_values):
    return [_make_output_item({output_id: output_value})
            for output_value in output_values]


class FakeMarApiSearchRequestCallback(RequestCallback):
    """
    'fake_mar_api_search' request handler registered with topic
    '/mcafee/mar/service/api/search'
    """

    MAR_API_SEARCH_TOPIC = "/mcafee/mar/service/api/search"

    IP_ADDRESS_ID = "ipaddrid"
    PROCESSES_ID = "processesid"

    RESULTS = {IP_ADDRESS_ID: _make_output_items("HostInfo|ip_address",
                                                 ["192.168.130.152",
                                                  "192.168.130.133"]),
               PROCESSES_ID: _make_output_items("Processes|name", MAR_PROCESS_IDS)}

    PROJECTION_TO_ID = {
        "HostInfo|ip_address": IP_ADDRESS_ID,
        "Processes": PROCESSES_ID
    }

    def __init__(self, client):
        """
        Constructor parameters:

        :param app: The application this handler is associated with
        """
        super(FakeMarApiSearchRequestCallback, self).__init__()
        self._client = client

    @staticmethod
    def _make_error_response(code, message):
        return {"code": code,
                "body": {
                    "applicationErrorList": [
                        {"code": code,
                         "message": message}
                    ]
                }}

    @staticmethod
    def _get_projection_as_string(projections):
        result = ""
        for projection in projections:
            result += projection["name"]
            if "outputs" in projection:
                result += "|"
                result += "|".join(
                    [output for output in projection["outputs"]])
        return result

    def on_request(self, request):
        """
        Invoked when a request message is received.

        :param request: The request message
        """
        request_payload = MessageUtils.json_payload_to_dict(request)

        try:
            res = Response(request)

            payload = {"code": 200,
                       "body": {}}

            if request_payload["target"] == "/v1/simple":
                payload = self.v1_simple(request_payload, payload)
            else:
                payload = self.v1_complex(request_payload, payload)

            MessageUtils.dict_to_json_payload(res, payload)
            self._client.send_response(res)

        except Exception as ex:
            err_res = ErrorResponse(request, error_code=0,
                                    error_message=MessageUtils.encode(str(ex)))
            self._client.send_response(err_res)

    def v1_simple(self, request_payload, response_payload):
        if request_payload["method"] != 'POST':
            response_payload = self._make_error_response(
                405, "Unsupported method")
        elif "body" not in request_payload or \
            "projections" not in request_payload["body"]:
            response_payload = self._make_error_response(
                400, "Missing body or projections parameter")
        else:
            projections_as_str = self._get_projection_as_string(
                request_payload["body"]["projections"])
            if projections_as_str in self.PROJECTION_TO_ID:
                response_payload["body"]["id"] = self.PROJECTION_TO_ID[
                    projections_as_str]
            else:
                response_payload = self._make_error_response(
                    501, "Unsupported projection")

        return response_payload

    def v1_complex(self, request_payload, response_payload):
        request_id = re.match(r".*/v1/(\w+)/.*",
                              request_payload["target"])
        if request_id and request_id.group(1) in self.RESULTS:
            request_items = self.RESULTS[request_id.group(1)]
            if request_payload["target"].endswith("/status"):
                if request_payload["method"] != 'GET':
                    response_payload = self._make_error_response(
                        405, "Unsupported method")
                else:
                    response_payload["body"]["results"] = len(request_items)
                    response_payload["body"]["errors"] = 0
                    response_payload["body"]["hosts"] = 1
                    response_payload["body"]["subscribedHosts"] = 1
                    response_payload["body"]["status"] = "FINISHED"
            elif request_payload["target"].endswith("/results"):
                if request_payload["method"] != 'GET':
                    response_payload = self._make_error_response(
                        405, "Unsupported method")
                elif "parameters" in request_payload and \
                    "$offset" in request_payload["parameters"] and \
                    "$limit" in request_payload["parameters"]:
                    offset = request_payload["parameters"]["$offset"]
                    limit = request_payload["parameters"]["$limit"]
                    response_payload["body"]["items"] = request_items[
                        offset:
                        offset + limit
                    ]
                else:
                    response_payload["body"]["items"] = request_items
        else:
            response_payload = self._make_error_response(
                404, "Id not found")

        return response_payload
