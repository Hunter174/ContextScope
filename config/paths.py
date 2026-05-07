from pathlib import Path

from platformdirs import user_data_dir


APP_NAME = "ContextScope"
APP_AUTHOR = "HunterPaxton"


DATA_DIR = Path(
    user_data_dir(
        APP_NAME,
        APP_AUTHOR
    )
)

CONFIG_DIR = (
    DATA_DIR
    / "config"
)

CONFIG_FILE = (
    CONFIG_DIR
    / "config.yaml"
)


def ensure_dirs():

    CONFIG_DIR.mkdir(
        parents=True,
        exist_ok=True
    )