import re
import time

import pytest

from cliasi import Cliasi, cli
from cliasi import SYMBOLS, __version__, TextColor


ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


def normalize_output(s: str) -> str:
    # Remove ANSI codes and carriage/clear sequences, collapse spaces
    s = ANSI_RE.sub("", s)
    s = s.replace("\r", "").replace("\n", "\n").replace("\x1b[2K", "")
    return s.strip()


@pytest.fixture()
def fixed_width(monkeypatch):
    # Make terminal size deterministic for progress bar tests
    from cliasi import cliasi as cliasi_module

    monkeypatch.setattr(cliasi_module, "_terminal_size", lambda: 40)
    yield


def test_basic_messages_symbols_and_message(capsys):
    c = Cliasi("TEST", messages_stay_in_one_line=False, colors=False)

    c.info("hello")
    out = normalize_output(capsys.readouterr().out)
    assert out.startswith("i [TEST]")
    assert "| hello" in out

    c.warn("be careful")
    out = normalize_output(capsys.readouterr().out)
    assert out.startswith("! [TEST]")
    assert "| be careful" in out

    c.success("ok")
    out = normalize_output(capsys.readouterr().out)
    assert out.startswith("✔ [TEST]")
    assert "| ok" in out

    c.fail("nope")
    out = normalize_output(capsys.readouterr().out)
    assert out.startswith("X [TEST]")
    assert "| nope" in out

    c.log("logged")
    out = normalize_output(capsys.readouterr().out)
    assert out.startswith("LOG [TEST]")
    assert "| logged" in out

    c.log_small("tiny")
    out = normalize_output(capsys.readouterr().out)
    assert out.startswith("L [TEST]")
    assert "| tiny" in out

    c.message("meh")
    out = normalize_output(capsys.readouterr().out)
    assert out.startswith("# [TEST]")
    assert "| meh" in out

    c.list("entry")
    out = normalize_output(capsys.readouterr().out)
    assert out.startswith("- [TEST]")
    assert "| entry" in out


def test_update_prefix_and_separator(capsys):
    c = Cliasi("OLD", messages_stay_in_one_line=False, colors=False, seperator="|")
    c.update_prefix("NEW")
    c.info("msg")
    out = normalize_output(capsys.readouterr().out)
    assert out.startswith("i [NEW]")
    assert "| msg" in out

    c.prefix_seperator = "::"
    c.info("again")
    out = normalize_output(capsys.readouterr().out)
    assert ":: again" in out


def test_verbosity_filters(capsys):
    c = Cliasi("V", messages_stay_in_one_line=False, colors=False, min_verbose_level=1)
    # According to current implementation, level > min is suppressed
    # lower or equal -> shown
    c.info("visible", verbosity=0)
    out = normalize_output(capsys.readouterr().out)
    assert "visible" in out
    # higher than min -> suppressed
    c.info("hidden", verbosity=2)
    out = capsys.readouterr().out
    assert out == ""


def test_override_messages_stay_in_one_line_prints_no_newline(capsys):
    c = Cliasi("OL", messages_stay_in_one_line=False, colors=False)
    c.info("same line", override_messages_stay_in_one_line=True)
    captured = capsys.readouterr()
    # Should not end with a newline because oneline keeps it on the same line
    assert not captured.out.endswith("\n")


def test_progressbar_static(fixed_width, capsys):
    c = Cliasi("PB", messages_stay_in_one_line=False, colors=False)
    c.progressbar("Working", progress=50, override_messages_stay_in_one_line=False, show_percent=True)
    out = normalize_output(capsys.readouterr().out)
    assert "[" in out and "]" in out
    assert "50%" in out

    c.progressbar_download("Downloading", progress=10, show_percent=False)
    out = normalize_output(capsys.readouterr().out)
    assert "[" in out and "]" in out


def test_non_blocking_animation_starts_and_stops(capsys):
    c = Cliasi("AN", messages_stay_in_one_line=True, colors=False)
    task = c.animate_message_non_blocking("Wait", interval=0.01)
    time.sleep(0.03)
    task.stop()
    out = normalize_output(capsys.readouterr().out)
    # At least one animation frame or the trailing newline from stop()
    assert "[" in out or "Wait" in out or out != ""


def test_non_blocking_progressbar_update_and_stop(fixed_width, capsys):
    c = Cliasi("APB", messages_stay_in_one_line=True, colors=False)
    task = c.progressbar_animated_normal("Doing", progress=0, interval=0.01, show_percent=True)
    time.sleep(0.02)
    task.update(progress=25)
    time.sleep(0.02)
    task.stop()
    out = normalize_output(capsys.readouterr().out)
    assert "Doing" in out or "25%" in out or "[" in out


def test_newline_prints_single_newline(capsys):
    c = Cliasi("NL", messages_stay_in_one_line=False, colors=False)
    c.newline()
    captured = capsys.readouterr().out
    # newline should just print a single newline
    assert captured == "\n"


def test_ask_visible_and_hidden(monkeypatch, capsys):
    # Patch input and getpass within module
    from cliasi import cliasi as cliasi_module

    monkeypatch.setattr("builtins.input", lambda prompt="": "visible_answer")
    c = Cliasi("ASK", messages_stay_in_one_line=True, colors=False)
    res = c.ask("Question? ", hide_input=False)
    # Output of the prompt likely contains '? [ASK]' and message
    out1 = capsys.readouterr().out
    assert res == "visible_answer"
    assert "? [" in normalize_output(out1)

    # Hidden input path
    monkeypatch.setattr(cliasi_module, "getpass", lambda prompt="": "secret_answer")
    res2 = c.ask("Hidden? ", hide_input=True)
    out2 = capsys.readouterr().out
    assert res2 == "secret_answer"
    # We at least printed something for the prompt
    assert "? [" in normalize_output(out2)


def test_animate_message_blocking_emits_output(capsys):
    c = Cliasi("BLK", messages_stay_in_one_line=True, colors=False)
    c.animate_message_blocking("Hold on", time=0.05, interval=0.01)
    out = normalize_output(capsys.readouterr().out)
    assert out != ""


def test_non_blocking_download_animation_starts_and_stops(capsys):
    c = Cliasi("DL", messages_stay_in_one_line=True, colors=False)
    task = c.animate_message_download_non_blocking("Download", interval=0.01)
    time.sleep(0.03)
    task.stop()
    out = normalize_output(capsys.readouterr().out)
    assert "Download" in out or "[" in out or out != ""


def test_progressbar_animated_download_update_and_stop(fixed_width, capsys):
    c = Cliasi("APBDL", messages_stay_in_one_line=True, colors=False)
    task = c.progressbar_animated_download(
        "Getting", progress=5, interval=0.01, show_percent=True
    )
    time.sleep(0.02)
    task.update(progress=15)
    time.sleep(0.02)
    task.stop()
    out = normalize_output(capsys.readouterr().out)
    assert "Getting" in out or "15%" in out or "[" in out


def test_default_cli_instance_is_usable(capsys):
    # Using the shared instance exported as `cli`
    cli.info("shared works")
    out = normalize_output(capsys.readouterr().out)
    assert "shared works" in out


def test_symbols_and_version_present():
    # Basic sanity checks for package exports from __init__
    assert isinstance(SYMBOLS, dict)
    # The package declares at least these two symbols
    assert SYMBOLS.get("success") == "✔"
    assert SYMBOLS.get("download") == "⤓"
    # Version string exists and looks like semantic version
    assert isinstance(__version__, str)
    assert __version__.count(".") >= 1


def test_textcolor_contains_expected_members():
    # Ensure TextColor enum exposes some basic colors and control codes
    names = {e.name for e in TextColor}
    assert {"RESET", "DIM", "RED", "GREEN", "YELLOW"}.issubset(names)
