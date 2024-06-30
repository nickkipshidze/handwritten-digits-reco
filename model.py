import torch, os
from torch import nn

class TinyVGG(nn.Module):
    def __init__(self, in_shape, hidden_units, out_shape):
        super().__init__()
        self.conv_block_1 = nn.Sequential(
            nn.Conv2d(in_channels=in_shape, out_channels=hidden_units, kernel_size=2, padding=1),
            nn.ReLU(),
            nn.Conv2d(in_channels=hidden_units, out_channels=hidden_units, kernel_size=2, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=3)
        )
        self.conv_block_2 = nn.Sequential(
            nn.Conv2d(in_channels=hidden_units, out_channels=hidden_units, kernel_size=2, padding=1),
            nn.ReLU(),
            nn.Conv2d(in_channels=hidden_units, out_channels=hidden_units, kernel_size=2, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=3)
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(in_features=hidden_units*4*4, out_features=out_shape),
            nn.Sigmoid()
        )

    def forward(self, X):
        return self.classifier(
            self.conv_block_2(
                self.conv_block_1(X)
            )
        )

class Model:
    def __init__(self, path):
        if os.path.exists(path):
            self.model = torch.load(path)
        else:
            raise FileNotFoundError("Path to model does not exist")
        self.class_names = ["0 - zero", "1 - one", "2 - two", "3 - three", "4 - four", "5 - five", "6 - six", "7 - seven", "8 - eight", "9 - nine"]
    
    def predict(self, X):
        X = torch.Tensor(X).reshape(28, 28).unsqueeze(0).unsqueeze(0) / 255
        X = X.flip(2)
        y_logits = self.model.forward(X)
        y_pred = y_logits.argmax(dim=1)
        y_label = self.class_names[y_pred.item()]
        y_accuracy = y_logits[0][y_pred].item() * 100
        return y_label, y_accuracy