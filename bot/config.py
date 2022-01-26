import toml

file_default = "./"


def load_config(path=file_default + "config.toml"):
    # Loads the config from `path`
    
    cfg = toml.load(path)
    return cfg

def load_queues(path=file_default + "saved_queues.toml"):
    # Loads the saved queue details from `path`

    queue_list = toml.load(path)
    return queue_list