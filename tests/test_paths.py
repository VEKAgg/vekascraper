from pathlib import Path

from shared.storage.paths import DataPaths, ensure_dirs, get_data_root


def test_get_data_root_default(monkeypatch: object) -> None:
    monkeypatch.delenv("DATA_ROOT", raising=False)  # type: ignore[attr-defined]
    result = get_data_root()
    assert result == Path("/data").resolve()


def test_get_data_root_from_env(monkeypatch: object) -> None:
    monkeypatch.setenv("DATA_ROOT", "/custom")  # type: ignore[attr-defined]
    result = get_data_root()
    assert result == Path("/custom").resolve()


def test_ensure_dirs_creates_all_subdirs(tmp_path: Path) -> None:
    paths = ensure_dirs(tmp_path)
    assert paths.jobs.is_dir()
    assert paths.logs.is_dir()
    assert paths.manifests.is_dir()
    assert paths.exports_messages.is_dir()
    assert paths.exports_members.is_dir()
    assert paths.temp.is_dir()


def test_ensure_dirs_returns_data_paths(tmp_path: Path) -> None:
    paths = ensure_dirs(tmp_path)
    assert isinstance(paths, DataPaths)
    assert paths.root == tmp_path


def test_ensure_dirs_idempotent(tmp_path: Path) -> None:
    ensure_dirs(tmp_path)
    ensure_dirs(tmp_path)


def test_data_paths_fields_are_paths(tmp_path: Path) -> None:
    paths = ensure_dirs(tmp_path)
    assert isinstance(paths.jobs, Path)
    assert isinstance(paths.logs, Path)
    assert isinstance(paths.manifests, Path)
    assert isinstance(paths.exports_messages, Path)
    assert isinstance(paths.exports_members, Path)
    assert isinstance(paths.temp, Path)
