import time
import os
import labelbox

# ==========================
# Configuration Parameters
# ==========================

# Replace with your actual Labelbox API key
LB_API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJjbHh1dGxiNnAwNW8yMDd6eDV1djRncnZqIiwib3JnYW5pemF0aW9uSWQiOiJjbHh1dGxiNmMwNW8xMDd6eDEybjM4eXYyIiwiYXBpS2V5SWQiOiJjbTFxMTJjYnYwNXBoMDcwZWZ3Y3UzZ2hqIiwic2VjcmV0IjoiMDAxMzA1YmJlYTY2NzNjMGFjNmYwM2UwNmIyMTEwOWIiLCJpYXQiOjE3Mjc3NjIzMDEsImV4cCI6MjM1ODkxNDMwMX0.iT2qzTR9W3zAaJjZUFMEr-aRj3u2aFbaqJKxzZpik_k'

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