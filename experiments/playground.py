from monte_carlo_graph_search.environment.griddly.clusters_env import GriddlyEnv

if __name__ == "__main__":

    env = GriddlyEnv(env_config=None)
    env.reset()

    actions = [3, 4, 1, 2, 2, 3, 4, 4, 1, 4, 4, 1, 1, 3, 2, 2, 2, 1, 1, 4, 4, 2, 1, 4, 4, 3, 3, 3, 2, 3, 4]

    for action in actions:
        next_obs, reward, done, info = env.step(action)
        print(env.get_observation())
        env.render()
        print("m")
