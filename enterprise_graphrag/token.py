from __future__ import annotations

import argparse

from .auth import issue_demo_token
from .config import settings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Issue a local-development Enterprise GraphRAG JWT."
    )
    parser.add_argument(
        "--subject",
        required=True,
        help="JWT subject.",
    )
    parser.add_argument(
        "--tenant",
        required=True,
        help="Tenant ID encoded into the token.",
    )
    parser.add_argument(
        "--scope",
        action="append",
        default=[],
        help="Scope to include. Repeat for multiple scopes.",
    )
    return parser


def main() -> None:
    if settings.environment.strip().lower() == "production":
        raise SystemExit(
            "Refusing to mint a demo JWT while GRAGRAPH_ENV=production."
        )

    parser = build_parser()
    args = parser.parse_args()

    if not args.scope:
        args.scope = ["graphrag:query"]

    print(
        issue_demo_token(
            args.subject,
            args.tenant,
            args.scope,
        )
    )


if __name__ == "__main__":
    main()
