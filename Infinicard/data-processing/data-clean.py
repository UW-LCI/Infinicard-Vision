import time
import os
import labelbox
from dotenv import load_dotenv

# Make sure to set environment variables for the Labelbox API key
# LABELBOX_API_KEY=your-api-key
load_dotenv()

LB_API_KEY = os.environ.get('LABELBOX_API_KEY')

# Replace with your actual Labelbox Project ID
PROJECT_ID = 'clyhq3smz027j07ve39u06lwr'

# Replace with your desired export task name
EXPORT_TASK_NAME = 'Export v2 (streamable): catalog query'

# Path to save the exported JSON file
EXPORT_OUTPUT_PATH = 'export-output.json'
client = labelbox.Client(api_key = LB_API_KEY)
export_task = labelbox.ExportTask.get_task(client, "cm1q1gzhk00k6071l4qwjdd2o")

# Download the file to a local path
converter = labelbox.FileConverter(file_path="export-output.json")
export_task.get_stream(converter=converter).start()

# Stream the file to stdout
def json_stream_handler(output: labelbox.JsonConverterOutput):
  print(output.json_str)
export_task.get_stream().start(stream_handler=json_stream_handler)