import toml

def load_config(path="./config.toml"):
    # Loads the config from `path`
    config = toml.load(path)
    return config
