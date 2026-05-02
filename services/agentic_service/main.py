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
        version=args.version,
        target_path=args.target,
        enable_llm=args.enable_llm
    )

    print(json.dumps(result, indent=2))


def main():
    """
    Main CLI entry point for AutoForge.

    Example:
    python main.py run-security --run-id RUN-0001 --target ./sample_ecommerce_app --enable-llm
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

    security_parser.add_argument(
        "--target",
        default=None,
        help="Target source code folder to scan"
    )

    security_parser.add_argument(
        "--enable-llm",
        action="store_true",
        help="Enable Ollama LLM-assisted secure code review"
    )

    security_parser.set_defaults(func=run_security)

    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        return

    args.func(args)


if __name__ == "__main__":
    main()