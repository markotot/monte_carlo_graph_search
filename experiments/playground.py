import time

from monte_carlo_graph_search.environment.griddly.clusters_env import ClustersEnv

if __name__ == "__main__":

    times = []
    env = ClustersEnv(env_config=None)
    env.env.unwrapped.level = 0
    for _ in range(1000):
        start_time = time.perf_counter()
        env2 = env.clone()
        end_time = time.perf_counter()
        times.append(end_time - start_time)

    print(times)
    # env.reset()

    # actions = [3, 4, 1, 2, 2, 3, 4, 4, 1, 4, 4, 1, 1, 3, 2, 2, 2, 1, 1, 4, 4, 2, 1, 4, 4, 3, 3, 3, 2, 3, 4]
    #
    # for action in actions:
    #     next_obs, reward, done, info = env.step(action)
    #     # print(env.get_observation())
    #     # env.render()
