#!/usr/bin/env python3
"""
LMS Telegram Bot — Entry point.

Supports two modes:
1. --test mode: Run handlers directly without Telegram (for development/testing)
2. Bot mode: Connect to Telegram and handle messages via aiogram

Usage:
    uv run bot.py --test "/start"           # Test mode - slash command
    uv run bot.py --test "s``hello"            # Test mode - natural language
    uv run bot.py                           # Bot mode (requires BOT_TOKEN)
"""
import argparse
import logging
import sys
from pathlib import Path

# Ensure bot/ directory is in path for imports
sys.path.insert(0, str(Path(__file__).parent))

from handlers import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
    route_intent,
)
from handlers.keyboards import get_start_keyboard, get_help_keyboard, keyboard_to_telegram_format
from config import settings

# Import aiogram only when needed (not used in test mode)
aiogram = None
InlineKeyboardMarkup = None

try:
    from aiogram import Bot, Dispatcher, types
    from aiogram.filters import Command
    from aiogram.types import InlineKeyboardMarkup
    aiogram_available = True
except ImportError:
    aiogram_available = False


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


async def bot_mode() -> None:
    """Run the bot in Telegram mode — connect and handle messages."""
    if not aiogram_available:
        logging.error("aiogram is not installed. Install with: uv add aiogram")
        sys.exit(1)

    if not settings.bot_token:
        logging.error("BOT_TOKEN is not set. Please set it in .env.bot.secret or environment.")
        sys.exit(1)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Initialize bot and dispatcher
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    # --- Slash command handlers ---

    @dp.message(Command("start"))
    async def cmd_start(message: types.Message):
        """Handle /start command."""
        response = handle_start()
        keyboard = keyboard_to_telegram_format(get_start_keyboard())
        await message.answer(response, reply_markup=keyboard)

    @dp.message(Command("help"))
    async def cmd_help(message: types.Message):
        """Handle /help command."""
        response = handle_help()
        keyboard = keyboard_to_telegram_format(get_help_keyboard())
        await message.answer(response, reply_markup=keyboard)

    @dp.message(Command("health"))
    async def cmd_health(message: types.Message):
        """Handle /health command."""
        response = handle_health()
        await message.answer(response)

    @dp.message(Command("labs"))
    async def cmd_labs(message: types.Message):
        """Handle /labs command."""
        response = handle_labs()
        await message.answer(response)

    @dp.message(Command("scores"))
    async def cmd_scores(message: types.Message):
        """Handle /scores command."""
        # Get the lab argument from the command
        args = message.text.split(maxsplit=1)
        lab = args[1] if len(args) > 1 else None
        response = handle_scores(lab)
        await message.answer(response)

    # --- Natural language message handler ---

    @dp.message()
    async def handle_message(message: types.Message):
        """Handle all other messages (natural language queries)."""
        user_text = message.text or ""

        if not user_text.strip():
            return

        # Use intent router for natural language
        # Note: debug output goes to stderr, won't appear in Telegram
        response = route_intent(user_text, debug=False)

        await message.answer(response)

    # Start polling
    logging.info("Bot is starting...")
    logging.info(f"Bot username: {(await bot.get_me()).username}")
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
        import asyncio
        asyncio.run(bot_mode())


if __name__ == "__main__":
    main()
