"""UEFNiVERSE Free-Python tool template.

One-sentence description of what this tool does.

Usage:
    python tool_template.py --example-option value
"""

import argparse


def build_parser() -> argparse.ArgumentParser:
    """Define the tool's command-line interface."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--example-option",
        type=str,
        default="default",
        help="Replace with your actual options",
    )
    return parser


def run(example_option: str) -> None:
    """Main tool logic goes here."""
    print(f"[ToolTemplate] Running with example_option={example_option!r}")


def main() -> None:
    args = build_parser().parse_args()
    run(args.example_option)


if __name__ == "__main__":
    main()
