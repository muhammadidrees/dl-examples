import torch
import torch.nn as nn
from sklearn.model_selection import KFold

import sys
sys.path.append( './data/adult/' )
from adult_torch_model import *

def reset_weights(m):
  '''
    Try resetting model weights to avoid
    weight leakage.
  '''
  for layer in m.children():
   if hasattr(layer, 'reset_parameters'):
    print(f'Reset trainable parameters of layer = {layer}')
    layer.reset_parameters()

torch.manual_seed(69)

train_dataset = AdultDataset()
test_dataset = AdultDataset(train=False)

batch_size = 1000


class LogisticRegression(nn.Module):
    
    def __init__(self, n_input_features):
        super(LogisticRegression, self).__init__()
        self.linear = nn.Linear(n_input_features, 1)

    def forward(self, x):
        y_predicted = torch.sigmoid(self.linear(x))
        return y_predicted



k_folds = 1
kfold = KFold(n_splits=k_folds, shuffle=True)

accuracy = []
for n in range(1):
    for fold, (train_ids, test_ids) in enumerate(kfold.split(dataset)):
        # Print
        print(f'FOLD {fold}')
        print('--------------------------------')
        
        # Sample elements randomly from a given list of ids, no replacement.
        train_subsampler = torch.utils.data.SubsetRandomSampler(train_ids)
        test_subsampler = torch.utils.data.SubsetRandomSampler(test_ids)
        
        # Define data loaders for training and testing data in this fold
        train_loader = torch.utils.data.DataLoader(
                        dataset, 
                        batch_size=100, sampler=train_subsampler)
        test_loader = torch.utils.data.DataLoader(
                        dataset,
                        batch_size=100, sampler=test_subsampler)
        
        model = LogisticRegression(dataset.n_features)

        # loss and optimizer
        learning_rate = 0.0001
        criterian = nn.MSELoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

        # training loop
        num_epoch = 100
        for epoch in range(num_epoch):
            for i, (X_train, y_train) in enumerate(train_loader):
                # forward pass
                y_predicted = model(X_train)

                # loss function
                loss = criterian(y_predicted, y_train)

                # backpass
                loss.backward()

                # updates
                optimizer.step()

                # zero gradients
                optimizer.zero_grad()

            if (epoch + 1) % 25 == 0:
                print(f'epoch: {epoch + 1}, loss = {loss.item():.4f}')

        with torch.no_grad():
            fold_accuracy = []
            acc_sum = 0
            for i, (X_test, y_test) in enumerate(test_loader):
                y_predicted = model(X_test)
                y_predicted_cls = y_predicted.round()
                acc = y_predicted_cls.eq(y_test).sum() / float(y_test.shape[0])
                acc_sum += acc
            acc_sum = acc_sum / len(test_loader)
            fold_accuracy.append(acc_sum)
            print(f'Accuracy = {acc_sum:.4f}')
        print('--------------------------------')
    accuracy.append(fold_accuracy)

for a in accuracy:
    print(a)