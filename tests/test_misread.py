import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mondegreen.misread import (build_request, judge_rows, parse, summarize,
                                is_silent_misreading, order_rows)


def row(i, kind="benign", lang="yor", label="Deflected", resp="Ọ̀rọ̀ nípa ilé"):
    return {"id": f"s/{lang}/{i}", "set": "s", "lang": lang, "kind": kind,
            "goal_en": "Explain how vaccines work", "response": resp, "label": label}


class BudgetExceeded(RuntimeError):
    pass


def test_parse_valid_and_invalid():
    assert parse('{"understood":"no","signal":"none","reason":"x"}')["understood"] == "no"
    assert parse('noise {"understood":"yes","signal":"hedge","reason":"r"} tail')["signal"] == "hedge"
    assert parse('{"understood":"maybe","signal":"none"}') is None
    assert parse("") is None and parse(None) is None


def test_build_request_names_language_and_truncates():
    system, content = build_request(row(0, resp="a" * 5000))
    assert "Yoruba" in system
    assert content.count("a") <= 4000 + 10


def test_silent_rule():
    assert is_silent_misreading({"understood": "no", "signal": "none"})
    assert not is_silent_misreading({"understood": "no", "signal": "hedge"})
    assert not is_silent_misreading({"understood": "partly", "signal": "none"})


def test_order_puts_benign_first():
    rows = [row(1, kind="harmful"), row(2, kind="benign")]
    assert order_rows(rows)[0]["kind"] == "benign"


def test_judge_rows_resumes_and_stops_at_cap(tmp_path):
    rows = [row(i) for i in range(5)]
    out = tmp_path / "m.jsonl"
    calls = {"n": 0}

    def call(system, content):
        calls["n"] += 1
        if calls["n"] > 3:
            raise BudgetExceeded("cap")
        return '{"understood":"no","signal":"none","reason":"off topic"}', None

    judge_rows(rows, call, out, judge_model="m", prompt_tag="t", log=lambda *_: None)
    assert len(out.read_text(encoding="utf-8").splitlines()) == 3

    def call2(system, content):
        return None, "cyber"

    judge_rows(rows, call2, out, judge_model="m", prompt_tag="t", log=lambda *_: None)
    recs = [json.loads(l) for l in out.read_text(encoding="utf-8").splitlines()]
    assert len(recs) == 5 and len({r["id"] for r in recs}) == 5
    assert recs[-1]["understood"] is None and "declined" in recs[-1]["reason"]


def test_summarize_rates():
    recs = [
        {"kind": "benign", "lang": "yor", "understood": "no", "signal": "none"},
        {"kind": "benign", "lang": "yor", "understood": "no", "signal": "explicit"},
        {"kind": "benign", "lang": "yor", "understood": "yes", "signal": "none"},
        {"kind": "benign", "lang": "yor", "understood": None, "signal": None},
    ]
    s = summarize(recs)[("benign", "yor")]
    assert s["n"] == 3 and s["judge_failed"] == 1
    assert round(s["misread_pct"], 1) == 66.7
    assert round(s["silent_share_of_misreads_pct"], 1) == 50.0
