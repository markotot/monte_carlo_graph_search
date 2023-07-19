import numpy as np


def update_metrics(aggregated_metrics, new_metrics):
    for key, value in new_metrics.items():
        if key in aggregated_metrics.keys():
            aggregated_metrics[key].append(new_metrics[key])
        else:
            aggregated_metrics[key] = [value]
    return aggregated_metrics


def dict_sum(dictionary):
    mean_dict = {}
    for key, value in dictionary.items():
        mean_dict[key] = np.sum(value)
    return mean_dict


def add_time_percentages(dictionary, total_time_value):
    metrics = {}
    for key, value in dictionary.items():
        if "time" in key:
            key_name = f"{key}_percentage"
            metrics[key_name] = value / total_time_value * 100
    dictionary.update(metrics)
    return dictionary
