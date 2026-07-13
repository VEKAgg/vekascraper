from __future__ import annotations

import logging

import discord
import httpx
from controller_bot.config import BotConfig
from discord.ext import commands

logger = logging.getLogger(__name__)


def _api_url(config: BotConfig, path: str) -> str:
    return f"{config.export_api_url.rstrip('/')}{path}"


def _headers(config: BotConfig) -> dict[str, str]:
    return {"X-API-Key": config.api_key, "Content-Type": "application/json"}


class AdminCog(commands.Cog):
    def __init__(self, bot: commands.Bot, config: BotConfig) -> None:
        self.bot = bot
        self.config = config

    def _check_admin(self, user_id: int) -> bool:
        return str(user_id) in self.config.admin_user_ids

    async def _post_job(self, interaction: discord.Interaction,
                        endpoint: str, guild_id: str) -> None:
        if not self._check_admin(interaction.user.id):
            await interaction.response.send_message(
                "You are not authorized to run this command.", ephemeral=True
            )
            return

        payload = {"type": endpoint, "guild_id": guild_id}
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                _api_url(self.config, f"/jobs/{endpoint}"),
                json=payload,
                headers=_headers(self.config),
                timeout=10,
            )

        if resp.is_success:
            data = resp.json()
            await interaction.response.send_message(
                f"Job created: `{data['job_id']}`", ephemeral=False
            )
        else:
            detail = resp.json().get("detail", "Unknown error")
            await interaction.response.send_message(
                f"Failed to create job: {detail}", ephemeral=True
            )

    extract = discord.app_commands.Group(
        name="extract", description="Create extraction jobs"
    )

    @extract.command(name="messages", description="Extract messages from a server")
    @discord.app_commands.describe(guild_id="Guild ID to extract from")
    async def extract_messages(
        self, interaction: discord.Interaction, guild_id: str
    ) -> None:
        await self._post_job(interaction, "messages", guild_id)

    @extract_messages.error
    async def extract_messages_error(
        self, interaction: discord.Interaction,
        error: discord.app_commands.AppCommandError
    ) -> None:
        logger.error("extract messages error: %s", error)
        await interaction.response.send_message(
            "An error occurred.", ephemeral=True
        )

    @extract.command(name="members", description="Extract members from a server")
    @discord.app_commands.describe(guild_id="Guild ID to extract from")
    async def extract_members(
        self, interaction: discord.Interaction, guild_id: str
    ) -> None:
        await self._post_job(interaction, "members", guild_id)

    @extract_members.error
    async def extract_members_error(
        self, interaction: discord.Interaction,
        error: discord.app_commands.AppCommandError
    ) -> None:
        logger.error("extract members error: %s", error)
        await interaction.response.send_message(
            "An error occurred.", ephemeral=True
        )

    @extract.command(name="both", description="Extract both messages and members")
    @discord.app_commands.describe(guild_id="Guild ID to extract from")
    async def extract_both(
        self, interaction: discord.Interaction, guild_id: str
    ) -> None:
        await self._post_job(interaction, "both", guild_id)

    @extract_both.error
    async def extract_both_error(
        self, interaction: discord.Interaction,
        error: discord.app_commands.AppCommandError
    ) -> None:
        logger.error("extract both error: %s", error)
        await interaction.response.send_message(
            "An error occurred.", ephemeral=True
        )

    @discord.app_commands.command(
        name="status", description="Check current job status"
    )
    async def status(self, interaction: discord.Interaction) -> None:
        if not self._check_admin(interaction.user.id):
            await interaction.response.send_message(
                "Not authorized.", ephemeral=True
            )
            return

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                _api_url(self.config, "/jobs"),
                headers=_headers(self.config),
                timeout=10,
            )

        if resp.is_success:
            data = resp.json()
            jobs = data.get("jobs", [])
            if not jobs:
                await interaction.response.send_message(
                    "No jobs found.", ephemeral=True
                )
                return

            lines = []
            for j in jobs[:10]:
                lines.append(f"`{j['job_id']}` — {j['type']} — {j['state']}")
            await interaction.response.send_message(
                "\n".join(lines), ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "Failed to fetch status.", ephemeral=True
            )

    @discord.app_commands.command(
        name="cancel", description="Cancel a job by ID"
    )
    @discord.app_commands.describe(
        job_id="Job ID to cancel"
    )
    async def cancel(
        self, interaction: discord.Interaction, job_id: str
    ) -> None:
        if not self._check_admin(interaction.user.id):
            await interaction.response.send_message(
                "Not authorized.", ephemeral=True
            )
            return

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                _api_url(self.config, f"/jobs/{job_id}/cancel"),
                headers=_headers(self.config),
                timeout=10,
            )

        if resp.is_success:
            data = resp.json()
            await interaction.response.send_message(
                f"Job `{data['job_id']}` is now `{data['state']}`.",
                ephemeral=False
            )
        else:
            detail = resp.json().get("detail", "Unknown error")
            await interaction.response.send_message(
                f"Cancel failed: {detail}", ephemeral=True
            )
