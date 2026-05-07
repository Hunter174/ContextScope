import keyring


class SecretStore:

    SERVICE_NAME = "contextscope"

    @classmethod
    def save(cls, key, value):

        if value is None:
            return

        keyring.set_password(
            cls.SERVICE_NAME,
            key,
            value
        )

    @classmethod
    def load(cls, key):

        return keyring.get_password(
            cls.SERVICE_NAME,
            key
        )