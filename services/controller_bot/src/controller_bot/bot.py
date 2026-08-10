from __future__ import annotations

import logging

import discord
from controller_bot.cogs.admin import AdminCog
from controller_bot.config import BotConfig
from discord.ext import commands

logger = logging.getLogger(__name__)


def run_bot() -> None:
    config = BotConfig.from_env()

    if not config.admin_user_ids:
        logger.warning("ADMIN_DISCORD_USER_IDS is empty — no one can run bot commands!")

    intents = discord.Intents.default()
    intents.message_content = False

    bot = commands.Bot(command_prefix=None, intents=intents)

    @bot.event
    async def on_ready() -> None:
        logger.info("Bot logged in as %s (ID: %s)", bot.user, bot.user.id)
        await bot.tree.sync()

    bot.add_cog(AdminCog(bot, config))

    bot.run(config.discord_token)
