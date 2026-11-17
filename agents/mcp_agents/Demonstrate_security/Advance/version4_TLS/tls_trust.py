import ssl
from pathlib import Path

CERT = Path(__file__).parent / "certs" / "cert.pem"

# system CAs + our self-signed certificate
TLS_CONTEXT = ssl.create_default_context(cafile=str(CERT))