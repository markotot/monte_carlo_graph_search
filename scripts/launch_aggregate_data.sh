#params="training.training_steps=10,100,1000,10000"
#python3 monte_carlo_graph_search/experiments/main.py --multirun $params

python3 -m experiments.aggregate_data run_name=$RUN_NAME start_run_id=$START_ID end_run_id=$END_ID
