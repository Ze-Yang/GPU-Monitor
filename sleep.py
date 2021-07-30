import argparse
import time
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import models
import torch.utils.data as data

parser = argparse.ArgumentParser(description='PyTorch Example')
parser.add_argument('--batch-size', '-b', type=int, default=64, metavar='N',
                    help='input batch size for training (default: 64)')


class PseudoDataset(data.Dataset):
    def __init__(self):
        pass

    def __getitem__(self, item):
        return torch.rand(3, 224, 224), np.random.randint(1000)

    def __len__(self):
        return 50000


def train(train_loader, model, criterion, optimizer):
    model.train()
    for i, (images, target) in enumerate(train_loader):
        images, target = images.cuda(), target.cuda()
        output = model(images)
        loss = criterion(output, target)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        # time.sleep(0.1)


def main():
    args = parser.parse_args()

    model = models.__dict__['resnet50']().cuda()
    model = nn.DataParallel(model)
    optimizer = optim.SGD(model.parameters(), lr=0.01)
    criterion = nn.CrossEntropyLoss().cuda()

    dataset = PseudoDataset()
    train_loader = torch.utils.data.DataLoader(dataset, batch_size=args.batch_size)

    while True:
        train(train_loader, model, criterion, optimizer)


if __name__ == '__main__':
    main()
