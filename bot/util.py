# Some generic utility commands.

def clamp(value, min_value, max_value) -> int:
    return max(min_value, min(value, max_value))
