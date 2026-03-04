"""
mTLS-Zertifikats-Generator für ATLAS GQA Refactor F3 (unified-auth-mtls).

Erzeugt:
- Root CA (atlas-ca)
- Server CA (atlas-srv) und Client CA (atlas-cli)
- Server-Zertifikate: atlas-api, mcp-server, openclaw-server
- Client-Zertifikate: cursor, scout, oc-brain, ha, atlas-client

Ausgabe: data/certs/ (nicht versionieren – .gitignore: data/certs/)

Verwendung:
    python -m src.scripts.generate_mtls_certs [--output DIR] [--days N]

Hinweis: Für Produktion CA-Key separat sichern; ideal mit HSM/Vault.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
from ipaddress import ip_address
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID, ExtensionOID


def _make_key(bits: int = 2048):
    return rsa.generate_private_key(public_exponent=65537, key_size=bits)


def _save_key(key, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ))


def _save_cert(cert: x509.Certificate, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))


def _subject(cn: str, o: str = "ATLAS_CORE") -> x509.Name:
    return x509.Name([
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, o),
        x509.NameAttribute(NameOID.COMMON_NAME, cn),
    ])


def create_root_ca(out_dir: Path, days: int = 3650) -> tuple[x509.Certificate, rsa.RSAPrivateKey]:
    """Root CA (10 Jahre)."""
    key = _make_key()
    subject = issuer = _subject("atlas-ca.local")
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(timezone.utc))
        .not_valid_after(datetime.now(timezone.utc) + timedelta(days=days))
        .add_extension(x509.BasicConstraints(ca=True, path_length=2), critical=True)
        .add_extension(x509.KeyUsage(
            digital_signature=True,
            key_cert_sign=True,
            crl_sign=True,
            key_encipherment=False,
            content_commitment=False,
            data_encipherment=False,
            key_agreement=False,
            encipher_only=False,
            decipher_only=False,
        ), critical=True)
        .sign(key, hashes.SHA256())
    )
    _save_key(key, out_dir / "ca_root.key")
    _save_cert(cert, out_dir / "ca_root.pem")
    return cert, key


def create_intermediate_ca(
    name: str,
    cn: str,
    root_cert: x509.Certificate,
    root_key: rsa.RSAPrivateKey,
    out_dir: Path,
    days: int = 3650,
) -> tuple[x509.Certificate, rsa.RSAPrivateKey]:
    """Intermediate CA (Server oder Client)."""
    key = _make_key()
    subject = _subject(cn)
    issuer = root_cert.subject
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(timezone.utc))
        .not_valid_after(datetime.now(timezone.utc) + timedelta(days=days))
        .add_extension(x509.BasicConstraints(ca=True, path_length=1), critical=True)
        .add_extension(x509.KeyUsage(
            digital_signature=True,
            key_cert_sign=True,
            crl_sign=True,
            key_encipherment=False,
            content_commitment=False,
            data_encipherment=False,
            key_agreement=False,
            encipher_only=False,
            decipher_only=False,
        ), critical=True)
        .sign(root_key, hashes.SHA256())
    )
    _save_key(key, out_dir / f"ca_{name}.key")
    _save_cert(cert, out_dir / f"ca_{name}.pem")
    return cert, key


def create_server_cert(
    name: str,
    cn: str,
    sans: list[str],
    ca_cert: x509.Certificate,
    ca_key: rsa.RSAPrivateKey,
    out_dir: Path,
    days: int = 365,
) -> None:
    """Server-Zertifikat mit SAN."""
    key = _make_key()
    subject = _subject(cn)
    issuer = ca_cert.subject
    san_list = []
    for s in sans:
        try:
            addr = ip_address(s)
            san_list.append(x509.IPAddress(addr))
        except ValueError:
            san_list.append(x509.DNSName(s))
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(timezone.utc))
        .not_valid_after(datetime.now(timezone.utc) + timedelta(days=days))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(
            x509.SubjectAlternativeName(san_list),
            critical=False,
        )
        .add_extension(x509.KeyUsage(
            digital_signature=True,
            key_encipherment=True,
            key_cert_sign=False,
            crl_sign=False,
            content_commitment=False,
            data_encipherment=False,
            key_agreement=False,
            encipher_only=False,
            decipher_only=False,
        ), critical=True)
        .add_extension(
            x509.ExtendedKeyUsage([x509.oid.ExtendedKeyUsageOID.SERVER_AUTH]),
            critical=False,
        )
        .sign(ca_key, hashes.SHA256())
    )
    _save_key(key, out_dir / f"{name}.key")
    _save_cert(cert, out_dir / f"{name}.pem")


def create_client_cert(
    name: str,
    cn: str,
    ca_cert: x509.Certificate,
    ca_key: rsa.RSAPrivateKey,
    out_dir: Path,
    days: int = 365,
) -> None:
    """Client-Zertifikat."""
    key = _make_key()
    subject = _subject(cn)
    issuer = ca_cert.subject
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(timezone.utc))
        .not_valid_after(datetime.now(timezone.utc) + timedelta(days=days))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(x509.KeyUsage(
            digital_signature=True,
            key_encipherment=True,
            key_cert_sign=False,
            crl_sign=False,
            content_commitment=False,
            data_encipherment=False,
            key_agreement=False,
            encipher_only=False,
            decipher_only=False,
        ), critical=True)
        .add_extension(
            x509.ExtendedKeyUsage([x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH]),
            critical=False,
        )
        .sign(ca_key, hashes.SHA256())
    )
    _save_key(key, out_dir / f"{name}.key")
    _save_cert(cert, out_dir / f"{name}.pem")


def main() -> int:
    parser = argparse.ArgumentParser(description="ATLAS mTLS Zertifikats-Generator")
    parser.add_argument("--output", "-o", default="data/certs", help="Ausgabe-Verzeichnis")
    parser.add_argument("--days", "-d", type=int, default=365, help="Gültigkeit Server/Client-Certs (Tage)")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    out_dir = (root / args.output).resolve()
    days = args.days

    print(f"[mTLS] Erzeuge Zertifikate in {out_dir}")
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Root CA
    print("  [1/6] Root CA (atlas-ca)...")
    root_cert, root_key = create_root_ca(out_dir)

    # 2. Intermediate CAs
    print("  [2/6] Server CA (atlas-srv)...")
    srv_ca_cert, srv_ca_key = create_intermediate_ca(
        "srv", "atlas-srv.local", root_cert, root_key, out_dir
    )
    print("  [3/6] Client CA (atlas-cli)...")
    cli_ca_cert, cli_ca_key = create_intermediate_ca(
        "cli", "atlas-cli.local", root_cert, root_key, out_dir
    )

    # 3. Server-Zertifikate
    print("  [4/6] Server-Zertifikate...")
    create_server_cert(
        "atlas-api",
        "atlas-api.dreadnought.local",
        ["atlas-api.local", "localhost", "127.0.0.1"],
        srv_ca_cert, srv_ca_key, out_dir, days,
    )
    create_server_cert(
        "mcp-server",
        "mcp.vps.atlas.local",
        ["mcp.vps.atlas.local", "localhost", "127.0.0.1"],
        srv_ca_cert, srv_ca_key, out_dir, days,
    )
    create_server_cert(
        "openclaw-server",
        "openclaw.vps.atlas.local",
        ["openclaw.vps.atlas.local", "localhost", "127.0.0.1"],
        srv_ca_cert, srv_ca_key, out_dir, days,
    )

    # 4. Client-Zertifikate
    print("  [5/6] Client-Zertifikate...")
    for name, cn in [
        ("cursor", "cursor.dreadnought.local"),
        ("scout", "scout.raspi.local"),
        ("oc-brain", "oc-brain.vps.atlas.local"),
        ("ha", "ha.scout.local"),
        ("atlas-client", "atlas.dreadnought.local"),
    ]:
        create_client_cert(name, cn, cli_ca_cert, cli_ca_key, out_dir, days)

    # 5. Chain-Dateien (Server + Client CA für Validierung)
    print("  [6/6] CA-Chains...")
    chain_srv = root_cert.public_bytes(serialization.Encoding.PEM) + srv_ca_cert.public_bytes(serialization.Encoding.PEM)
    chain_cli = root_cert.public_bytes(serialization.Encoding.PEM) + cli_ca_cert.public_bytes(serialization.Encoding.PEM)
    (out_dir / "chain_server.pem").write_bytes(chain_srv)
    (out_dir / "chain_client.pem").write_bytes(chain_cli)

    print(f"\n[SUCCESS] Zertifikate in {out_dir}")
    print("  CA: ca_root.pem, ca_srv.pem, ca_cli.pem")
    print("  Server: atlas-api.pem/.key, mcp-server.pem/.key, openclaw-server.pem/.key")
    print("  Client: cursor.pem/.key, scout.pem/.key, oc-brain.pem/.key, ha.pem/.key, atlas-client.pem/.key")
    print("  Chains: chain_server.pem (Server-Validierung), chain_client.pem (Client-Validierung)")
    print("\n  ACHTUNG: data/certs/ in .gitignore aufnehmen; niemals committen.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
