# Some generic utility commands.

import math
from re import L

import lavalink


def clamp(value, min_value, max_value) -> int:
    return max(min_value, min(value, max_value))

def duration_to_milis(duration: str) -> int:
    parts = duration.split(":")

    hours = int(parts[0]) * 3600000
    minutes = int(parts[1]) * 60000
    seconds = int(parts[2]) * 1000

    time = hours + minutes + seconds
    return time

def milis_to_duration(milis: int) -> str:
    hours = math.trunc(milis / 3600000)
    if hours < 10:
        hours = f"0{hours}"
    else:
        hours = f"{hours}"
    milis = milis % 3600000

    minutes = math.trunc(milis / 60000)
    if minutes < 10:
        minutes = f"0{minutes}"
    else:
        minutes = f"{minutes}"
    milis = milis % 60000

    seconds = math.trunc(milis / 1000)
    if seconds < 10:
        seconds = f"0{seconds}"
    else:
        seconds = f"{seconds}"

    parts = [hours, minutes, seconds]

    time = ":".join(parts)
    return time

def seek_bar(player: lavalink.DefaultPlayer):
    time_total_milis = player.current.duration

    time_current_milis = player.position
    time_current_str = milis_to_duration(time_current_milis)

    seek_start = f"{time_current_str} ["
    seek_bar = "======================================"
    seek_end = f"] -{milis_to_duration(time_total_milis - time_current_milis)}"

    seek_pos = math.floor((time_current_milis / time_total_milis) * 40)
    if seek_pos > 40:
        seek_pos = 0

    seek_bar = list(seek_bar)
    seek_bar[seek_pos] = "🎵"
    seek_bar = "".join(seek_bar)

    return seek_start + seek_bar + seek_end
    

def progress_bar(current: int, total: int, length: int = 20, fill: str = '█') -> str:

    percent = f"{math.floor(100 * (current / float(total)))}"

    filledLength = int(length * current // total)

    bar = fill * filledLength + '░' * (length - filledLength)

    return f"{str(current).zfill(len(str(total)))}/{total} |{bar}| {percent.zfill(3)}%"
