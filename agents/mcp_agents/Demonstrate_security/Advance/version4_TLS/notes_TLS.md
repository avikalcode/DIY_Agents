JWT travels in plain text. Anyone on the network path can read the Authorization header and replay the token until it expires. TLS encrypts the traffic and proves the server is who it claims to be. It’s transport security,

# quick launch
```
pip install pyjwt[crypto]

cd version4_TLS
python .\gen_cert_localhost.py

cd advance
python -m version4_TLS.mcp_server_tls

if valid token gives error 'HTTPS valid token : status 401' then check for the token is valid or not
python -m version4_TLS.diagnose_token

this check the TLS certificate valid or not but not the trust as it wrap the certificate around socket
python -m version4_TLS.tls_check

Option A: in same terminal window
$env:SSL_CERT_FILE = "$PWD\version4_TLS\certs\cert.pem"

Option B: fo windows trust store and current user credential 
certutil -user -addstore Root certs\cert.pem

Option c: in the code specify explicitly to hhtps2 to get certficate from specific folder
uncomment the line [verify=TLS_CONTEXT]

python -m version4_TLS.todo_mcp_client_JWT_TLS_test
```


## Step 1: Create local certificates
* depreceated makecert 
mkcert -install adds its CA to your system trust store, and Windows may show a confirmation prompt. Add certs/ and private.pem to .gitignore, because key files never get committed.

```
bash

cd version4_TLS
mkcert -install
mkdir certs
mkcert -key-file certs/key.pem -cert-file certs/cert.pem 127.0.0.1 localhost ::1
```

Two points about the certificate:

`The SAN list matters.` 

Modern clients check the Subject Alternative Name and ignore the CN, so the list includes 127.0.0.1 (our URL), localhost, and ::1. A certificate without a matching SAN fails verification even when it’s trusted.

`ca=False.` 

The certificate can vouch only for itself and can’t sign other certificates. That makes trusting it safer than trusting mkcert’s CA, whose stolen key could mint certificates for any website.

## Step 2: Make clients trust it
### Option A: Trust it for one terminal only (no system changes,  recommendation)

httpx2 honors SSL_CERT_FILE before falling back to the system store. 

The trust disappears when you close the terminal, and nothing else on your machine is affected.

In the client terminal:powershell
```
$env:SSL_CERT_FILE = "$PWD\certs\cert.pem"
python jwt_tests.py
```

### Option B: Add it to the Windows trust store (current user)
`certutil -user -addstore Root certs\cert.pem`

Windows will show a security warning asking to confirm adding a root certificate. 

Check that it names the certificate just made (localhost) before clicking Yes. 

Per the migration guide, httpx2 validates against the operating system trust store, so after this the client should trust the server without any environment variable.

## To inspect or remove it:

`GUI: press Win+R, type certmgr.msc,` then open Trusted Root Certification Authorities → Certificates and find localhost.
Command line: certutil -user -delstore Root localhost removes it. Be aware this deletes every certificate with subject localhost in that store, so if you have others, use the GUI instead.

Remove the certificate when you’re done experimenting. A key that sits in a trusted store for a year is a liability, and this one’s key is an unencrypted file in your project folder.

## Step 3: Check it works
Restart the server (it loads certs/key.pem and certs/cert.pem at startup).
In the client terminal (with Option A’s variable set, or after Option B), run tls_check.py from my last message.