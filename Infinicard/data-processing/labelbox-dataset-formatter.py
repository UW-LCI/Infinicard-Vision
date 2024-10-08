import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
import json
from PIL import Image
import requests
import io

class LabelboxDataset(Dataset):
    def __init__(self, json_file, transform=None):
        with open(json_file, 'r') as f:
            self.data = json.load(f)
        self.transform = transform
        self.class_mapping = {
            'Container': 0,
            'Dropdown': 1,
            'Icon': 2,
            'Image': 3,
            'Text': 4,
            'Text Input': 5
        }

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        if 'data_row' not in item or 'row_data' not in item['data_row']:
            print(f"Missing 'row_data' in item: {item}")
            return None  # or handle it in a way that suits your needs
        image_url = item['data_row']['row_data']
        image = Image.open(io.BytesIO(requests.get(image_url).content))
        if self.transform:
            image = self.transform(image)
        annotations = self.data[idx]['projects']['clyhq3smz027j07ve39u06lwr']['labels'][0]['annotations']['objects']
        boxes = []
        labels = []
        for obj in annotations:
            if obj['name'] in self.class_mapping:
                bbox = obj['bounding_box']
                x_min = bbox['left']
                y_min = bbox['top']
                x_max = x_min + bbox['width']
                y_max = y_min + bbox['height']
                boxes.append([x_min, y_min, x_max, y_max])
                labels.append(self.class_mapping[obj['name']])
        return image, {'boxes': boxes, 'labels': labels}


# Define your transformation pipeline
transform = transforms.Compose([
    transforms.Grayscale(num_output_channels=3),  # Convert grayscale images to RGB
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# Create the dataset and dataloader
dataset = LabelboxDataset(json_file='export-output.json', transform=transform)
dataloader = DataLoader(dataset, batch_size=4, shuffle=True)

print(f"Number of samples in the dataset: {len(dataset)}")
print(f"Number of batches in the dataloader: {len(dataloader)}")
# Iterate through the dataloader
# for images, targets in dataloader:
#     print(f"Images shape: {images.shape}")
#     print(f"Targets: {targets}")
    # Your processing code here