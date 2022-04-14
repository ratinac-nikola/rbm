import torch
import torch.nn.functional as F
from utils import *


class RBM:
    def __init__(
        self,
        n_visible: int,
        n_hidden: int,
        device: str = "cpu",
        learning_rate: float = 0.1,
    ) -> None:
        """
        Construct the RBM model with given number of visible and hidden units

        :arg visible_units: number of visible units
        :arg hidden_units: number of hidden units
        :arg device: the device to instantiate the tensor on
        :arg learning_rate: rate at which to modify weights and biases
        """
        self.n_visible = n_visible
        self.n_hidden = n_hidden

        self.device = device
        self.learning_rate = learning_rate

        self.w = torch.randn(n_hidden, n_visible, 5, device=self.device)

        self.v_bias = torch.randn(n_visible, 5, device=self.device)
        self.h_bias = torch.randn(n_hidden, device=self.device)

    def sample_h(self, v: torch.Tensor) -> torch.Tensor:
        """
        Sample hidden units given that v is the visible layer
        :param v: visible layer
        """

        a = torch.sum(torch.matmul(self.w, v.t()), dim=[1, 2])

        activation = self.h_bias + a

        phv = torch.sigmoid(activation)

        return phv, torch.bernoulli(phv)

    def sample_v(self, h: torch.Tensor) -> torch.Tensor:
        """
        Sample visible units given that h is the hidden layer
        :param h: hidden layer
        """

        hw = torch.matmul(self.w.permute(1, 2, 0), h.t())

        pvh = hw + self.v_bias.expand_as(hw)

        pvh = pvh.softmax(dim=1)

        return pvh, softmax_to_onehot(pvh)

    def train(
        self, v0: torch.Tensor, vk: torch.Tensor, ph0: torch.Tensor, phk: torch.Tensor
    ) -> None:
        """
        Perform contrastive divergence algorithm to optimize the weights that minimize the energy
        This maximizes the log-likelihood of the model
        """

        # caluclate the deltas
        hb_delta = ph0 - phk
        vb_delta = v0 - vk

        w_delta = hb_delta.view([self.n_hidden, 1, 1]) * vb_delta.view(
            [1, self.n_visible, 5]
        )
        # print(w_delta)
        # update the parameters of the model
        self.v_bias += vb_delta * self.learning_rate
        self.h_bias += hb_delta * self.learning_rate
        self.w += w_delta * self.learning_rate

    def reconstruct(self, v: torch.Tensor) -> torch.Tensor:
        """
        For a given v input tensor, let the RBM reconstruct it
        by performing a forward and backward pass
        :arg v: the input tensor
        """

        return self.sample_v(self.sample_h(v)[1])[1]


if __name__ == "__main__":
    rbm = RBM(100, 20)
    rbm.reconstruct(None)
