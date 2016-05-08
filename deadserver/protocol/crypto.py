import nacl.secret

NONCE_SIZE = nacl.secret.SecretBox.NONCE_SIZE

# TODO: With the faster processor, we probably can afford assymetric crypto. Measure and switch if
#       possible.
class CryptoBox:
    """Provides symmetric encryption and decryption with the given key.

    Somewhat hides the key, in order to avoid e.g. accidentally logging it.
    """
    def __init__(self, key):
        box = nacl.secret.SecretBox(key)
        self.decrypt = lambda nonce, payload: box.decrypt(payload, nonce)
        self.encrypt = lambda nonce, payload: box.encrypt(payload, nonce)[NONCE_SIZE:]  # argh

    def encrypt(self, nonce, payload):
        raise RuntimeError("If you see this, you are doing something terrible. Stop it.")

    def decrypt(self, nonce, payload):
        raise RuntimeError("If you see this, you are doing something terrible. Stop it.")
