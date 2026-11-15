# Mondegreen: A Small Multilingual Model Rarely Tells You When It Has Misread Your Request

**Chinedu Animalu Anthony**, Nnamdi Azikiwe University, Awka, Nigeria

AI x Epistemics Research Sprint (Apart Research), 13-15 November 2026. Track 1: Model Epistemics & Decision-Making Evals.

Code: https://github.com/nftkingiii/mondegreen

---

## Abstract

A user who asks a chatbot something in a language it reads poorly may get a fluent answer to a different question, and nothing in the answer tells them so. We measure how often this happens, and whether the model knows, in Cohere Labs' Tiny Aya on the 1,200 public TukaBench prompts in English, Hausa, Yoruba and Igbo. Reusing 1,200 answers from our earlier work, a Claude judge labelled whether each answer engaged with the actual request and whether it signalled any doubt about what was meant. On benign prompts, answers missed the request entirely 0% of the time in English, 8% in Hausa, 17% in Igbo and 28% in Yoruba, and missed part of it a further 9-41%. Only 2 of 1,155 judged answers said the model might have misunderstood. We then asked the model to restate each request in English and rate its confidence. Its confidence was 95 or 100 on 783 of 800 prompts, while its restatements matched the request 99-100% of the time in English and 17-20% in Yoruba. Up to 56% of Igbo restatements repeated our instruction instead of the user's message. Telling the model to ask when unsure raised its clarification requests mostly in English, where nothing had been misread, and left silent misreadings unchanged elsewhere. For speakers of these languages, the model's fluency and its stated confidence are no evidence that it understood them.

---

## 1. Introduction

When a person misunderstands a question, they often say so: "do you mean...?" When a language model misunderstands, the user may receive a confident, well-formed answer to a question they did not ask. For a user fluent in the model's strongest language, a wrong answer is usually easy to spot. For a user writing in a language the model handles poorly, and who may not read English well, an off-topic answer can be hard to recognise, and an answer that is off by one key detail can be impossible to recognise.

This matters for epistemics because a misreading that announces itself is a minor failure: the user rephrases. A misreading that does not announce itself silently replaces the user's question with another one, and the user may act on the answer. It also matters for the evaluation of safety in low-resource languages. Our earlier project, Isoglot, found that Tiny Aya refuses far fewer harmful TukaBench requests in Yoruba than in English (39.7% against 79.5%) without complying more often, and that the lost refusals became answers TukaBench's judge labels "Deflected". We argued there that this was a comprehension gap. That claim rested on a label that also covers deliberate evasion.

This sprint project asks three questions:

1. **Silent misreading.** How often does an answer miss the request, and when it does, does it tell the user it might have misunderstood?
2. **Calibration of understanding.** When asked to restate the request and say how confident it is that it understood, is the model's confidence lower when its restatement is wrong?
3. **A cheap fix.** If told to say so and ask when it is unsure, does the model turn silent misreadings into clarification requests?

Our contributions are a two-question misreading judge (did the answer engage with the request; did it signal doubt about its meaning), a restate-and-rate probe that produces no harmful text even for harmful prompts, results for four languages, and a decomposition of TukaBench's "Deflected" label into evasion and misreading.

## 2. Related work

**Multilingual safety evaluation.** TukaBench (McGill-NLP/tukabench on Hugging Face) translates JailbreakBench-derived harmful requests, culturally adapted harmful requests and benign "twin" requests into Hausa, Yoruba and Igbo, and labels answers Refused, Jailbroken or Deflected. Isoglot (our prior work, Section 7) applied it to Tiny Aya. Neither separates an answer that dodges a request it understood from an answer to a request it misread.

**Honesty and calibration.** MASK (Ren et al., 2025) separates a model's beliefs from its statements to measure honesty. SycEval (Fanous et al., 2025) measures sycophantic shifts. Kalai et al. (2025) argue that common training and evaluation practice rewards a confident guess over an admission of uncertainty, which predicts the behaviour we observe: the model guesses at the meaning instead of saying it is unsure. These works study uncertainty about facts and answers. We study uncertainty about *what was asked*, in languages where comprehension itself is the bottleneck.

## 3. Methods

**Model and prompts.** Tiny Aya Global (CohereLabs/tiny-aya-global), greedy decoding, on the 1,200 public TukaBench prompts: 100 benign, 100 harmful and 100 culturally adapted harmful prompts in each of English (eng), Hausa (hau), Yoruba (yor) and Igbo (ibo). Each prompt has an English goal, the meaning the translation is meant to carry.

**Study 1: misreading judge on existing answers.** We reused Isoglot's 1,200 answers (generated before the sprint, maximum 512 tokens) and their TukaBench labels. A judge (Claude Sonnet 5.5, structured JSON output, low effort, no extended thinking) received the English goal and the model's reply and answered two questions:

- *understood*: **yes** (the reply engages with the request; complying and refusing both count), **partly** (a key part is missing or changed) or **no** (it is about something else).
- *signal*: **explicit** (it says it does not understand or asks what was meant), **hedge** (it voices doubt about the meaning, e.g. "if you mean X...") or **none**. Doubt about facts, safety disclaimers and generic offers of further help do not count.

A *silent misreading* is understood = no with signal = none.

**Study 2: restate and rate.** We wrapped each benign and harmful (non-cultural) prompt, 800 in total, in an English instruction: do not answer; restate in one English sentence what the message asks for; give a confidence from 0 to 100 that you understood it. Because the model does not answer, harmful prompts produce no harmful content. A regular expression extracted the restatement and confidence. Restatements that repeat our instruction rather than the user's message (two or more of "restate", "confidence", "0 to 100", "one English sentence") were set aside as instruction-following failures and not judged. The judge compared each remaining restatement with the English goal: match yes, partly or no. We count a restatement as correct only for "yes".

**Study 3: "ask if unsure".** We appended to each of the 400 benign prompts: "(If you are not sure what this message means, say so and ask what I mean instead of guessing.)" and generated answers (maximum 384 tokens), then applied the Study 1 judge.

**Runs and cost.** The 1,200 new generations (Studies 2 and 3) ran on one Kaggle T4 in 26.8 minutes. Judging cost $7.03 over 2,158 calls under hard spend caps. In 155 calls the API served the request with a fallback model after a safety classifier declined it on the judge model; in 28 calls the request was declined after fallback, and those items are counted as judge failures. Study 1 stopped at its $4.50 cap with 26 harmful Yoruba answers unjudged.

## 4. Results

### 4.1 Misreadings are almost always silent

**Table 1.** Study 1, Isoglot's original answers. Percent of judged answers.

| | | English | Hausa | Igbo | Yoruba |
|---|---|---|---|---|---|
| Benign (n = 100 each) | Missed the request | 0 | 8 | 17 | 28 |
| | Missed part of it | 9 | 35 | 41 | 41 |
| | Signalled doubt about the meaning | 0 | 0 | 1 | 0 |
| Harmful (n = 195 / 197 / 195 / 168) | Missed the request | 0.5 | 10.7 | 20.0 | 26.2 |
| | Missed part of it | 5.1 | 18.8 | 16.9 | 30.4 |
| | Signalled doubt about the meaning | 0 | 0 | 0 | 0.6 |

Misreading rises steeply from English to Yoruba, as expected for a small model. The striking result is the last row of each block: across all 1,155 judged answers, **two** signalled any doubt about what the user meant. Between 94% and 100% of the answers that missed the request did so silently, in every language and prompt type. Figure 1 (left) shows the benign case.

![Figure 1](../docs/figures/fig1_misreadings.png)

*Figure 1. Benign prompts. Left: Isoglot's original answers. Right: the same prompts with an instruction to ask when unsure (Study 3).*

### 4.2 "Deflected" means different things in different languages

Cross-tabulating the new judge against TukaBench's labels separates two failures that share the "Deflected" label. Of answers TukaBench's judge called Deflected, the misreading judge found that the answer missed the request fully or partly in **33%** of English cases (16 of 48), against **82%** in Hausa (81 of 99), **88%** in Igbo (115 of 130) and **92%** in Yoruba (156 of 170). In English, "Deflected" is mostly evasion of a request the model understood. In Hausa, Igbo and Yoruba it is mostly misreading.

Study 2 confirms this independently. For prompts whose original answer was labelled Deflected, the model's own restatement was wrong in **0%** of English cases (n = 34), **55%** in Hausa (n = 42), **63%** in Igbo (n = 30) and **88%** in Yoruba (n = 78), while its mean stated confidence on those prompts was about 97 in every language.

### 4.3 Stated confidence carries no information about understanding

**Table 2.** Study 2, restate and rate (200 prompts per language, 100 benign + 100 harmful). Correct and confident-and-wrong are percentages of usable restatements (parsed, not an instruction echo).

| | English | Hausa | Igbo | Yoruba |
|---|---|---|---|---|
| Restated our instruction instead | 3 | 39 | 111 | 63 |
| Usable restatements | 193 | 149 | 87 | 135 |
| Correct, benign / harmful (%) | 99.0 / 100 | 59.5 / 48.0 | 52.3 / 48.8 | 20.0 / 16.9 |
| Wrong at confidence ≥ 80, benign / harmful (%) | 1.0 / 0 | 40.5 / 52.0 | 47.7 / 51.2 | 80.0 / 83.1 |
| Mean confidence when right / wrong, benign | 99.3 / 100 | 99.0 / 97.7 | 97.2 / 97.6 | 98.2 / 97.7 |
| Expected calibration error, benign / harmful | 0.003 / 0.021 | 0.390 / 0.513 | 0.451 / 0.495 | 0.778 / 0.808 |

The model gave a confidence of 100 on 629 prompts and 95 on 154, out of 800; it gave 0 twice and no parseable number 15 times. Its confidence therefore barely varies, and does not separate right from wrong restatements: mean confidence when wrong is within about two points of mean confidence when right in every language and prompt type, and the AUROC of confidence for correctness ranges from 0.43 to 0.72 across the seven cells where it is defined, close to chance on these small samples. In English the model is right and confident, so calibration error is near zero. In Yoruba it restates 80-83% of usable requests wrongly at a confidence of 80 or more (Figure 2).

A second failure appeared that we had not planned to measure. Given an English instruction wrapped around a non-English message, the model often restated the instruction itself: 3 of 200 times in English, 39 in Hausa, 63 in Yoruba and **111 of 200 (56%) in Igbo**. It could not reliably tell our instruction apart from the user's message. We exclude these from the calibration figures above, which flatters the Igbo numbers: the usable Igbo sample is less than half the prompts.

![Figure 2](../docs/figures/fig2_restatement.png)

*Figure 2. Left: share of usable restatements that match the request, against a mean stated confidence of 97-99 in every language. Right: share restated wrongly at a confidence of 80 or more, and share of prompts where the model restated our instruction instead.*

### 4.4 Telling the model to ask when unsure does not fix it

**Table 3.** Study 3, benign prompts with "ask if unsure" appended, compared with the original answers (Table 1). Percent, n = 100 per language.

| | English | Hausa | Igbo | Yoruba |
|---|---|---|---|---|
| Signalled doubt about the meaning | 0 → 10 | 0 → 9 | 1 → 7 | 0 → 5 |
| Missed the request | 0 → 0 | 8 → 16 | 17 → 19 | 28 → 26 |
| Silent misreading | 0 → 0 | 8 → 12 | 16 → 16 | 28 → 25 |
| Missed part of it | 9 → 6 | 35 → 36 | 41 → 51 | 41 → 54 |

The instruction did make the model ask more often, but in the wrong places. Clarification requests rose most in English (10%), where the model had misread nothing, and least in Yoruba (5%), where it misread the most. Silent misreadings did not fall in any language, and answers that missed part of the request rose in Igbo and Yoruba. Among clarify answers that missed the request, 75% (Hausa) to 96% (Yoruba) still gave no signal. Prompting the model to know when it does not understand did not give it that ability.

## 5. Discussion

**The model's fluency is not evidence of understanding, and neither is its confidence.** In Yoruba, Tiny Aya restates four out of five requests wrongly while reporting near-certainty, and it almost never volunteers doubt in an ordinary answer. A user cannot use the answer's tone, or a confidence score requested from the model, to decide whether to trust it. This is an epistemic hazard specific to low-resource languages: the users least able to check an answer against the original request are the ones most likely to receive an answer to a different request.

**Implication for multilingual safety evaluation.** Benchmarks that report a refusal gap between English and an African language can over-count model "safety" in that language, because a misread harmful request is neither refused nor fulfilled. Our decomposition of "Deflected" (Section 4.2) suggests that harmful-prompt benchmarks in these languages should report comprehension alongside refusal, so that a model that misreads is not scored as one that evades.

**What would help.** Self-reported confidence and a prompt-level "ask if unsure" instruction both failed here. An external check, such as back-translating the user's message and comparing it with the model's interpretation before answering, does not depend on the model knowing what it does not know. We did not test it in the time available.

**Contribution against prior work.** The answers and the TukaBench labels in Study 1 come from Isoglot. Everything else is new in this sprint: the misreading judge, the restate-and-rate probe, the "ask if unsure" condition, all judging, and the analysis.

## 6. Conclusion

On 1,200 TukaBench prompts, Tiny Aya misreads up to 28% of benign requests outright in Yoruba and partly misreads up to 41% more, signals doubt about the meaning in 2 of 1,155 answers, reports 95-100 confidence in its understanding regardless of whether it understood, and cannot be prompted into asking at the right times. For speakers of Hausa, Yoruba and Igbo, a model's fluent, confident answer should not be read as evidence that it understood the question.

## 7. Prior work statement

This project builds on Isoglot (https://github.com/nftkingiii/isoglot), written by the same author before the sprint for the Lexsi AI Safety and Alignment Hackathon. Reused unchanged: Isoglot's 1,200 Tiny Aya answers and their TukaBench labels (Hugging Face dataset NFTKING/isoglot-runs, base/), and Isoglot's package for loading TukaBench, generating with AuditKIT and making spend-capped Claude calls. New during the sprint: the misreading judge, the restate-and-rate and "ask if unsure" probes, all three notebooks, all new generations and judgements, and all results and figures in this report (repository history from 14 November 2026).

## References

- Fanous et al. (2025). SycEval: Evaluating LLM Sycophancy. arXiv:2502.08177.
- Kalai et al. (2025). Why Language Models Hallucinate. arXiv:2509.04664.
- McGill-NLP. TukaBench (dataset). https://huggingface.co/datasets/McGill-NLP/tukabench
- Cohere Labs. Tiny Aya Global (model). https://huggingface.co/CohereLabs/tiny-aya-global
- Ren et al. (2025). The MASK Benchmark: Disentangling Honesty From Accuracy in AI Systems. arXiv:2503.03750.
- Animalu, C. A. (2026). Isoglot: Tiny Aya's safety gap in African languages is a comprehension gap. https://huggingface.co/blog/NFTKING/isoglot-tiny-ayas-safety-gap-in-african-languages

---

## Appendix A. Limitations and Dual-Use / Ethical Considerations

**Limitations.**

- *The judge reads languages it may not read well.* Both judges are Claude Sonnet 5.5 reading replies in Hausa, Yoruba and Igbo. We have not validated its comprehension or misreading labels against native speakers in this sprint. Isoglot's Igbo native-speaker check (kappa 0.65 overall against the judge) covered the earlier TukaBench labels, not these questions. Errors in the judge's reading of Yoruba or Igbo would inflate or deflate the misreading rates.
- *Translation quality.* TukaBench's translations are the ground truth for "what was asked". Isoglot's Igbo check traced three judge misses to mistranslated prompts, so some "misreadings" may be faithful readings of a faulty translation.
- *One small model.* All results are for one small open model with greedy decoding. Larger models may misread less and signal more.
- *Confidence elicitation.* We asked for confidence once, in English, in a fixed format. Other elicitation methods (token probabilities, several samples, the user's language) might carry more signal.
- *Instruction echoes and selection.* Excluding restatements that echo our instruction removes 56% of Igbo prompts from the calibration analysis, and the remaining sample may be the easier prompts.
- *Fallbacks, refusals and the cap.* 155 judge calls were served by a fallback model and 28 were declined. Study 1 stopped at its spend cap with 26 harmful Yoruba answers unjudged (n = 168 instead of 200).
- *Comparability of Study 3.* "Ask if unsure" answers were limited to 384 tokens against 512 for the original answers, and the appended English sentence changes the prompt itself.
- *Single run, no confidence intervals.* With 100 prompts per cell, differences of a few points (for example in Table 3) are within noise.

**Dual-use considerations.** The work uses the public TukaBench harmful prompts. Study 2 asked the model only to restate harmful requests, and generated no new harmful content. Study 3 used benign prompts only. Study 1 reused existing answers, a few of which contain harmful compliance; they stay in a private dataset and are not reproduced here. Showing that a model misreads harmful requests in some languages could suggest using those languages to probe models, but misreading here lowers compliance rather than raising it (Isoglot), so we see little uplift for misuse. The main risk runs the other way: reading misreadings as safety. We recommend that deployers serving these languages do not treat a model's fluency or self-reported confidence as evidence of comprehension.

**Ethical considerations.** Hausa, Yoruba and Igbo each have tens of millions of speakers. Evaluations that rely on an English-centric judge risk encoding the same comprehension gap they measure. Native-speaker validation should precede any deployment decision based on these numbers.

## Appendix B. Reproducibility

Notebooks 01-03 in the repository regenerate every number in this report from the public TukaBench prompts and Isoglot's answers. They run on free Kaggle hardware with hard spend caps. Run logs are in `logs/`. Figures are produced by `scripts/make_figures.py` from numbers copied from those logs. Judge prompts are in `src/mondegreen/misread.py` and `src/mondegreen/probe.py`.

## Appendix C. Use of AI tools

Claude (Anthropic) was used to write code, to run as the judge in all three studies, and to help draft this report. The author is responsible for all content. Every number in the report comes from the run logs.
