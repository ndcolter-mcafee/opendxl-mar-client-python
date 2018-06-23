import os
import threading
import subprocess

from tests.test_base import BaseMarClientTest
from tests.test_value_constants import *
from tests.mock_marserver import MockMarServer

SAMPLE_FOLDER = str(os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
).replace("\\", "/")) + "/sample"

BASIC_FOLDER = SAMPLE_FOLDER + "/basic"
ADVANCED_FOLDER = SAMPLE_FOLDER + "/advanced"

COMMON_PY_FILENAME = SAMPLE_FOLDER + "/common.py"
NEW_COMMON_PY_FILENAME = COMMON_PY_FILENAME + ".new"

CONFIG_FOLDER = str(os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"))
CONFIG_FILENAME = CONFIG_FOLDER + "/dxlclient.config"
NEW_CONFIG_FILENAME = CONFIG_FILENAME + ".new"
CA_FILENAME = CONFIG_FOLDER + "/ca-bundle.crt"
CERT_FILENAME = CONFIG_FOLDER + "/client.crt"
KEY_FILENAME = CONFIG_FOLDER + "/client.key"

def overwrite_file_line(filename, target, replacement):
    base_file = open(filename, 'r')
    new_file = open(filename + ".new", "w+")

    for line in base_file:
        if line.startswith(target):
            line = replacement
        new_file.write(line)

    base_file.close()
    new_file.close()

    os.remove(filename)
    os.rename(filename + ".new", filename)


def overwrite_common_py():
    target_line = "CONFIG_FILE = "
    replacement_line = target_line + "\"" + CONFIG_FILENAME + "\"\n"
    overwrite_file_line(COMMON_PY_FILENAME, target_line, replacement_line)


def overwrite_config_cert_locations():
    target_line = "BrokerCertChain = "
    replacement_line = target_line + "\"" + CA_FILENAME + "\"\n"
    overwrite_file_line(CONFIG_FILENAME, target_line, replacement_line)

    target_line = "CertFile = "
    replacement_line = target_line + "\"" + CERT_FILENAME + "\"\n"
    overwrite_file_line(CONFIG_FILENAME, target_line, replacement_line)

    target_line = "PrivateKey = "
    replacement_line = target_line + "\"" + KEY_FILENAME + "\"\n"
    overwrite_file_line(CONFIG_FILENAME, target_line, replacement_line)

class SampleRunner(object):

    def __init__(self, cmd, target=''):
        self.cmd = cmd
        self.target_file = target
        self.process = None
        self.output = "Not started"


    def run(self, timeout):
        def target():
            self.process = subprocess.Popen(
                [self.cmd, self.target_file],
                stdout=subprocess.PIPE,
                #stderr=subprocess.PIPE,
            )
            self.output = self.process.communicate()[0]

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(timeout)
        if thread.is_alive():
            self.process.terminate()
            thread.join()

        return self.output.decode('utf-8')

class TestApiSearch(BaseMarClientTest):

    def test_basicsearch_example(self):
        # Modify common/config files to work with local ".\test" directory
        overwrite_common_py()
        overwrite_config_cert_locations()

        # Modify sample file to include necessary sample data
        sample_filename = BASIC_FOLDER + "/basic_search_example.py"

        with self.create_client(max_retries=0) as dxl_client:
            # Set up client, and register mock service
            mock_mar_server = MockMarServer(dxl_client)
            dxl_client.connect()
            mock_mar_server.start_service()

            sample_runner = SampleRunner(
                cmd="python",
                target=sample_filename
            )
            output = sample_runner.run(timeout=10)

            self.assertNotIn("Error", output)
            self.assertIn("Results:", output)
            self.assertIn(MAR_HOST_IP_ADDRESS_1, output)
            self.assertIn(MAR_HOST_IP_ADDRESS_2, output)

            mock_mar_server.stop_service()
            dxl_client.disconnect()


    def test_basicpaging_example(self):
        # Modify common/config files to work with local ".\test" directory
        overwrite_common_py()
        overwrite_config_cert_locations()

        # Modify sample file to include necessary sample data
        sample_filename = BASIC_FOLDER + "/basic_paging_example.py"

        target_line = "HOST_IP = "
        replacement_line = target_line + "\"" + MAR_HOST_IP_ADDRESS_1 + "\"\n"
        overwrite_file_line(sample_filename, target_line, replacement_line)

        with self.create_client(max_retries=0) as dxl_client:
            # Set up client, and register mock service
            mock_mar_server = MockMarServer(dxl_client)
            dxl_client.connect()
            mock_mar_server.start_service()

            sample_runner = SampleRunner(
                cmd="python",
                target=sample_filename
            )
            output = sample_runner.run(timeout=10)

            self.assertNotIn("Error", output)
            for process_id in MAR_PROCESS_IDS:
                self.assertIn(process_id, output)

            mock_mar_server.stop_service()
            dxl_client.disconnect()
