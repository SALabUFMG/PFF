# Library imports
from torch import nn


class SoccerRepCAE(nn.Module):

    def __init__(self, n_channels, width, height, latent_dim):

        super(SoccerRepCAE, self).__init__()

        self.n_channels = n_channels
        self.width = width
        self.height = height
        self.latent_dim = latent_dim

        # Encoder layers
        self.conv1 = nn.Sequential(
            nn.ZeroPad2d(1),
            nn.Conv2d(1, 8, kernel_size=(3, 3), stride=1, padding='valid', dtype=float),
            nn.ReLU(),
            nn.MaxPool2d(2, 2)
        )
        self.fusion1 = nn.Sequential(
            nn.Conv2d(8, 1, kernel_size=(1, 1), stride=1, dtype=float),
            nn.ReLU()
        )
        self.conv2 = nn.Sequential(
            nn.ZeroPad2d(1),
            nn.Conv2d(8, 8, kernel_size=(3, 3), stride=1, padding='valid', dtype=float),
            nn.ReLU(),
            nn.MaxPool2d(2, 2)
        )
        self.fusion2 = nn.Sequential(
            nn.Conv2d(8, 1, kernel_size=(1, 1), stride=1, dtype=float),
            nn.ReLU()
        )
        self.fc_mu = nn.Linear(int(self.width/2) * int(self.height/2) + int(self.width/4) * int(self.height/4), self.latent_dim, dtype=float)
        self.fc_logvar = nn.Linear(int(self.width/2) * int(self.height/2) + int(self.width/4) * int(self.height/4), self.latent_dim, dtype=float)

        # Decoder layers
        self.fc_d = nn.Linear(self.latent_dim, 8 * self.width * self.height, dtype=float)
        self.deconv1 = nn.Sequential(
            nn.ConvTranspose2d(8, n_channels, kernel_size=3, stride=1, padding=(1, 1), dtype=float),
            nn.Sigmoid(),
        )

        self.initialize_weights()

    def encode(self, x):
        # Apply encoder layers
        x = self.conv1(x)
        x = x.view(x.size(0), -1)
        z = self.fc_e(x)

        return z

    def decode(self, z):
        # Apply decoder layers
        z = self.fc_d(z)
        z = z.view(z.size(0), 8, self.height, self.width)
        z = self.deconv1(z)
        return z

    # Function for randomly initializing weights.
    def initialize_weights(self):

        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.Linear):
                nn.init.normal_(m.weight, 0, 0.01)
                nn.init.constant_(m.bias, 0)

    def forward(self, x):
        # Encode input
        z = self.encode(x)

        # Decode latent code
        recon_x = self.decode(z)

        return recon_x, z