import argparse
import logging
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


logger = logging.getLogger(__name__)


def generate_keypair(out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)

    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    private_path = out_dir / "private_key.pem"
    public_path = out_dir / "public_key.pem"

    private_path.write_bytes(private_pem)
    public_path.write_bytes(public_pem)

    return private_path, public_path


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

    parser = argparse.ArgumentParser(description="Generate KONACH Ed25519 signing keys")
    parser.add_argument("--out-dir", default="keys", help="Output directory")
    args = parser.parse_args()

    private_path, public_path = generate_keypair(Path(args.out_dir))

    logger.info("Private key: %s", private_path)
    logger.info("Public key:  %s", public_path)
    logger.info("Set KONACH_LICENSE_PUBLIC_KEY_PEM on client side with public key content.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
