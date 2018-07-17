from tests.test_base import *
from tests.test_value_constants import *
from tests.mock_marserver import MockMarServer

class TestSamples(BaseClientTest):

    def test_basicsearch_example(self):
        # Modify sample file to include necessary sample data
        sample_filename = self.BASIC_FOLDER + "/basic_search_example.py"

        with self.create_client(max_retries=0) as dxl_client:
            dxl_client.connect()

            with MockMarServer(dxl_client):
                mock_print = BaseClientTest.run_sample(sample_filename)

                mock_print.assert_any_call(
                    StringContains("Results:")
                )

                mock_print.assert_any_call(
                    StringContains(MAR_HOST_IP_ADDRESS_1)
                )

                mock_print.assert_any_call(
                    StringContains(MAR_HOST_IP_ADDRESS_2)
                )

                mock_print.assert_any_call(
                    StringDoesNotContain("Error")
                )

            dxl_client.disconnect()


    def test_basicpaging_example(self):
        # Modify sample file to include necessary sample data
        sample_filename = self.BASIC_FOLDER + "/basic_paging_example.py"
        temp_sample_file = TempSampleFile(sample_filename)

        target_line = "HOST_IP = "
        replacement_line = target_line + "\"" + MAR_HOST_IP_ADDRESS_1 + "\"\n"
        temp_sample_file.write_file_line(
            target_line,
            replacement_line
        )

        with self.create_client(max_retries=0) as dxl_client:
            dxl_client.connect()

            with MockMarServer(dxl_client):
                mock_print = BaseClientTest.run_sample(temp_sample_file.temp_file.name)

                mock_print.assert_any_call(
                    StringDoesNotContain("Error")
                )

                for process_id in MAR_PROCESS_IDS:
                    mock_print.assert_any_call(
                        StringContains(process_id)
                    )

            dxl_client.disconnect()
