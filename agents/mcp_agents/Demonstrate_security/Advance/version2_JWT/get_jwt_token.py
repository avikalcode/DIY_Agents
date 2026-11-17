#In real life a separate authorization server does this job (Level 3). Here it’s a helper so to mint test tokens.import time, uuid
import time, uuid
import jwt

# from agents.mcp_agents.Demonstrate_security.Advance.version3.mcp_server_v3 import CURRENT_DIR

from .config import ISSUER, RESOURCE

# RW = ["todo:read", "todo:write"]

def make_token(sub: str, #user id, e.g. "alice" or "bob"
               scopes: list[str], 
               ttl: int = 3600, 
               aud: str = RESOURCE
               ) -> str:
    
    now = int(time.time())
    
    payload = {
        "iss": ISSUER, 
        "sub": sub, # user id, e.g. "alice" or "bob"
        "aud": aud,
        "iat": now, 
        "exp": now + ttl,
        "scope": " ".join(scopes),
        "jti": str(uuid.uuid4()), # unique identifier for the token, used to prevent replay attacks
    }

    from pathlib import Path
    # 1. Get the folder where THIS python file lives (version2/)
    CURRENT_DIR = Path(__file__).resolve().parent
        
    # 2. Go up one level (.parent) and into version2/private.pem
    KEY_PATH = CURRENT_DIR.parent / "version2_JWT" / "private.pem"
    # PRIVATE_KEY = open(KEY_PATH).read()    

    with open(KEY_PATH, "r") as f:
        PRIVATE_KEY = f.read()

    # encode the payload, then hash it and then encrypt the hash with the private key to create a signature. 
    # The signature is appended to the payload to form the final JWT token.
    return jwt.encode(payload, PRIVATE_KEY, algorithm="RS256")

# --------breakdown of what each part does:
# • jwt.encode(...): The function that takes data, formats it into standard JWT sections 
#                   (Header, Payload, Signature), and outputs a Base64-encoded token string.
#                   The JWT header explicitly specifies the algorithm being used: {
#                                                                                   "alg": "RS256",
#                                                                                   "typ": "JWT"
#                                                                                  }

# • payload: A Python dictionary containing the claims (data) that is inside the token—such as the 
#           user ID (sub),
#           expiration time (exp), 
#           issuer (iss), 
#           audience (aud), 
#           permissions (scope).

# • open("private.pem").read(): Reads RSA Private Key from a local file named private.pem. 
#                               This key is used to mathematically sign the token. 
#                               Because only auth server has this private key, nobody else can forge a valid token.

# • algorithm="RS256":  Specifies the signing algorithm (RSA Signature with SHA-256). 
#                       Unlike symmetric algorithms (HS256) where the same secret key signs and verifies the token, 
#                       RS256 uses a public/private key pair:

# 	• Auth Server (Minting): Uses private.pem to sign the token.

# 	• Resource Server (Verifying): Uses the corresponding public.pem to verify the token is authentic—without needing access to the private key.