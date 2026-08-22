import pytest

from app.services import git_mining
from tests.conftest_git import build_risky_repo


@pytest.mark.asyncio
async def test_mine_file_metrics_on_real_crafted_history(tmp_path):
    repo = build_risky_repo(tmp_path)
    metrics = await git_mining.mine_file_metrics(repo)

    assert "src/risky.js" in metrics
    assert "src/stable.js" in metrics

    risky = metrics["src/risky.js"]
    stable = metrics["src/stable.js"]

    assert risky.change_frequency == 4
    assert risky.bug_fix_commits == 2
    assert risky.bug_fix_ratio == 0.5
    assert len(risky.authors) == 2

    assert stable.change_frequency == 1
    assert stable.bug_fix_commits == 0
    assert len(stable.authors) == 1


@pytest.mark.asyncio
async def test_get_recent_commits_real_order_and_files(tmp_path):
    repo = build_risky_repo(tmp_path)
    commits = await git_mining.get_recent_commits(repo, limit=10)

    assert len(commits) == 4
    assert commits[0].message == "feat: extend risky with extra helper"
    assert "src/risky.js" in commits[0].files


@pytest.mark.asyncio
async def test_get_commit_diff_returns_real_diff(tmp_path):
    repo = build_risky_repo(tmp_path)
    commits = await git_mining.get_recent_commits(repo, limit=10)
    diff = await git_mining.get_commit_diff(repo, commits[0].sha)
    assert "extra" in diff


@pytest.mark.asyncio
async def test_is_git_repo(tmp_path):
    repo = build_risky_repo(tmp_path)
    assert await git_mining.is_git_repo(repo) is True

    not_a_repo = tmp_path / "not_a_repo"
    not_a_repo.mkdir()
    assert await git_mining.is_git_repo(not_a_repo) is False
