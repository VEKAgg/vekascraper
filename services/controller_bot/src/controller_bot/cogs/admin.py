from __future__ import annotations

import logging

import discord
import httpx
from controller_bot.config import BotConfig
from discord.ext import commands

logger = logging.getLogger(__name__)

STATE_EMOJI: dict[str, str] = {
    "QUEUED": "\U0001f7e1",
    "RUNNING": "\U0001f7e2",
    "CANCELLING": "\U0001f7e0",
    "COMPLETED": "\u2705",
    "FAILED": "\u274c",
    "CANCELLED": "\u2b1b",
    "CREATED": "\u2b1c",
}


class AdminCog(commands.Cog):
    def __init__(self, bot: commands.Bot, config: BotConfig) -> None:
        self.bot = bot
        self.config = config
        self._client = httpx.AsyncClient(
            base_url=config.export_api_url.rstrip("/"),
            headers={"X-API-Key": config.api_key, "Content-Type": "application/json"},
            timeout=10.0,
        )

    async def cog_unload(self) -> None:
        await self._client.aclose()

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
        resp = await self._client.post(f"/jobs/{endpoint}", json=payload)

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

        resp = await self._client.get("/jobs")

        if resp.is_success:
            data = resp.json()
            jobs = data.get("jobs", [])
            if not jobs:
                await interaction.response.send_message(
                    "No jobs found.", ephemeral=True
                )
                return

            jobs.sort(key=lambda j: j.get("created_at", ""), reverse=True)

            lines = []
            for j in jobs[:15]:
                emoji = STATE_EMOJI.get(j["state"], "")
                lines.append(
                    f"{emoji} `{j['job_id']}` \u2014 {j['type']} \u2014 {j['state']}"
                )
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

        resp = await self._client.post(f"/jobs/{job_id}/cancel")

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
