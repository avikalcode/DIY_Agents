import datetime
import ipaddress
import os

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID

# ---------------------------------------------------------------
# 1. The key pair
#   The PRIVATE key stays on the server and proves "I am the owner of this
#   certificate" during the TLS handshake. The PUBLIC key goes inside the
#   certificate for everyone to see. 2048-bit RSA is the common minimum today. 
#   2048-bit RSA key is an asymmetric encryption key pair where the mathematical value (the modulus) used to encrypt and sign data is 2048 binary digits (bits) long
# ---------------------------------------------------------------
key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

# ---------------------------------------------------------------
# 2. Subject name and CN (Common Name)
#   Subject = who the certificate is about. CN is a human-readable label.
#   Modern clients do NOT use CN to check the hostname; they use the SAN
#   below). still set a CN because many tools display it and the name
#   field can't be empty in practice.
# ---------------------------------------------------------------
name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "localhost")])

now = datetime.datetime.now(datetime.timezone.utc)

cert = (
    x509.CertificateBuilder()
    .subject_name(name) # 
    
    # -----------------------------------------------------------
    # 3. Issuer
    # Who signed this certificate. Here issuer == subject, which is exactly
    # what "self-signed" means: we vouch for ourselves. That's why clients
    # won't trust it until we add it to a trust store ourselves.
    # -----------------------------------------------------------
    .issuer_name(name)                      # self-signed: issuer == subject
    .public_key(key.public_key())           # The public key that the certificate binds to the subject.
    
    # -----------------------------------------------------------
    # 4. Serial number
    # A unique number per certificate from its issuer. Used for revocation
    # and to tell certificates apart. Random is the standard approach.
    # -----------------------------------------------------------
    .serial_number(x509.random_serial_number())
    
    # -----------------------------------------------------------
    # 5. Validity period (not_valid_before / not_valid_after)
    # Outside this window clients reject the certificate.  start 5 minutes
    # in the past so a slightly wrong system clock doesn't cause "not yet
    # valid". One year is fine for local use; shorter lifetimes limit damage
    # if the key leaks.
    # -----------------------------------------------------------
    .not_valid_before(now - datetime.timedelta(minutes=5))
    .not_valid_after(now + datetime.timedelta(days=365))

    # -----------------------------------------------------------
    # 6. SAN (Subject Alternative Name)  <-- the important one
    # The list of hostnames/IPs this certificate is valid FOR. Clients
    # compare the address they connected to against this list. If it isn't
    # here, verification fails even if the certificate is trusted.
    #   DNSName   -> matches host names like https://localhost:8000
    #   IPAddress -> matches https://127.0.0.1:8000 and https://[::1]:8000
    # Our server URL uses 127.0.0.1, so that IP MUST be listed.
    # -----------------------------------------------------------
    .add_extension(x509.SubjectAlternativeName([
        x509.DNSName("localhost"),
        x509.IPAddress(ipaddress.ip_address("127.0.0.1")),
        x509.IPAddress(ipaddress.ip_address("::1")),
    ]), critical=False)

    # -----------------------------------------------------------
    # 7. BasicConstraints: ca=False
    # Says "this is an ordinary (leaf) certificate, NOT a certificate
    # authority". It can't be used to sign other certificates. This limits
    # the damage if the key is stolen, since the attacker can't mint
    # certificates for other sites. critical=True means clients must
    # understand and obey this field.
    # -----------------------------------------------------------
    .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)

    # -----------------------------------------------------------
    # 8. KeyUsage
    # What the KEY may be used for. We allow:
    #   digital_signature -> signing the TLS handshake
    #   key_encipherment  -> RSA key exchange (older TLS modes)
    # Everything else is switched off, including key_cert_sign (signing
    # other certificates), which stays False.
    # -----------------------------------------------------------
    .add_extension(x509.KeyUsage(
        digital_signature=True, key_encipherment=True,
        content_commitment=False, data_encipherment=False, key_agreement=False,
        key_cert_sign=False, crl_sign=False,
        encipher_only=False, decipher_only=False), critical=True)

     # -----------------------------------------------------------
    # 9. ExtendedKeyUsage: SERVER_AUTH
    # The PURPOSE of the certificate: authenticating a TLS server. Without
    # it, some clients refuse the certificate for HTTPS.
    # -----------------------------------------------------------
    .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]), critical=False)

     # -----------------------------------------------------------
    # 10. Signature (SHA-256)
    # The issuer signs the certificate's contents. Because it's self-signed,
    # we sign with our own private key. SHA-256 is the hash used; SHA-1 is
    # obsolete and rejected by clients.
    # -----------------------------------------------------------
    .sign(key, hashes.SHA256())
)

# ---------------------------------------------------------------
# 11. Write the files
# key.pem  = PRIVATE key. Secret. Never commit it or share it.
#            (NoEncryption means it isn't password-protected, which is
#            convenient for local dev but means file permissions are the
#            only protection.)
# cert.pem = the PUBLIC certificate. Safe to share; this is the file you
#            add to a trust store or point SSL_CERT_FILE at.
# ---------------------------------------------------------------
os.makedirs("certs", exist_ok=True)
with open("certs/key.pem", "wb") as f:
    f.write(key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption()))
with open("certs/cert.pem", "wb") as f:
    f.write(cert.public_bytes(serialization.Encoding.PEM))
print("Wrote certs/key.pem and certs/cert.pem")