import torch
import argparse
import os
import numpy as np
import yaml
import random
import torchvision
from tqdm import tqdm
from torch.utils.data.dataloader import DataLoader
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.models.detection.anchor_utils import AnchorGenerator

device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

def collate_fn(batch):
    return tuple(zip(*batch))

def train(args):
    # To be implemented
    seed = 1111 # TODO: Set the seed
    torch.manual_seed(seed)
    np.random.seed(seed)
    random.seed(seed)
    if device == 'cuda':
        torch.cuda.manual_seed_all(seed)

    train_dataset = None # TODO: Load the dataset
    train_loader = DataLoader(train_dataset, batch_size=2, shuffle=True, num_workers=4, collate_fn=collate_fn)

    if args.use_resnet50_fpn:
        faster_rcnn = torchvision.models.detection.fasterrcnn_resnet50_fpn(pretrained=True) # Set Min and Max size for images
        faster_rcnn.roi_heads.box_predictor = FastRCNNPredictor(faster_rcnn_model.roi_heads.box_predictor.cls_score.in_features, num_classes=6)
    else:
        # TODO: Implement Faster RCNN custom model (e.g. ResNet34)
        print("To be implemented")
        exit()
        # backbone = torchvision.models.resnet34(pretrained=True, norm_layer=torchvision.ops.FrozenBatchNorm2d)
        # backbone = torch.nn.Sequential(*list(backbone.children())[:-3])
        # backbone.out_channels = 256
        # roi_align = torchvision.ops.MultiScaleRoIAlign(featmap_names=['0'], output_size=7, sampling_ratio=2)
        # rpn_anchor_generator = AnchorGenerator()
        # faster_rcnn_model = torchvision.models.detection.FasterRCNN(backbone,

    faster_rcnn_model.to(device)
    faster_rcnn_model.train()

    optimizer = torch.optim.SGD(lr=1E-4,
                                params=filter(lambda p: p.requires_grad, faster_rcnn_model.parameters()),
                                weight_decay=5E-5, momentum=0.9)

    num_epochs = 15 # TODO: Set the number of epochs
    step_count = 0

    for epoch in range(num_epochs):
        rpn_classification_losses, rpn_localization_losses = [], []
        frcnn_classification_losses, frcnn_localization_losses = [], []

        for images, targets, _ in tqdm(train_dataset):
            optimizer.zero_grad()

            for target in targets:
                target['boxes'] = target['bboxes'].float().to(device)
                del target['bboxes']
                target['labels'] = target['labels'].long().to(device)

            images = [img.float().to(device) for img in images]
            batch_losses = faster_rcnn_model(images, targets)

            # Aggregate loss
            loss = sum(batch_losses[loss_name] for loss_name in [
                'loss_classifier', 'loss_box_reg', 'loss_rpn_box_reg', 'loss_objectness'
            ])

            # Record losses
            rpn_classification_losses.append(batch_losses['loss_objectness'].item())
            rpn_localization_losses.append(batch_losses['loss_rpn_box_reg'].item())
            frcnn_classification_losses.append(batch_losses['loss_classifier'].item())
            frcnn_localization_losses.append(batch_losses['loss_box_reg'].item())

            # Backpropagation and optimization
            loss.backward()
            optimizer.step()

            break  # Remove this if you don't intend to break after the first iteration

        # Save model checkpoint
        model_name = 'tv_frcnn_r50fpn_' if args.use_resnet50_fpn else 'tv_frcnn_'
        torch.save(faster_rcnn_model.state_dict(), os.path.join(train_config['task_name'], model_name + train_config['ckpt_name']))

        # Print losses for the epoch
        print(f'Finished epoch {epoch}')
        print(
            f'RPN Classification Loss: {np.mean(rpn_classification_losses):.4f} | '
            f'RPN Localization Loss: {np.mean(rpn_localization_losses):.4f} | '
            f'FRCNN Classification Loss: {np.mean(frcnn_classification_losses):.4f} | '
            f'FRCNN Localization Loss: {np.mean(frcnn_localization_losses):.4f}'
        )

    print('Done Training...')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Arguments for faster rcnn using torchvision code training')
    parser.add_argument('--config', dest='config_path',
                        default='config/voc.yaml', type=str)
    parser.add_argument('--use_resnet50_fpn', dest='use_resnet50_fpn',
                        default=True, type=bool)
    args = parser.parse_args()
    train(args)