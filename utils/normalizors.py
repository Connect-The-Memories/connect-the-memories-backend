import collections
import datetime
from typing import List, Dict, Any, Optional

def group_exercise_data_by_date(attempts: List[Dict[str, any]]) -> Dict[datetime.date, List[Dict[str, Any]]]:
    """
        Groups exercise attempts by date.
    """
    grouped_data = collections.defaultdict(list)
    
    for attempt in attempts:
        date = attempt["timestamp"].date()
        grouped_data[date].append(attempt)
    
    return dict(grouped_data)

def normalize_values_min_max(values: List[float], invert: bool = False) -> List[Optional[float]]:
    """
        Normalizes a list of values to a range of 0 to 1 using min-max normalization.
        If invert is True, the normalization is inverted.
    """
    if not values:
        return []

    min_val = min(values)
    max_val = max(values)
    value_range = max_val - min_val

    normalized_values: List[Optional[float]] = []

    if value_range == 0:
        normalized_values = [0.5] * len(values)
    else:
        for value in values:
            if invert:
                normalized_value = (max_val - value) / value_range
            else:
                normalized_value = (value - min_val) / value_range
            normalized_values.append(normalized_value)

    return normalized_values

def preprocess_and_normalize(attempts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
        Preprocesses and normalizes exercise attempts data.
    """
    if not attempts:
        return {}

    grouped_data = group_exercise_data_by_date(attempts)
    processed_attempts = []

    sorted_dates = sorted(grouped_data.keys())

    for day in sorted_dates:
        daily_attempts = grouped_data[day]

        accuracies = [attempt["accuracy"] for attempt in daily_attempts if "accuracy" in attempts]
        reaction_time = [attempt["avg_reaction_time"] for attempt in daily_attempts if "avg_reaction_time" in attempts]

        norm_accuracies = normalize_values_min_max(accuracies, invert=False)
        norm_reaction_time = normalize_values_min_max(reaction_time, invert=True)

        acc_idx = 0
        rt_idx = 0
        for attempt in daily_attempts:
            if "accuracy" in attempt and acc_idx < len(norm_accuracies):
                attempt["normalized_accuracy_daily"] = norm_accuracies[acc_idx]
                acc_idx += 1
            else:
                attempt["normalized_accuracy_daily"] = None

            if "avg_reaction_time" in attempt and rt_idx < len(norm_reaction_time):
                attempt["normalized_rt_daily"] = norm_reaction_time[rt_idx]
                rt_idx += 1
            else:
                attempt["normalized_rt_daily"] = None

            processed_attempts.append(attempt)

    return processed_attempts