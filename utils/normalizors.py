import collections
import datetime
from typing import List, Dict, Any, Optional

def group_exercise_data_by_date(attempts: List[Dict[str, any]]) -> Dict[datetime.date, List[Dict[str, Any]]]:
    """
        Groups exercise attempts by date.
    """
    grouped_data: Dict[datetime.date, List[Dict[str, Any]]] = collections.defaultdict(list)
    
    for attempt in attempts:
        date = attempt["timestamp"]
        grouped_data[date.date()].append(attempt)
    
    return dict(grouped_data)

def normalize_values_min_max(values: List[float], invert: bool = False) -> List[Optional[float]]:
    """
        Normalizes a list of values to a range of 0 to 1 using min-max normalization.
        If invert is True, the normalization is inverted.
    """
    if not values:
        return []

    min_val, max_val = min(values), max(values)
    value_range = max_val - min_val

    normalized_values: List[Optional[float]] = []

    if value_range == 0:
        normalized_values = [0.5] * len(values)
    else:
        for value in values:
            normalized = (value - min_val) / value_range
            normalized_values.append(1 - normalized if invert else normalized)
    return normalized_values

def process_exercise_data(attempts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
        Preprocesses and normalizes exercise attempts data.
    """
    if not attempts:
        return {}

    grouped_data = group_exercise_data_by_date(attempts)
    sorted_dates = sorted(grouped_data.keys())

    avg_accuracies = []
    avg_reaction_times = []

    for day in sorted_dates:
        daily_attempts = grouped_data[day]

        accuracies = [attempt["accuracy"] for attempt in daily_attempts if "accuracy" in attempt]
        reaction_time = [attempt["avg_reaction_time"] for attempt in daily_attempts if "avg_reaction_time" in attempt]

        avg_accuracies.append(sum(accuracies) / len(accuracies) if accuracies else 0)
        avg_reaction_times.append(sum(reaction_time) / len(reaction_time) if reaction_time else 0)

    # Uncomment the following lines if you want to normalize the values, currently commented out due to time restraints (and this is not really that useful at the moment)
    # norm_accuracies = normalize_values_min_max(accuracies, invert=False)
    # norm_reaction_time = normalize_values_min_max(reaction_time, invert=True)

    result = {}
    for i, day in enumerate(sorted_dates):
        result[day] = [avg_accuracies[i], avg_reaction_times[i]]

    return result