# KONACH Admin License Tool - Internal Operations Guide

## 1) Purpose
The Admin License Tool is an internal-only utility used to:
- Generate Ed25519 key pairs (private/public)
- Accept customer request codes
- Issue signed machine-bound license JSON blobs

This tool must remain separate from client deliverables.

## 2) Standard Workflow (Request Code -> License)
1. Customer runs client app and obtains request code.
2. Admin opens `LicenseAdminTool.exe`.
3. Admin pastes request code and customer metadata.
4. Admin signs license with private key.
5. Admin sends generated license JSON to customer.
6. Customer imports license into client activation dialog.

## 3) How to Generate and Approve Licenses
1. Open tool.
2. (Optional) click `Generate Keys` for first setup.
3. Select private key path.
4. Paste request code.
5. Set customer name, status, and duration in days.
6. Click `Issue License`.
7. Deliver JSON output securely to the customer.

## 4) Safe Issuance Rules
- Verify customer identity before issuing.
- Ensure request code is from the intended machine.
- Use short license durations for pilots/testing.
- Keep issuance records and change approvals.

## 5) Revoke or Replace License
- Revoke by issuing a new license with `status=revoked`.
- Replace by issuing a new valid license for same customer/machine after approval.
- Keep audit trail of old and replacement license IDs.

## 6) Output Locations
- Default output file: `license.json` in current folder
- Keys directory default: `keys/`
- Copy-to-clipboard is available for quick secure transfer

## 7) Operational Precautions
- Restrict tool usage to authorized operators.
- Use role-based workstation access and endpoint protection.
- Back up issuance records and key metadata securely.

## 8) Security Precautions
- Private key is strictly confidential and never shared with clients.
- Client package must include only public key for verification.
- Do not store private key in source control, shared folders, or installer assets.
- Rotate keys per policy and maintain key-version mapping (`key_id`).

## 9) Reusing This Licensing Architecture in Another Program
You can reuse this architecture for another product by keeping the same pattern:
- Request code encoder in client
- License signer in admin tool
- Signature verification in client startup gate

### Reusable Components
- `services/licensing/license_codec.py` (encoding/parsing/signature verification)
- `services/licensing/fingerprint.py` (machine fingerprint model)
- Admin-side signing logic from `admin_license_tool/issue_license.py`

### Components That Must Stay Private
- Private key files
- Admin issuance workflow, approval policies, and revocation decisions
- Any internal operator/audit metadata

## 10) Adapting to Another Product
- Change app identity fields (`app_id`, product name, versions).
- Change branding strings in GUI and readme.
- Keep cryptographic flow unchanged unless security review approves changes.

## 11) Adapting DB and License Schema
- Keep `licensed_machines`, `app_installations`, and `license_audit_log` as baseline.
- Add product-specific columns with additive migrations.
- Version all schema changes via numbered SQL migration files.

## 12) Internal Support Notes
- If a customer reports "signature invalid", verify public key mismatch first.
- If customer reports "fingerprint mismatch", request a fresh request code.
- If activation fails with malformed key, validate env key format and encoding.
