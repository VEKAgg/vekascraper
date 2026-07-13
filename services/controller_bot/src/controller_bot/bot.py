from __future__ import annotations

import logging

import discord
from discord.ext import commands

from controller_bot.config import BotConfig
from controller_bot.cogs.admin import AdminCog

logger = logging.getLogger(__name__)


def run_bot() -> None:
    config = BotConfig.from_env()

    intents = discord.Intents.default()
    intents.message_content = False

    bot = commands.Bot(command_prefix=None, intents=intents)

    @bot.event
    async def on_ready() -> None:
        logger.info("Bot logged in as %s (ID: %s)", bot.user, bot.user.id)
        await bot.tree.sync()

    bot.add_cog(AdminCog(bot, config))

    if config.discord_token:
        bot.run(config.discord_token)
    else:
        logger.error("DISCORD_BOT_TOKEN is not set")
