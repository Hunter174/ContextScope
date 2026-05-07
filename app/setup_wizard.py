from integrations.manager import IntegrationManager
from config.loader import save_config
from config.paths import CONFIG_FILE
from config.secrets import SecretStore


def run_setup():

    manager = IntegrationManager()

    config = {
        "setup_completed": True,
        "integrations": {}
    }

    for integration in manager.get_supported_integrations():

        if integration.required:
            enabled = "y"
            print(
                f"{integration.name} "
                f"is required."
            )

        else:
            enabled = input(
                f"Enable "
                f"{integration.name}? "
                f"(y/n): "
            )

        if enabled.lower() != "y":
            continue

        integration.setup()

        if not integration.validate():

            print(
                f"{integration.name} "
                f"validation failed."
            )

            continue

        config["integrations"][integration.name] = (integration.export_config())

        secrets = integration.export_secrets()
        for key, value in secrets.items():
            SecretStore.save(f"{integration.name}.{key}", value)

    save_config(config)
    print("Setup complete.")


def reset_setup():
    manager = IntegrationManager()
    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()

    for integration in manager.get_supported_integrations():

        for key in integration.secret_keys():
            SecretStore.delete(f"{integration.name}.{key}")

    print("Configuration reset.")