#params="training.training_steps=10,100,1000,10000"
#python3 monte_carlo_graph_search/experiments/main.py --multirun $params

python3 -m experiments.main run_name=$RUN_NAME env.seed=$SEED search.seed=$SEED
