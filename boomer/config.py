import toml

file_default = "./_config.toml"

def load_config(path=file_default):
    # Loads the config from `path`
    
    cfg = toml.load(path)
    return cfg

    
