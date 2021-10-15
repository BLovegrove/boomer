# Some generic utility commands.

def clamp(value, min_value, max_value) -> int:
    return max(min_value, min(value, max_value))


def truncate_string(value, max_length=255, suffix='...'):
    string_value = str(value)
    string_truncated = string_value[:min(len(string_value), (max_length - len(suffix)))]
    suffix = (suffix if len(string_value) > max_length else '')
    return string_truncated + suffix
