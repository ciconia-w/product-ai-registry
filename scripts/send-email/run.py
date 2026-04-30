#!/usr/bin/env python3
import argparse
import os
import smtplib
import socket
from contextlib import contextmanager
from email.mime.text import MIMEText
from email.utils import formataddr


def env_bool(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def require_env(name):
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"missing required environment variable: {name}")
    return value


@contextmanager
def network_overrides():
    original_socket = socket.socket
    original_getaddrinfo = socket.getaddrinfo
    try:
        if env_bool("SMTP_FORCE_IPV4", False):
            def ipv4_only(host, port, family=0, type=0, proto=0, flags=0):
                return original_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
            socket.getaddrinfo = ipv4_only

        proxy_host = os.getenv("SMTP_PROXY_HOST")
        if proxy_host:
            try:
                import socks
            except ImportError as exc:
                raise RuntimeError("SMTP proxy requested but PySocks is not installed") from exc
            proxy_type_name = os.getenv("SMTP_PROXY_TYPE", "http").strip().lower()
            proxy_type_map = {
                "http": socks.HTTP,
                "socks4": socks.SOCKS4,
                "socks5": socks.SOCKS5,
            }
            proxy_type = proxy_type_map.get(proxy_type_name)
            if proxy_type is None:
                raise RuntimeError(f"unsupported SMTP_PROXY_TYPE: {proxy_type_name}")
            proxy_port = int(os.getenv("SMTP_PROXY_PORT", "3128"))
            socks.set_default_proxy(proxy_type, proxy_host, proxy_port)
            socket.socket = socks.socksocket
        yield
    finally:
        socket.socket = original_socket
        socket.getaddrinfo = original_getaddrinfo


def send_email(to_email, subject, body, sender_name=None):
    smtp_server = require_env("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT", "465"))
    smtp_username = require_env("SMTP_USERNAME")
    smtp_password = require_env("SMTP_PASSWORD")
    from_email = os.getenv("SMTP_FROM_EMAIL", smtp_username)
    from_name = sender_name or os.getenv("EMAIL_SENDER_NAME") or os.getenv("SMTP_FROM_NAME") or "Registry Mail Sender"
    timeout = int(os.getenv("SMTP_TIMEOUT", "30"))
    use_ssl = env_bool("SMTP_USE_SSL", smtp_port == 465)
    use_starttls = env_bool("SMTP_USE_STARTTLS", not use_ssl)

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = formataddr((from_name, from_email))
    msg["To"] = to_email

    with network_overrides():
        if use_ssl:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=timeout)
        else:
            server = smtplib.SMTP(smtp_server, smtp_port, timeout=timeout)
            if use_starttls:
                server.starttls()

        try:
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        finally:
            server.quit()


def build_parser():
    parser = argparse.ArgumentParser(
        description="Send a plaintext email using SMTP configuration from environment variables."
    )
    parser.add_argument("to_email", help="recipient email address")
    parser.add_argument("subject", help="email subject")
    parser.add_argument("body", help="email body")
    parser.add_argument(
        "--from-name",
        default=None,
        help="override sender display name; defaults to EMAIL_SENDER_NAME or SMTP_FROM_NAME",
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    try:
        send_email(args.to_email, args.subject, args.body, sender_name=args.from_name)
    except Exception as exc:
        print(f"❌ failed to send email: {exc}")
        raise SystemExit(1)
    print(f"✅ email sent to: {args.to_email}")


if __name__ == "__main__":
    main()
