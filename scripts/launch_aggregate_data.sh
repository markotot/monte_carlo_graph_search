#params="training.training_steps=10,100,1000,10000"
#python3 monte_carlo_graph_search/experiments/main.py --multirun $params

python3 -m experiments.aggregate_data start_run_id=$1 end_run_id=$2
