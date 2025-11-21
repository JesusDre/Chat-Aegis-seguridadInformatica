# firma.py
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.backends import default_backend
import base64
from pathlib import Path

KEY_DIR = Path("keys")
PRIVATE_KEY = KEY_DIR / "private.pem"
PUBLIC_KEY = KEY_DIR / "public.pem"


def generar_llaves():
    KEY_DIR.mkdir(exist_ok=True)

    if not PRIVATE_KEY.exists():
        private = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public = private.public_key()

        with open(PRIVATE_KEY, "wb") as f:
            f.write(
                private.private_bytes(
                    serialization.Encoding.PEM,
                    serialization.PrivateFormat.PKCS8,
                    serialization.NoEncryption()
                )
            )

        with open(PUBLIC_KEY, "wb") as f:
            f.write(
                public.public_bytes(
                    serialization.Encoding.PEM,
                    serialization.PublicFormat.SubjectPublicKeyInfo
                )
            )


def cargar_llave_privada():
    with open(PRIVATE_KEY, "rb") as f:
        return serialization.load_pem_private_key(
            f.read(), password=None, backend=default_backend()
        )


def firmar_bytes(data: bytes) -> str:
    """Firma y regresa texto Base64."""
    private = cargar_llave_privada()
    signature = private.sign(
        data,
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    return base64.b64encode(signature).decode()
