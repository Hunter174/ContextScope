from config.paths import ensure_dirs
from config.loader import is_setup_complete
from setup.setup_service import run_setup
from setup.reset_service import reset_setup

from app.main import run_app


def bootstrap(force_setup=False, reset=False):

    ensure_dirs()

    if reset:
        print("Resetting configuration...")
        reset_setup()

    needs_setup = (
        force_setup
        or not is_setup_complete()
    )

    if needs_setup:
        print("Running setup...")
        run_setup()

    run_app()