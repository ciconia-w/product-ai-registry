---
name: send-email
version: 0.1.0
description: Use the registry send-email script safely by checking SMTP prerequisites, environment variables, and provider-specific setup before attempting delivery
---

# Send Email

Use this skill when an agent needs to send a plaintext email through the registry `script:send-email`.

This skill exists because email sending is not just a script execution problem:

- the mailbox provider must allow SMTP
- an app password or authorization code is usually required
- the runtime environment must provide SMTP credentials
- some hosts need proxy or IPv4 overrides

The script sends mail.
This skill makes sure the script is used correctly.

## When To Use

Use this skill when:

- the user asks to send an email
- another skill needs to mail a report or digest
- you need to verify SMTP configuration before relying on `script:send-email`

## Required Preconditions

Before sending:

1. Confirm the mailbox provider has SMTP enabled.
2. Confirm the account has an app password / SMTP authorization code if the provider requires one.
3. Confirm these environment variables are present:

```text
SMTP_SERVER
SMTP_PORT
SMTP_USERNAME
SMTP_PASSWORD
```

Optional environment variables:

```text
SMTP_FROM_EMAIL
SMTP_FROM_NAME
EMAIL_SENDER_NAME
SMTP_USE_SSL
SMTP_USE_STARTTLS
SMTP_PROXY_HOST
SMTP_PROXY_PORT
SMTP_PROXY_TYPE
SMTP_FORCE_IPV4
SMTP_TIMEOUT
```

## Provider Setup Guidance

### 163 / NetEase Mail

Typical setup:

- enable SMTP in mailbox settings
- generate an authorization code
- use:
  - `SMTP_SERVER=smtp.163.com`
  - `SMTP_PORT=465`
  - `SMTP_USE_SSL=true`

### Gmail

Typical setup:

- use an app password instead of the normal account password
- use:
  - `SMTP_SERVER=smtp.gmail.com`
  - `SMTP_PORT=587`
  - `SMTP_USE_STARTTLS=true`

Do not assume a provider accepts direct username/password login without prior SMTP enablement.

## Execution Flow

1. Verify SMTP env vars exist.
2. If the host needs a proxy, set `SMTP_PROXY_*`.
3. If the host has IPv6 or routing issues, set `SMTP_FORCE_IPV4=true`.
4. Send using the script:

```bash
python3 scripts/send-email/run.py "<recipient>" "<subject>" "<body>"
```

Optional sender display name override:

```bash
python3 scripts/send-email/run.py "<recipient>" "<subject>" "<body>" --from-name "Ops Bot"
```

## Failure Handling

If sending fails, report which class of failure occurred:

- missing SMTP environment variables
- provider SMTP not enabled
- invalid authorization code / app password
- TLS / SSL mismatch
- proxy or network routing issue
- recipient rejection

Do not claim the mail was sent unless the script reports success.

## Recommended Usage Pattern

When another capability needs email delivery:

1. prepare the report body first
2. verify SMTP configuration
3. call `script:send-email`
4. report success or the exact blocker

## Notes

- This skill is intentionally provider-agnostic.
- Credentials must come from environment variables or another secure host mechanism, never from hardcoded values in repository files.
