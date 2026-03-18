# KONACH Admin License Tool (Private)

This tool is intentionally separated from the client application runtime.
Do NOT ship this folder to customers.

## Purpose

- Generate keypair for licensing
- Parse machine request codes
- Issue signed licenses bound to machine fingerprint

## Security Rules

- `keys/private_key.pem` must stay private and never be copied to the client app
- Only `keys/public_key.pem` (or its text content) is allowed in client deployment
- Exclude `admin_license_tool/` from customer installer output

## Usage

1. Generate keys once:

```powershell
python generate_keys.py
```

### GUI mode (simple)

Run:

```powershell
python main.py
```

In the GUI:

1. Paste `Request Code` from client app.
2. Enter `Customer` and `Days`.
3. Select status (`active` by default).
4. Verify `Private Key` path (`keys/private_key.pem`).
5. Verify `Client Public Key` path (`config/license_public_key.pem`) so the tool can enforce key compatibility.
6. Click `Issue License`.
7. Use `Copy License JSON` and send to customer.

Important:
- If you click `Generate Keys`, a new key pair is created.
- Licenses signed by that new private key will fail in client unless the matching public key is deployed to client config.

2. Issue a license from request code:

```powershell
python issue_license.py --request-code "<REQUEST_CODE>" --customer "Customer A" --days 365 --expected-public-key "config/license_public_key.pem" --out "license.json"
```

3. Share `license.json` with customer.

## Output Contract

The generated license is an Ed25519-signed JSON envelope.
The client verifies signature, hardware ID, status, and expiry.

Standard license JSON fields:

```json
{
	"hwid": "...",
	"customer": "...",
	"issued_at": "...",
	"expires_at": "...",
	"signature": "..."
}
```
