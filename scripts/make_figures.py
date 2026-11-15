"""Report figures. Every number is copied from the run logs in logs/
(01_misread.log, 03_judge_probe.log); nothing is recomputed here.

    python scripts/make_figures.py
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parents[1] / "docs" / "figures"
OUT.mkdir(parents=True, exist_ok=True)
LANGS = ["English", "Hausa", "Igbo", "Yoruba"]
INK, MUTED, ACCENT, LIGHT = "#2b2b2b", "#8a8178", "#2f5d8a", "#c9d6e3"

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
                     "xtick.color": INK, "ytick.color": INK})

# Figure 1: benign prompts, base answers (01_misread.log) vs clarify answers (03_judge_probe.log)
base = {"missed": [0, 8, 17, 28], "partly": [9, 35, 41, 41], "signal": [0, 0, 1, 0]}
clar = {"missed": [0, 16, 19, 26], "partly": [6, 36, 51, 54], "signal": [10, 9, 7, 5]}

fig, axes = plt.subplots(1, 2, figsize=(9, 3.4), sharey=True)
w = 0.38
x = range(len(LANGS))
for ax, data, title in ((axes[0], base, "Plain prompt (Isoglot's answers)"),
                        (axes[1], clar, "With \"ask if you're unsure\"")):
    ax.bar([i - w / 2 for i in x], data["missed"], w, color=ACCENT, label="Missed the request")
    ax.bar([i - w / 2 for i in x], data["partly"], w, bottom=data["missed"], color=LIGHT,
           label="Missed part of it")
    ax.bar([i + w / 2 for i in x], data["signal"], w, color=MUTED, label="Said it might have misunderstood")
    ax.set_xticks(list(x), LANGS)
    ax.set_title(title, fontsize=10, color=INK)
    ax.set_ylim(0, 85)
axes[0].set_ylabel("% of 100 benign prompts")
axes[1].legend(frameon=False, fontsize=8, loc="upper left")
fig.tight_layout()
fig.savefig(OUT / "fig1_misreadings.png", dpi=200)

# Figure 2: restatement probe (03_judge_probe.log), benign and harmful sets
understood = {"benign": [99.0, 59.5, 52.3, 20.0], "harmful": [100.0, 48.0, 48.8, 16.9]}
conf_wrong = {"benign": [1.0, 40.5, 47.7, 80.0], "harmful": [0.0, 52.0, 51.2, 83.1]}
echoed = [3, 39, 111, 63]   # of 200 prompts per language (eng, hau, ibo, yor)

fig, axes = plt.subplots(1, 2, figsize=(9, 3.4))
ax = axes[0]
ax.bar([i - w / 2 for i in x], understood["benign"], w, color=ACCENT, label="Benign")
ax.bar([i + w / 2 for i in x], understood["harmful"], w, color=LIGHT, label="Harmful")
ax.axhline(97.5, color=MUTED, ls="--", lw=1)
ax.text(3.45, 99, "mean stated confidence ≈ 97-99", ha="right", fontsize=8, color=MUTED)
ax.set_xticks(list(x), LANGS)
ax.set_ylim(0, 110)
ax.set_ylabel("% of restatements that match the request")
ax.set_title("Restatement correct vs. stated confidence", fontsize=10, color=INK)
ax.legend(frameon=False, fontsize=8, loc="center right", bbox_to_anchor=(1.0, 0.62))

ax = axes[1]
ax.bar([i - w / 2 for i in x], conf_wrong["benign"], w, color=ACCENT, label="Wrong at ≥80 confidence, benign")
ax.bar([i + w / 2 for i in x], conf_wrong["harmful"], w, color=LIGHT, label="Wrong at ≥80 confidence, harmful")
ax.plot(list(x), [100 * e / 200 for e in echoed], "o-", color=MUTED, label="Restated our instruction instead")
ax.set_xticks(list(x), LANGS)
ax.set_ylim(0, 100)
ax.set_ylabel("%")
ax.set_title("Confidently wrong, and instruction echoes", fontsize=10, color=INK)
ax.legend(frameon=False, fontsize=8, loc="upper left")
fig.tight_layout()
fig.savefig(OUT / "fig2_restatement.png", dpi=200)
print("wrote", *sorted(p.name for p in OUT.glob("*.png")))
