"""End-to-end test: makes sure `python run.py` actually works, using a
temporary database so it never touches real project data.
"""

from app.main import run


def test_run_once_completes_successfully(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "test_run.db"))
    monkeypatch.setenv("DRY_RUN", "true")

    exit_code = run(["--dry-run", "--once"])

    assert exit_code == 0
    assert (tmp_path / "test_run.db").exists()


def test_run_demo_mode_completes_successfully(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "test_run_demo.db"))

    exit_code = run(["--dry-run", "--demo", "--once"])

    assert exit_code == 0
