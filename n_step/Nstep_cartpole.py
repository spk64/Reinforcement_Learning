#!/usr/bin/env python
# coding: utf-8

# In[10]:


# !pip install gym
import gym
import numpy as np
import matplotlib.pyplot as plt
from itertools import product
from math import pi

def normalize_state(state):
    x, v ,omega, omega_dot=state       
    x_normalized = (x + x_max) / (2 * x_max)  
    v_normalized = (v + v_max) / (2 * v_max) 
    omega_normalized = (omega + omega_max) / (2 * omega_max)  
    omega_dot_normalized = (omega_dot + omega_dot_max) / (2 * omega_dot_max)
    return x_normalized, v_normalized, omega_normalized, omega_dot_normalized

def episilon_greedy_action(action_value, eps):
    if(np.random.random() < eps):
      action = np.random.randint(len(action_value))
    else:
      action = np.argmax(action_value)   
    return action

def compute_fourier_basis(order, num_state_vars):
    combinations = list(product(*(range(order + 1) for _ in range(num_state_vars))))
    return np.array(combinations)

def compute_action_value(weights, features, normalized_state): 
    phi=compute_phi(features, normalized_state)
    action_value = np.dot(weights, phi) 
    return action_value[(0,0)]

def compute_phi(features, normalized_state): 
    phi = np.cos(pi * np.dot(features, np.array(list(normalized_state)).reshape(len(normalized_state), 1))) 
    return phi
    
def run_episode(weights, features, alpha, eps, n_steps): 
    T = 500
    t = 0
    
    done = False  
    env = gym.make('CartPole-v1')
    state = env.reset()[0]
    normalized_state = normalize_state(state)
    
    vals = []
    for i in range(len(actions)):
        vals.append(compute_action_value(weights[i], features, normalized_state))
    action_state_value=vals
    action = episilon_greedy_action(action_state_value, eps)

    states_memory = [state]
    action_memory = [action]
    reward_memory = []

    while True:
        state = states_memory[-1]
        normalized_state = normalize_state(state)
        action = action_memory[-1]

        next_state, reward, done, _, _ = env.step(action)
        states_memory.append(next_state)
        reward_memory.append(reward)
        
        if done or t==T: 
            return weights, t , t

        if not done:
            vals = []
            for i in range(len(actions)):
                vals.append(compute_action_value(weights[i], features, normalized_state))
            action_state_value=vals
            action = episilon_greedy_action(action_state_value, eps)
            action_memory.append(action)
        else:
            T = t + 1

        tau = t - n_steps + 1
        if tau >= 0:
            G = sum([ pow(discount_parameter, i - tau - 1) * reward_memory[i] for i in range(tau+1, min(tau + n_steps, T))])
            if tau + n_steps < T: 
                G += pow(discount_parameter, n_steps) * compute_action_value(weights[action_memory[tau + n_steps]], features, normalize_state(states_memory[tau + n_steps]))
            
            for i in range(len(actions)):
                weights[i] += float(alpha) * (G - compute_action_value(weights[action_memory[tau]], features, normalize_state(states_memory[tau]))) * np.transpose(compute_phi(features ,normalize_state(states_memory[tau])))

        t += 1
        
def plot_episodes_action(overall_steps,numEpisodes,a, flag=False):
    plt.title('Learning curve')
    for i in range(len(a)):
        label = f'n_step={a[i]}' if flag else f'alpha={a[i]}'
        plt.plot(overall_steps[i],[i for i in range(1, numEpisodes + 1)],label = label)
        #plt.fill_between([i for i in range(1, numEpisodes + 1)],overall_rewards[i] - std_deviations[i], overall_rewards[i] + std_deviations[i],alphas = )
        #plt.errorbar([i for i in range(1, numEpisodes + 1)], overall_reward, yerr=std_deviation, linestyle='None', color='blue',label='Std Dev')
        #plt.errorbar([i for i in range(1, numEpisodes + 1)], overall_result, yerr=std_overall_result, linestyle='None', color='brown',label='Std Dev')
    plt.legend()
    plt.xlabel('Steps')
    plt.ylabel('Episodes')
    plt.show()
    
def plot_rewards(overall_rewards, std_deviations, numEpisodes, a, flag=False):
    plt.title('Performance Cartpole')
    for i in range(len(a)):
        label = f'n_step={a[i]}' if flag else f'alpha={a[i]}'
        plt.plot([i for i in range(1, numEpisodes + 1)], overall_rewards[i], label=label)

    plt.legend()
    plt.xlabel('Episodes')
    plt.ylabel('Reward')
    plt.show()

actions = [0, 1]
state_variables = ['x', 'v', 'omega', 'omega_dot']
x_max = 4.8
v_max = 4  
omega_max = 0.418
omega_dot_max = 2.5   
num_state_variables = len(state_variables)
discount_parameter = 1

def varying_alphas():

    numTimes = 3
    numEpisodes = 800
    alphas = [.001,.01,.1,1]
    epsilon = 0.9
    n_steps = 8
    order = 2
    decay_epsilon_param = 0.1
    overall_result =[]
    tot_steps = []
    rewards = np.zeros((numTimes,numEpisodes))

    avg_alpha_rew = []
    avg_alpha_std_rewards = []
    avg_alpha_act = []
    for alpha in alphas:
        overall_rewards = []
        overall_actions = []
        for i in range(numTimes):
            reward_tot = []
            tot_actions = 0
            cum_actions = []
            
            decay_epsilon = epsilon
            total = int(pow(order+1, len(state_variables)))
            weights = [np.array([0.0] * total).reshape(1, total) for i in actions]
            combinations = compute_fourier_basis(order,num_state_variables)
            for i in range(numEpisodes):
                if (i+1) % 50 == 0 and decay_epsilon > 0:
                    decay_epsilon -= decay_epsilon_param
                    decay_epsilon = max(0, decay_epsilon)
        
                weights, timesteps ,totReward  = run_episode(weights, combinations, alpha, decay_epsilon, n_steps)
                tot_actions += timesteps
                cum_actions.append(tot_actions)
                reward_tot.append(totReward)
        
            overall_actions.append(cum_actions)
            overall_rewards.append(reward_tot)

        avg_rewards = np.mean(overall_rewards, axis=0)
        std_rewards = np.std(overall_rewards, axis=0)
        avg_actions = np.mean(overall_actions, axis=0)
        avg_alpha_rew.append(avg_rewards)
        avg_alpha_std_rewards.append(std_rewards)
        avg_alpha_act.append(avg_actions)
    plot_episodes_action(avg_alpha_act,numEpisodes,alphas, False)
    plot_rewards(avg_alpha_rew,avg_alpha_std_rewards,numEpisodes,alphas, False)

#varying_alphas()
def varying_nstep():

    numTimes = 3
    numEpisodes = 800
    alpha = 0.001
    epsilon = 0.9
    n_step_list = [1,2, 4,8]
    order = 2
    decay_epsilon_param = 0.1
    overall_result =[]
    tot_steps = []
    rewards = np.zeros((numTimes,numEpisodes))

    avg_alpha_rew = []
    avg_alpha_std_rewards = []
    avg_alpha_act = []
    for n_steps in n_step_list:
        overall_rewards = []
        overall_actions = []
        for i in range(numTimes):
            reward_tot = []
            tot_actions = 0
            cum_actions = []
            
            decay_epsilon = epsilon
            total = int(pow(order+1, len(state_variables)))
            weights = [np.array([0.0] * total).reshape(1, total) for i in actions]
            combinations = compute_fourier_basis(order,num_state_variables)
            for i in range(numEpisodes):
                if (i+1) % 50 == 0 and decay_epsilon > 0:
                    decay_epsilon -= decay_epsilon_param
                    decay_epsilon = max(0, decay_epsilon)
        
                weights, timesteps ,totReward  = run_episode(weights, combinations, alpha, decay_epsilon, n_steps)
                tot_actions += timesteps
                cum_actions.append(tot_actions)
                reward_tot.append(totReward)
        
            overall_actions.append(cum_actions)
            overall_rewards.append(reward_tot)

        avg_rewards = np.mean(overall_rewards, axis=0)
        std_rewards = np.std(overall_rewards, axis=0)
        avg_actions = np.mean(overall_actions, axis=0)
        avg_alpha_rew.append(avg_rewards)
        avg_alpha_std_rewards.append(std_rewards)
        avg_alpha_act.append(avg_actions)
    plot_episodes_action(avg_alpha_act,numEpisodes,n_step_list, True)
    plot_rewards(avg_alpha_rew,avg_alpha_std_rewards,numEpisodes,n_step_list, True)

varying_nstep()


# In[ ]:




