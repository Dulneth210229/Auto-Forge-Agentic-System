import argparse
import json

from agents.security_agent.agent import SecurityAgent


def run_security(args):
    """
    CLI handler for running the Security Agent.
    """

    agent = SecurityAgent(output_root="outputs")

    result = agent.run(
        run_id=args.run_id,
        version=args.version
    )

    print(json.dumps(result, indent=2))


def main():
    """
    Main CLI entry point for AutoForge.

    Current supported command:
    python main.py run-security --run-id RUN-0001
    """

    parser = argparse.ArgumentParser(
        description="AutoForge Single-Service Multi-Agent System"
    )

    subparsers = parser.add_subparsers(dest="command")

    security_parser = subparsers.add_parser(
        "run-security",
        help="Run the Security Agent and generate a security report"
    )

    security_parser.add_argument(
        "--run-id",
        default="RUN-0001",
        help="Run ID for this AutoForge execution"
    )

    security_parser.add_argument(
        "--version",
        default="v1",
        help="Artifact version, for example v1, v2, v3"
    )

    security_parser.set_defaults(func=run_security)

    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        return

    args.func(args)


if __name__ == "__main__":
    main()