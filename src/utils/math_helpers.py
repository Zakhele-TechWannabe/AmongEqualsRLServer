from typing import Dict, Any
import random


def normalize_probabilities(probabilities: Dict[Any, float]) -> Dict[Any, float]:
    """Normalize a dictionary of probabilities to sum to 1.0"""
    total = sum(probabilities.values())
    
    if total == 0:
        # If all probabilities are 0, return uniform distribution
        uniform_prob = 1.0 / len(probabilities)
        return {key: uniform_prob for key in probabilities.keys()}
    
    return {key: prob / total for key, prob in probabilities.items()}


def weighted_random_choice(probabilities: Dict[Any, float]) -> Any:
    """Choose randomly from a dictionary of weighted probabilities"""
    # Normalize probabilities first
    normalized_probs = normalize_probabilities(probabilities)
    
    # Use random.choices for weighted selection
    choices = list(normalized_probs.keys())
    weights = list(normalized_probs.values())
    
    return random.choices(choices, weights=weights)[0]


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp a value between min and max"""
    return max(min_val, min(max_val, value))


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation between a and b by factor t"""
    return a + (b - a) * clamp(t, 0.0, 1.0)
