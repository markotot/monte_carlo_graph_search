#params="training.training_steps=10,100,1000,10000"
#python3 monte_carlo_graph_search/experiments/main.py --multirun $params
# $1 = SEED
python3 -m experiments.main env.seed=$1 search.seed=$1
