import json

import numpy as np
import soundfile as sf

from autonomous_mixing.cli import main

SR = 44100


def _stems(tmp_path, bass_sr=SR):
    t = np.arange(2 * SR) / SR
    kick = tmp_path / "kick.wav"
    bass = tmp_path / "bass.wav"
    sf.write(kick, 0.5 * np.sin(2 * np.pi * 60 * t) * np.exp(-8 * (t % 0.5)), SR)
    sf.write(bass, 0.2 * np.sin(2 * np.pi * 55 * np.arange(2 * bass_sr) / bass_sr), bass_sr)
    return kick, bass


def test_analyze_writes_json_report(tmp_path):
    kick, bass = _stems(tmp_path)
    out = tmp_path / "out" / "analysis.json"
    assert main(["analyze", str(kick), str(bass), "--output", str(out)]) == 0
    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["schema_version"] == "m0.1"
    assert report["sample_rate_hz"] == SR
    assert report["duration_seconds"] == 2.0
    for stem in ("kick", "bass"):
        assert len(report[stem]["sha256"]) == 64
        assert report[stem]["peak_dbfs"] <= 0.0
        assert report[stem]["low_band_power_proxy"] > 0.0
    assert 0.0 <= report["temporal_coactivity_fraction"] <= 1.0


def test_analyze_is_deterministic(tmp_path):
    kick, bass = _stems(tmp_path)
    a, b = tmp_path / "a.json", tmp_path / "b.json"
    main(["analyze", str(kick), str(bass), "--output", str(a)])
    main(["analyze", str(kick), str(bass), "--output", str(b)])
    assert a.read_text(encoding="utf-8") == b.read_text(encoding="utf-8")


def test_incompatible_inputs_reported_without_traceback(tmp_path, capsys):
    kick, bass = _stems(tmp_path, bass_sr=48000)
    out = tmp_path / "analysis.json"
    assert main(["analyze", str(kick), str(bass), "--output", str(out)]) == 2
    err = capsys.readouterr().err
    assert err.startswith("error: Stems must share a sample rate")
    assert "Traceback" not in err
    assert not out.exists()


def test_missing_input_reported(tmp_path, capsys):
    kick, _ = _stems(tmp_path)
    assert main(["analyze", str(kick), str(tmp_path / "nope.wav"), "--output", str(tmp_path / "x.json")]) == 2
    assert "not found" in capsys.readouterr().err
