# Some generic utility commands.

import math
import lavalink

def clamp(value, min_value, max_value) -> int:
    # returns a given number restricted between a min and max value
    
    return max(min_value, min(value, max_value))

def millis_to_duration(millis: int) -> str:
    # Converts milliseconds to an HH:MM:SS string format
    
    hours = math.trunc(millis / 3600000)
    if hours < 10:
        hours = f"0{hours}"
    else:
        hours = f"{hours}"
    millis = millis % 3600000

    minutes = math.trunc(millis / 60000)
    if minutes < 10:
        minutes = f"0{minutes}"
    else:
        minutes = f"{minutes}"
    millis = millis % 60000

    seconds = math.trunc(millis / 1000)
    if seconds < 10:
        seconds = f"0{seconds}"
    else:
        seconds = f"{seconds}"

    parts = [hours, minutes, seconds]

    time = ":".join(parts)
    return time

def seek_bar(player: lavalink.DefaultPlayer, length: int = 20, fill: str = '█'):

    total = player.current.duration
    current = player.position

    filledLength = int(length * current // total)

    bar = fill * filledLength + '░' * (length - filledLength)

    return f"🎵 {millis_to_duration(current)} |{bar}| {millis_to_duration(total)} 🎵"

def progress_bar(current: int, total: int, length: int = 20, fill: str = '█') -> str:

    percent = f"{math.floor(100 * (current / float(total)))}"

    filledLength = int(length * current // total)

    bar = fill * filledLength + '░' * (length - filledLength)

    return f"{str(current).zfill(len(str(total)))}/{total} |{bar}| {percent.zfill(3)}%"
