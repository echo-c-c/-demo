#!/usr/bin/env python3
"""
Cross-platform server launcher for production/deployment.

Usage examples:
  - python start_server.py --host 0.0.0.0 --port 8080
  - HOST=0.0.0.0 PORT=8080 python start_server.py
  - With SSL:
      python start_server.py --host 0.0.0.0 --port 8443 \
        --ssl-certfile /path/to/fullchain.pem \
        --ssl-keyfile /path/to/privkey.pem

Notes:
  - This runs `backend.main:app` with uvicorn.
  - Do NOT use --reload in production.
  - Reads environment variables if CLI flags are not supplied:
      HOST, PORT, WORKERS, LOG_LEVEL, SSL_CERTFILE, SSL_KEYFILE
"""

import os
import argparse
import uvicorn


def positive_int(value: str) -> int:
    try:
        ivalue = int(value)
        if ivalue <= 0:
            raise ValueError
        return ivalue
    except ValueError:
        raise argparse.ArgumentTypeError("must be a positive integer")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Start FastAPI server (uvicorn)")
    parser.add_argument("--host", default=os.getenv("HOST", "0.0.0.0"), help="Bind address (default from HOST env or 0.0.0.0)")
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", "8080")), help="Port (default from PORT env or 8080)")
    parser.add_argument("--workers", type=positive_int, default=int(os.getenv("WORKERS", "1")), help="Number of worker processes (default from WORKERS env or 1)")
    parser.add_argument("--log-level", default=os.getenv("LOG_LEVEL", "info"), choices=["critical", "error", "warning", "info", "debug", "trace"], help="Log level")
    parser.add_argument("--ssl-certfile", default=os.getenv("SSL_CERTFILE"), help="Path to SSL certificate file (PEM)")
    parser.add_argument("--ssl-keyfile", default=os.getenv("SSL_KEYFILE"), help="Path to SSL key file (PEM)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    ssl_certfile = args.ssl_certfile if args.ssl_certfile else None
    ssl_keyfile = args.ssl_keyfile if args.ssl_keyfile else None

    uvicorn.run(
        "backend.main:app",
        host=args.host,
        port=args.port,
        workers=args.workers,
        log_level=args.log_level,
        ssl_certfile=ssl_certfile,
        ssl_keyfile=ssl_keyfile,
        # proxy_headers allows correct client IPs when behind reverse proxies like Nginx
        proxy_headers=True,
        forwarded_allow_ips="*",
    )


if __name__ == "__main__":
    main()
