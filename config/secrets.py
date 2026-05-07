import keyring


class SecretStore:

    SERVICE_NAME = "ContextScope"

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

    @classmethod
    def delete(cls, key):

        try:

            keyring.delete_password(
                cls.SERVICE_NAME,
                key
            )

        except Exception:
            pass