# Data Card: BhashaSwitch Multilingual Evaluation Benchmark

## 1. Dataset Overview
- **Name**: BhashaSwitch Hindi-English Code-Switching Benchmark Manifest
- **Version**: 1.0.0
- **Languages**: Hindi (Devanagari), English (Latin), Code-Switched (Hinglish)
- **Schema**: CSV format with columns `clip_id`, `audio_path`, `language`, `reference`, `hypothesis`, `notes`
- **Total Test Utterances**: 8 curated diagnostic clips

## 2. Language Categories & Linguistic Phenomena
| Language Condition | Sample Count | Evaluated Linguistic Phenonema |
|:---|:---:|:---|
| **Monolingual Hindi** | 2 | Devanagari numerals (5 बजे), grammatical negation particles (नहीं) |
| **Monolingual English** | 2 | Alphanumeric entities (flight 204), command negation (*do not*) |
| **Code-Switched (Hinglish)** | 4 | Intra-sentential matrix switching, romanized particles (*pe* vs *par*), account numerals (9845 vs 9840) |

## 3. Data Integrity & PII Protection
- All utterances are synthetic or curated public conversational test prompts representing typical voice-agent intents (banking queries, meeting schedules, support confirmations).
- **No Private or Personal Identifiable Information (PII)** is included.
- Reference transcripts are human-verified for ground truth accuracy.

## 4. Evaluation Metrics
- **Word Error Rate (WER)** via `jiwer`
- **Character Error Rate (CER)**
- **Semantic Error Tracking**: Automated detection of critical negation drops and numerical digit mutations.
