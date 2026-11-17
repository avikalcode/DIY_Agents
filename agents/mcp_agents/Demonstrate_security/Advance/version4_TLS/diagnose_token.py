import jwt
from .config import RESOURCE, ISSUER
# from version2_JWT.get_jwt_token import make_token
from .get_jwt_token import make_token

t = make_token("alice", ["todo:read", "todo:write"])
print("header:", jwt.get_unverified_header(t))
print("claims:", jwt.decode(t, options={"verify_signature": False}))
print("server expects aud =", RESOURCE, " iss =", ISSUER)

try:
    jwt.decode(t, open("version2_JWT/public.pem").read(), algorithms=["RS256"],
               audience=RESOURCE, issuer=ISSUER)
    print("local verify: OK")
except Exception as e:
    print("local verify FAILED:", type(e).__name__, e)