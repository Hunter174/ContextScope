from integrations.manager import IntegrationManager

from config.paths import CONFIG_FILE
from config.secrets import SecretStore


def reset_setup():

    manager = IntegrationManager()

    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()

    for integration in manager.get_supported_integrations():

        for key in integration.secret_keys():

            SecretStore.delete(
                f"{integration.name}.{key}"
            )

    print("Configuration reset.")