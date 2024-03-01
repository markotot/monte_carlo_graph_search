#params="training.training_steps=10,100,1000,10000"
#python3 monte_carlo_graph_search/experiments/main.py --multirun $params
echo "LAUNCH playground"
echo $SEED
echo "LAUNCH playground"
python3 -m experiments.playground $SEED
