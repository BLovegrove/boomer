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

def seek_bar(player: lavalink.DefaultPlayer, length: int = 20, fill: str = '█'):

    total = player.current.duration
    current = player.position

    filledLength = int(length * current // total)

    bar = fill * filledLength + '░' * (length - filledLength)

    return f"🎵 {milis_to_duration(current)} |{bar}| {milis_to_duration(total)} 🎵"


def progress_bar(current: int, total: int, length: int = 20, fill: str = '█') -> str:

    percent = f"{math.floor(100 * (current / float(total)))}"

    filledLength = int(length * current // total)

    bar = fill * filledLength + '░' * (length - filledLength)

    return f"{str(current).zfill(len(str(total)))}/{total} |{bar}| {percent.zfill(3)}%"
