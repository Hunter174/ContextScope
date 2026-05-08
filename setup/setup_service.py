from integrations.manager import IntegrationManager

from config.loader import save_config
from config.secrets import SecretStore


DEFAULT_CONFIG = {
    "version": 1,
    "setup_completed": True,
    "integrations": {}
}


def run_setup():
    manager = IntegrationManager()
    config = DEFAULT_CONFIG.copy()

    for integration in manager.get_supported_integrations():
        enabled = prompt_integration_enabled(integration)

        if not enabled:
            continue

        print(f"Setting up {integration.name}...")

        integration.setup()

        if not integration.validate():
            print(f"{integration.name} validation failed.")

            continue

        save_integration_config(config, integration)
        save_integration_secrets(integration)

    save_config(config)

    print("Setup complete.")


def prompt_integration_enabled(integration):
    if integration.required:
        print(f"{integration.name} is required.")
        return True

    response = input(f"Enable {integration.name}? (y/n): ")
    return response.lower() == "y"


def save_integration_config(config, integration):
    config["integrations"][integration.name] = {
        "enabled": True,
        **integration.export_config()
    }

def save_integration_secrets(integration):
    secrets = integration.export_secrets()
    for key, value in secrets.items():
        SecretStore.save(f"{integration.name}.{key}", value)