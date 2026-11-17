# Quick launch
```
cd advance/version2_jwt
python gen_keys.py

cd Advance
python -m version2_JWT.todo_mcp_server   
python -m version2_JWT.todo_mcp_client_JWT_test
```

`version 1` showed static secret tokens , it is the better choice when:

- Revocation is immediate. Remove a token from the list and it’s dead. 

- Simplicity. For a small internal tool with two trusted callers, static tokens are fine. Plenty of real APIs work this way.

`version 2` is extension of version 1

- Tokens expire, so a leaked token stops working.

- Tokens are tied to this server through the aud and iss claims, so a token minted for another service is rejected.

- The server holds only a public key. It can check tokens but can’t create them.

- Authorization: a read-only token can list but can’t add or remove.

- Data isolation: Alice and Bob each see only their own todos.

# Authentication vs authorization

This is the key idea of version 2 is:

`Authentication (v1 and v2)`: proving who the user is (identity). Both stages do this, the second more robustly.

`Authorization (v2 only):` deciding what user may do. Scopes and per-user data separation are new in this stage.

In v1, a valid token meant total access. In v2, a valid token means “identified, and limited to what the token’s scopes and your own data allow.”

### The Difference Between the Two Approaches

| Feature | v1: Static Tokens | v2: Signed JWTs |
| :--- | :--- | :--- |
| **What the token is** | A random string the server has memorized | A signed document containing claims (who, what, until when) |
| **How the server checks it** | Looks it up in its own list | Verifies the signature with a public key, then checks the claims |
| **What the server must store** | Every valid token (secrets) | Only a public key (not secret) |
| **Adding a user** | Change server config and restart | Issue a new token; the server needs no change |
| **Expiry** | None. Valid forever until you rotate it | Built in (`exp`) |
| **Permissions** | All tokens equal | Scopes in the token (`todo:read`, `todo:write`) |


`Static tokens are simple but crude. Each one is a password the server has to guard, and all of them are equally powerful. JWTs move trust to a signature, so the server can verify tokens it didn’t create and doesn’t remember.`

### What v2 adds

| Feature | Fixes this problem from 2.3 |
| :--- | :--- |
| **Signed JWT (RS256)** | Tokens were opaque secrets, and the server held a list of them. Now the server holds only a public key and can verify tokens but can’t forge them. |
| **Expiry (`exp`)** | A leaked token worked forever. |
| **Audience (`aud`) + issuer (`iss`)** | A token minted for another service can’t be replayed against this one. |
| **Scopes per tool** | Every valid token could do everything. Now `todo:read` and `todo:write` are separate. |
| **Per-user todos** | Alice could delete Bob’s items. Now each `sub` has its own list. |


## dependency 
`pip install "pyjwt[crypto]"`

## asymettric keys 

**Private key** : `private.pem is the signing key. Keep it out of git, and the server never reads it. Only public.pem goes to the server.`

- Serilailization: Bytes

- Encoding  : PEM

- Format    : PKCS8

- Encryptes : No

- Signing private key using
-- Step 1. Hashing algo     : SHA256
-- Step 2. Encrypting algo  : RSA (other encryption HS256)

**Public Key**
- Serilailization: Bytes

- Encoding  : PEM

- Encryptes : No

