#!/usr/bin/env python3
"""
LMS Telegram Bot — Entry point.
ijgghg
Supports two modes:ikjggk
1. --test mode: Run handlers directly without Telegram (for development/testing)
2. Bot mode: Connect to Telegram and handle messages via aiogram

Usage:
    uv run bot.py --test "/start"           # Test mode - slash command
    uv run bot.py --test "hello"            # Test mode - natural language
    uv run bot.py    iasdgasdf                       # Bot mode (requires BOT_TOKEN)
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Ensure bot/ directory is in path for imports
sys.path.insert(0, str(Path(__file__).parent))

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from config import settings
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


async def run_bot_mode() -> None:
    """Run the Telegram bot using aiogram.

    This connects to Telegram and handles messages via the same handlers
    used in --test mode.
    """
    if not settings.bot_token:
        print("Error: BOT_TOKEN is required for bot mode.")
        print("Set BOT_TOKEN in .env.bot.secret or .env.docker.secret")
        sys.exit(1)

    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Create bot and dispatcher
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    # Create keyboard buttons for common actions
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="/start"), KeyboardButton(text="/help")],
            [KeyboardButton(text="/health"), KeyboardButton(text="/labs")],
        ],
        resize_keyboard=True,
    )

    # /start handler
    @dp.message(CommandStart())
    async def start_handler(message: types.Message) -> None:
        response = handle_start()
        await message.answer(response, reply_markup=keyboard)

    # /help handler
    @dp.message(Command("help"))
    async def help_handler(message: types.Message) -> None:
        response = handle_help()
        await message.answer(response, reply_markup=keyboard)

    # /health handler
    @dp.message(Command("health"))
    async def health_handler(message: types.Message) -> None:
        response = handle_health()
        await message.answer(response, reply_markup=keyboard)

    # /labs handler
    @dp.message(Command("labs"))
    async def labs_handler(message: types.Message) -> None:
        response = handle_labs()
        await message.answer(response, reply_markup=keyboard)

    # /scores handler
    @dp.message(Command("scores"))
    async def scores_handler(message: types.Message) -> None:
        # Extract argument after /scores
        args = message.text.split(maxsplit=1)
        lab = args[1] if len(args) > 1 else None
        response = handle_scores(lab)
        await message.answer(response, reply_markup=keyboard)

    # Natural language handler (for non-command messages)
    @dp.message()
    async def natural_language_handler(message: types.Message) -> None:
        text = message.text or ""
        if text.startswith("/"):
            # Already handled by command handlers
            return
        response = route_intent(text, debug=False)
        await message.answer(response, reply_markup=keyboard)

    # Start polling
    print("Application started")
    await dp.start_polling(bot)


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
        # Bot mode: connect to Telegram
        asyncio.run(run_bot_mode())


if __name__ == "__main__":
    main()
