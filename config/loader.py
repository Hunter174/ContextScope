import yaml

from config.paths import CONFIG_FILE


DEFAULT_CONFIG = {
    "version": 1,
    "setup_completed": False,
    "integrations": {}
}


def config_exists():

    return CONFIG_FILE.exists()


def load_config():

    if not config_exists():
        return DEFAULT_CONFIG.copy()

    with open(CONFIG_FILE, "r") as f:

        loaded = yaml.safe_load(f) or {}

    return (
        DEFAULT_CONFIG
        | loaded
    )


def save_config(config):

    with open(CONFIG_FILE, "w") as f:

        yaml.safe_dump(
            config,
            f,
            default_flow_style=False,
            sort_keys=False
        )


def is_setup_complete():

    config = load_config()

    return config.get(
        "setup_completed",
        False
    )