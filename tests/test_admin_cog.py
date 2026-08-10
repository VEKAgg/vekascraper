from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from controller_bot.cogs.admin import STATE_EMOJI, AdminCog
from controller_bot.config import BotConfig


@pytest.fixture
def config() -> BotConfig:
    return BotConfig(
        discord_token="bot-token",
        admin_user_ids=["111", "222"],
        export_api_url="http://localhost:8080",
        api_key="test-key",
    )


@pytest.fixture
def empty_config() -> BotConfig:
    return BotConfig(
        discord_token="bot-token",
        admin_user_ids=[],
        export_api_url="http://localhost:8080",
        api_key="test-key",
    )


@pytest.fixture
def cog(config: BotConfig) -> AdminCog:
    bot = MagicMock()
    return AdminCog(bot, config)


def _mock_interaction(user_id: int = 111) -> MagicMock:
    interaction = MagicMock()
    interaction.user.id = user_id
    interaction.response = AsyncMock()
    return interaction


class TestCheckAdmin:
    def test_authorized(self, cog: AdminCog) -> None:
        assert cog._check_admin(111) is True

    def test_unauthorized(self, cog: AdminCog) -> None:
        assert cog._check_admin(99999) is False

    def test_empty_list(self, empty_config: BotConfig) -> None:
        cog = AdminCog(MagicMock(), empty_config)
        assert cog._check_admin(111) is False


class TestPostJob:
    @pytest.mark.asyncio
    async def test_unauthorized(self, cog: AdminCog) -> None:
        interaction = _mock_interaction(user_id=99999)
        await cog._post_job(interaction, "messages", "g1")
        interaction.response.send_message.assert_called_once()
        call_args = interaction.response.send_message.call_args
        assert "not authorized" in call_args[0][0].lower()

    @pytest.mark.asyncio
    async def test_success(self, cog: AdminCog) -> None:
        interaction = _mock_interaction()
        mock_resp = MagicMock()
        mock_resp.is_success = True
        mock_resp.json.return_value = {"job_id": "JOB-123"}
        cog._client = AsyncMock()
        cog._client.post = AsyncMock(return_value=mock_resp)
        await cog._post_job(interaction, "messages", "g1")
        interaction.response.send_message.assert_called_once()
        call_args = interaction.response.send_message.call_args
        assert "JOB-123" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_api_error(self, cog: AdminCog) -> None:
        interaction = _mock_interaction()
        mock_resp = MagicMock()
        mock_resp.is_success = False
        mock_resp.json.return_value = {"detail": "Active job exists"}
        cog._client = AsyncMock()
        cog._client.post = AsyncMock(return_value=mock_resp)
        await cog._post_job(interaction, "messages", "g1")
        call_args = interaction.response.send_message.call_args
        assert "Active job exists" in call_args[0][0]


def _get_callback(cog: AdminCog, name: str):
    """Get the underlying callback from a discord.py Command decorator."""
    attr = getattr(cog, name)
    if hasattr(attr, "callback"):
        return attr.callback
    return attr


class TestStatus:
    @pytest.mark.asyncio
    async def test_unauthorized(self, cog: AdminCog) -> None:
        interaction = _mock_interaction(user_id=99999)
        cb = _get_callback(cog, "status")
        await cb(cog, interaction)
        interaction.response.send_message.assert_called_once()
        call_args = interaction.response.send_message.call_args
        assert "not authorized" in call_args[0][0].lower()

    @pytest.mark.asyncio
    async def test_no_jobs(self, cog: AdminCog) -> None:
        interaction = _mock_interaction()
        mock_resp = MagicMock()
        mock_resp.is_success = True
        mock_resp.json.return_value = {"jobs": []}
        cog._client = AsyncMock()
        cog._client.get = AsyncMock(return_value=mock_resp)
        cb = _get_callback(cog, "status")
        await cb(cog, interaction)
        call_args = interaction.response.send_message.call_args
        assert "no jobs" in call_args[0][0].lower()

    @pytest.mark.asyncio
    async def test_shows_jobs(self, cog: AdminCog) -> None:
        interaction = _mock_interaction()
        mock_resp = MagicMock()
        mock_resp.is_success = True
        mock_resp.json.return_value = {"jobs": [
            {"job_id": "JOB-001", "type": "messages",
             "state": "QUEUED", "created_at": "2026-01-01"},
        ]}
        cog._client = AsyncMock()
        cog._client.get = AsyncMock(return_value=mock_resp)
        cb = _get_callback(cog, "status")
        await cb(cog, interaction)
        call_args = interaction.response.send_message.call_args
        text = call_args[0][0]
        assert "JOB-001" in text
        assert STATE_EMOJI["QUEUED"] in text

    @pytest.mark.asyncio
    async def test_capped_at_15(self, cog: AdminCog) -> None:
        interaction = _mock_interaction()
        jobs = [
            {"job_id": f"JOB-{i:03d}", "type": "messages",
             "state": "QUEUED", "created_at": str(i)}
            for i in range(20)
        ]
        mock_resp = MagicMock()
        mock_resp.is_success = True
        mock_resp.json.return_value = {"jobs": jobs}
        cog._client = AsyncMock()
        cog._client.get = AsyncMock(return_value=mock_resp)
        cb = _get_callback(cog, "status")
        await cb(cog, interaction)
        call_args = interaction.response.send_message.call_args
        text = call_args[0][0]
        assert text.count("JOB-") == 15

    @pytest.mark.asyncio
    async def test_api_failure(self, cog: AdminCog) -> None:
        interaction = _mock_interaction()
        mock_resp = MagicMock()
        mock_resp.is_success = False
        cog._client = AsyncMock()
        cog._client.get = AsyncMock(return_value=mock_resp)
        cb = _get_callback(cog, "status")
        await cb(cog, interaction)
        call_args = interaction.response.send_message.call_args
        assert "failed" in call_args[0][0].lower()


class TestCancel:
    @pytest.mark.asyncio
    async def test_unauthorized(self, cog: AdminCog) -> None:
        interaction = _mock_interaction(user_id=99999)
        cb = _get_callback(cog, "cancel")
        await cb(cog, interaction, "JOB-123")
        interaction.response.send_message.assert_called_once()
        call_args = interaction.response.send_message.call_args
        assert "not authorized" in call_args[0][0].lower()

    @pytest.mark.asyncio
    async def test_success(self, cog: AdminCog) -> None:
        interaction = _mock_interaction()
        mock_resp = MagicMock()
        mock_resp.is_success = True
        mock_resp.json.return_value = {"job_id": "JOB-123", "state": "CANCELLED"}
        cog._client = AsyncMock()
        cog._client.post = AsyncMock(return_value=mock_resp)
        cb = _get_callback(cog, "cancel")
        await cb(cog, interaction, "JOB-123")
        call_args = interaction.response.send_message.call_args
        assert "CANCELLED" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_api_failure(self, cog: AdminCog) -> None:
        interaction = _mock_interaction()
        mock_resp = MagicMock()
        mock_resp.is_success = False
        mock_resp.json.return_value = {"detail": "Not found"}
        cog._client = AsyncMock()
        cog._client.post = AsyncMock(return_value=mock_resp)
        cb = _get_callback(cog, "cancel")
        await cb(cog, interaction, "JOB-123")
        call_args = interaction.response.send_message.call_args
        assert "Not found" in call_args[0][0]


class TestCogUnload:
    @pytest.mark.asyncio
    async def test_closes_client(self, cog: AdminCog) -> None:
        cog._client = AsyncMock()
        await cog.cog_unload()
        cog._client.aclose.assert_called_once()


class TestExtractCommands:
    @pytest.mark.asyncio
    async def test_extract_messages_delegates(self, cog: AdminCog) -> None:
        interaction = _mock_interaction()
        with patch.object(cog, "_post_job", new_callable=AsyncMock) as mock_post:
            cb = _get_callback(cog, "extract_messages")
            await cb(cog, interaction, "g1")
            mock_post.assert_called_once_with(interaction, "messages", "g1")

    @pytest.mark.asyncio
    async def test_extract_members_delegates(self, cog: AdminCog) -> None:
        interaction = _mock_interaction()
        with patch.object(cog, "_post_job", new_callable=AsyncMock) as mock_post:
            cb = _get_callback(cog, "extract_members")
            await cb(cog, interaction, "g1")
            mock_post.assert_called_once_with(interaction, "members", "g1")

    @pytest.mark.asyncio
    async def test_extract_both_delegates(self, cog: AdminCog) -> None:
        interaction = _mock_interaction()
        with patch.object(cog, "_post_job", new_callable=AsyncMock) as mock_post:
            cb = _get_callback(cog, "extract_both")
            await cb(cog, interaction, "g1")
            mock_post.assert_called_once_with(interaction, "both", "g1")
