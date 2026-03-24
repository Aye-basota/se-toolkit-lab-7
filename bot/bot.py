#!/usr/bin/env python3
"""
LMS Telegram Bot — Entry point.

Supports two modes:
1. --test mode: Run handlers directly without Telegram (for development/testing)
2. Bot mode: Connect to Telegram and handle messages via aiogram

Usage:
    uv run bot.py --test "/start"           # Test mode - slash command
    uv run bot.py --test "hello"            # Test mode - natural language
    uv run bot.py                           # Bot mode (requires BOT_TOKEN)
"""
import argparse
import sys
from pathlib import Path
# Ensure bot/ directory is in path for importasdfafs
sys.path.insert(0, str(Path(__file__).parent))

from handlers import handle_start, handle_help, handle_health, handle_labs, handle_scores
from handlers.intent_router import route as route_intent


def parse_command(text: str) -> tuple[str, str | None]:
    """Parse a command string into (command, argument).
    
    Examples:
        "/start" → ("/start", None)
        "/scores lab-04" → ("/scores", "lab-04")
        "hello" → ("hello", None)
    """
    parts = text.strip().split(maxsplit=1)
    if not parts:
        return ("", None)
    command = parts[0].lower()
    argument = parts[1] if len(parts) > 1 else None
    return (command, argument)


def run_test_mode(command_text: str) -> None:
    """Run a command in test mode — call handler directly, print result.
    
    This allows testing without Telegram. The same handlers are called
    from both --test mode and the Telegram bot.
    """
    command, argument = parse_command(command_text)
    
    # Check if it's a slash command
    if command.startswith("/"):
        # Route to appropriate handler
        if command == "/start":
            response = handle_start()
        elif command == "/help":
            response = handle_help()
        elif command == "/health":
            response = handle_health()
        elif command == "/labs":
            response = handle_labs()
        elif command == "/scores":
            response = handle_scores(argument)
        else:
            response = f"Unknown command: {command}. Use /help to see available commands."
    else:
        # Natural language query — use intent router
        # Debug mode prints to stderr so it doesn't mix with stdout response
        response = route_intent(command_text, debug=True)
    
    # Print response to stdout (exit code 0)
    print(response)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="LMS Telegram Bot")
    parser.add_argument(
        "--test",
        type=str,
        metavar="COMMAND",
        help="Run in test mode with the given command (e.g., --test '/start' or --test 'hello')",
    )
    
    args = parser.parse_args()
    
    if args.test:
        # Test mode: call handler directly, print result, exit
        run_test_mode(args.test)
        sys.exit(0)
    else:
        # Bot mode: connect to Telegram (TODO: implement)
        print("Bot mode not implemented yet. Use --test mode for testing.")
        print("Example: uv run bot.py --test '/start'")
        print("Example: uv run bot.py --test 'what labs are available'")
        sys.exit(1)


if __name__ == "__main__":
    main()
