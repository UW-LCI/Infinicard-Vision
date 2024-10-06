import time
import os
import uuid
import labelbox
from labelbox import Client, FileConverter, types as lb_types, LabelImport
import json
from dotenv import load_dotenv
# from fix_busted_json import repair_json

# Code from Labelbox Documentation

# ==========================
# Configuration Parameters
# ==========================

load_dotenv()

# ASK Lucas to give you the API key access
LB_API_KEY = os.environ.get('LABELBOX_API_KEY')

PROJECT_ID = 'clyhq3smz027j07ve39u06lwr'

# Your existing Export Task ID
EXPORT_TASK_ID = 'cm1q1gzhk00k6071l4qwjdd2o'

# Path to save the exported JSON file
EXPORT_OUTPUT_PATH = 'export-output.json'

# ==========================
# Initialize Labelbox Client
# ==========================

client = Client(api_key=LB_API_KEY)
project = client.get_project(PROJECT_ID)

# ==========================
# Step 1: Retrieve and Monitor Export Task
# ==========================

def wait_for_export(client, export_task_id, timeout=600, interval=10):
    """
    Waits for the export task to complete.

    Args:
        client: Labelbox client instance.
        export_task_id: The Export Task ID to monitor.
        timeout: Maximum time to wait in seconds.
        interval: Time between status checks in seconds.

    Returns:
        Completed export task object.

    Raises:
        TimeoutError: If the task doesn't complete within the timeout period.
    """
    export_task = labelbox.ExportTask.get_task(client, "cm1q1gzhk00k6071l4qwjdd2o")
    start_time = time.time()
    return export_task

# ==========================
# Step 2: Download the Exported Data
# ==========================

def download_exported_data(client, export_task_id, file_path):
    """
    Downloads the exported data to the specified local file path.

    Args:
        client: Labelbox client instance.
        export_task_id: The Export Task ID to download.
        file_path: The local file path to save the exported data.
    """
    export_task = labelbox.ExportTask.get_task(client, "cm1q1gzhk00k6071l4qwjdd2o")

    # Initialize the FileConverter with the desired local file path
    converter = FileConverter(file_path=file_path)

    # Start the download stream
    print(f"Starting download of export data to '{file_path}'...")
    export_task.get_stream(converter=converter).start()
    print(f"Export data successfully downloaded to '{file_path}'.")

# ==========================
# Step 3: Load Exported Data
# ==========================

def load_exported_data(file_path):
    """
    Loads exported data from the JSONL file.

    Args:
        file_path: Path to the exported JSONL file.

    Returns:
        List of data rows.
    """
    data_rows = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line)
            data_rows.append(data)
    print(f"Loaded {len(data_rows)} data rows from '{file_path}'.")
    return data_rows

# ==========================
# Step 4: Define Annotations
# ==========================

def create_annotations():
    """
    Creates a list of annotations as per your initial setup.

    Returns:
        List of Labelbox annotation objects.
    """
    annotations = [
        lb_types.ObjectAnnotation(
            name="Text",
            value=lb_types.Rectangle(
                start=lb_types.Point(x=0, y=0),
                end=lb_types.Point(x=30, y=30)
            )
        ),
        lb_types.ObjectAnnotation(
            name="Image",
            value=lb_types.Rectangle(
                start=lb_types.Point(x=0, y=0),
                end=lb_types.Point(x=30, y=30)
            )
        ),
        lb_types.ObjectAnnotation(
            name="Icon",
            value=lb_types.Rectangle(
                start=lb_types.Point(x=0, y=0),
                end=lb_types.Point(x=30, y=30)
            )
        ),
        lb_types.ObjectAnnotation(
            name="Container",
            value=lb_types.Rectangle(
                start=lb_types.Point(x=0, y=0),
                end=lb_types.Point(x=30, y=30)
            )
        ),
        lb_types.ObjectAnnotation(
            name="Text Input",
            value=lb_types.Rectangle(
                start=lb_types.Point(x=0, y=0),
                end=lb_types.Point(x=30, y=30)
            )
        ),
        lb_types.ObjectAnnotation(
            name="Dropdown",
            value=lb_types.Rectangle(
                start=lb_types.Point(x=0, y=0),
                end=lb_types.Point(x=30, y=30)
            )
        ),
        lb_types.ObjectAnnotation(
            name="List",
            value=lb_types.Rectangle(
                start=lb_types.Point(x=0, y=0),
                end=lb_types.Point(x=30, y=30)
            )
        ),
        lb_types.ObjectAnnotation(
            name="Slider",
            value=lb_types.Rectangle(
                start=lb_types.Point(x=0, y=0),
                end=lb_types.Point(x=30, y=30)
            )
        )
    ]
    return annotations

# ==========================
# Step 5: Create Labels with Annotations
# ==========================

def create_labels(project, data_rows, annotations):
    """
    Creates labels for each data row with the specified annotations.

    Args:
        project: Labelbox project instance.
        data_rows: List of data rows from the exported data.
        annotations: List of annotation objects to apply.
    """
    labels_to_create = []
    for row in data_rows:
        external_id = row.get("data_row").get('external_id')
        id = row.get("data_row").get("id")
        if not external_id:
            print(f"Data row with UID {row.get('id')} does not have an external_id. Skipping.")
            continue

        label = lb_types.Label(
            data={
                "global_key": external_id # this is still mot allowed
            },
            annotations=annotations
        )
        labels_to_create.append(label)

    print(f"Creating {len(labels_to_create)} labels...")
    if labels_to_create:
        # Labelbox SDK's upload_labels method
        try:
            label_import = LabelImport.create_from_objects(
                            client = client,
                            project_id = PROJECT_ID,
                            name = "label_import_job"+str(uuid.uuid4()),
                            labels = labels_to_create)
            label_import.wait_till_done()
            print("Labels successfully uploaded.")
        except Exception as e:
            print(f"An error occurred while uploading labels: {e}")
    else:
        print("No labels to upload.")

# ==========================
# Main Workflow Execution
# ==========================

def main():
    try:
        # Step 1: Wait for Export Task to Complete
        completed_export_task = wait_for_export(client, EXPORT_TASK_ID)
        print(f"Export Task '{EXPORT_TASK_ID}' completed successfully.")

        # Step 2: Download Exported Data
        download_exported_data(client, EXPORT_TASK_ID, EXPORT_OUTPUT_PATH)
        print(f"Exported data downloaded to '{EXPORT_OUTPUT_PATH}'.")

        # Step 3: Load Exported Data
        data_rows = load_exported_data(EXPORT_OUTPUT_PATH)

        # Step 4: Define Annotations
        # annotations = create_annotations()
        # print(f"Created {len(annotations)} annotations.")

        # create_labels(project, data_rows, annotations)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
