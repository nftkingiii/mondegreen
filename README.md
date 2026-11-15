# Mondegreen

Does a small multilingual model tell you when it has misread your request?

Built for the Apart Research **AI x Epistemics Research Sprint** (13-15 November 2026),
Track 1: Model Epistemics & Decision-Making Evals.

## Question

Earlier work (Isoglot, below) found that Cohere Labs' Tiny Aya refuses far fewer harmful
requests in Hausa, Yoruba and Igbo than in English, and that the lost refusals are mostly
*deflections*: fluent answers about something other than what was asked. A user who can't
read English can't tell such an answer is off-topic. Mondegreen asks the epistemic question
behind that:

1. **Silent misreadings.** How often does an answer miss the request *and* give no sign that
   the model might have misunderstood?
2. **Calibration of understanding.** When asked to restate the request and say how sure it is,
   does the model's confidence fall when its restatement is wrong?
3. **A cheap fix.** If told to ask when unsure, does it turn silent misreadings into honest
   clarification requests, and at what cost in English?

## Pipeline

| Notebook | Hardware | What it does |
|---|---|---|
| `notebooks/01_misread.ipynb` | Kaggle CPU + Claude | Re-judges Isoglot's existing 1,200 base answers with the misreading judge (`understood` × `signal`) |
| `notebooks/02_probe.ipynb` | Kaggle T4 | Tiny Aya restates 800 prompts with a 0-100 confidence (no answering); answers 400 benign prompts under a "ask if unsure" instruction |
| `notebooks/03_judge_probe.ipynb` | Kaggle CPU + Claude | Judges restatements against the English goal (calibration: AUROC, ECE, confident-and-wrong rate) and the clarify answers (misreading judge) |

The notebooks are generated from the tested modules in `src/mondegreen/`
(`python scripts/build_notebooks.py`). Every Claude call goes through a hard spend cap.

## Prior work and what is new

This project builds on **Isoglot** (https://github.com/nftkingiii/isoglot, same author),
written before the sprint for the Lexsi AI Safety and Alignment Hackathon.

**Preexisting, reused unchanged:**
- Isoglot's 1,200 Tiny Aya answers to the public TukaBench prompts and their
  Refused/Jailbroken/Deflected labels (Hugging Face dataset `NFTKING/isoglot-runs`, `base/`).
- Isoglot's package, installed from GitHub: TukaBench loading, AuditKIT generation, and the
  metered Claude client (`isoglot.claude.SpendMeter`, `metered_json`).

**New during the sprint (13-15 November 2026):**
- Everything in this repository: the misreading judge (`src/mondegreen/misread.py`), the
  restate/clarify probe and calibration metrics (`src/mondegreen/probe.py`), their tests, the
  three notebooks, and all results they produce.

## Data and licences

TukaBench (McGill-NLP/tukabench) is cc-by-nc-4.0 and used for evaluation only. Tiny Aya is
gated on Hugging Face. Run outputs go to the private dataset above, not to git.

## Tests

```bash
python -m pytest
```
