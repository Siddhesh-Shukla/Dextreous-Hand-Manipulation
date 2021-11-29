"""ShadowHand Environment Wrappers."""
import os

from numpy.core.shape_base import block
import numpy as np
# from torch._C import TreeView
import gym
from gym import spaces
from ppo import PPO
from matplotlib import pyplot as plt

# Torch
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.distributions import Normal, MultivariateNormal

use_cuda = torch.cuda.is_available()
use_cuda = False
device = torch.device("cuda" if use_cuda else "cpu")


# Initialising the environment
env = gym.make("HandManipulateBlock-v0")
done, observation = False, env.reset()
rewards = []
done_cntr = 0
action = env.action_space.sample()
observation, reward, done, info = env.step(action)

num_inputs = np.array(np.shape(observation["observation"]))[0]   # 61
num_outputs = np.array(np.shape(action))[0]                      # 20


"""
Hyperparameters used for PPO by OpenAI's implementation
discount factor γ                   0.998
Generalized Advantage Estimation λ  0.95
entropy regularization coefficient  0.01
PPO clipping parameter              0.2
optimizer Adam [28]
learning rate                       3e-4
batch size (per GPU)                80k chunks x 10 transitions = 800k transitions
minibatch size (per GPU)            25.6k transitions
number of minibatches per step      60
network architecture                dense layer with ReLU + LSTM
size of dense hidden layer          1024
LSTM size                           512
"""

# HYPERPARAMETERS
# Model
lstm_nh = 64  # Hidden layer size in LSTM
dense_na = 128  # Size of dense hidden layer
action_dist_size = 20  # Action distribution size
value_output_size = 1  # Single output

hyperparameters = {
				'timesteps_per_batch': 200, 
				'max_timesteps_per_episode': 200, 
				'gamma': 0.99,                  
				'n_updates_per_iteration': 10,
				'lr': 3e-4, 
				'clip': 0.2,
				'render': True,
				'render_every_i': 10
			  }


#Actor and Critic models
class PPO_model(nn.Module):
    def __init__(self, nX, nY):
        super(PPO_model, self).__init__()
        self.stack = nn.Sequential(
            nn.Linear(nX, dense_na),
            nn.ReLU(),
            nn.LSTM(dense_na, lstm_nh, batch_first=True)
        )
        self.Lin = nn.Linear(lstm_nh, nY)

    def forward(self, obs):
        # obs = F.normalize(obs)
        obs, _ = self.stack(obs)
        out = self.Lin(obs)
        return out

model = PPO(policy_class=PPO_model, env=env, **hyperparameters)

model.learn(total_timesteps = 500000)

# model = Policy_Value_NN()
# print(model)
def plot(frame_idx, rewards):
    # clear_output(True)
    # plt.figure(figsize=(20,5))
    # plt.subplot(131)
    plt.title(f"Total frames = {len(frame_idx)}")
    plt.plot(rewards)
    plt.show()


def model_save(model):
    torch.save(model.state_dict, PATH)


def model_load(model):
    model.load_state_dict(torch.load(PATH))
    # model.eval()


def test_env(rndr=True):
    print("Running a test")
    state = env.reset()
    if rndr:
        env.render()
    done = False
    total_reward = 0
    while not done:
        state = torch.FloatTensor([state["observation"]]).unsqueeze(0).to(device)
        action = model.actor.forward(state)
        next_state, reward, done, _ = env.step(action.detach().cpu().numpy().ravel())
        state = next_state
        if rndr:
            env.render()
        total_reward += reward
    return total_reward

print(model.actor)
frames = [10000 * i for i in range(len(rewards))]
rewards = [i.cpu().detach().numpy().ravel() for i in rewards]
plot(frames, rewards)
[test_env() for _ in range(25)]

if save_model:
    model_save(model)