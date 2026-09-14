# inboxHero: Agentic Email Management System
**IIIT Hyderabad — Fortnight Assignment 06: Agentic Systems in the Wild**  
**Student:** Murali Krishna D (`evernorth-aai-1152623`)  
**GitHub Repository:** [https://github.com/Krishna4/inbox-hero-IIT](https://github.com/Krishna4/inbox-hero-IIT)  

---

## Overview

`inboxHero` is an agentic email triage and response system designed to process, ground, and safely clear an executive inbox (100 messages) without human burnout or catastrophic hallucination. It implements deterministic zero-token triage for automated mail, strictly grounded drafting (cite-or-silence), adversarial prompt injection defense, cross-process preference memory, and a comprehensive 3-pane dashboard.

---

## Quickstart & Demonstration Commands

```bash
# Setup environment (Python 3.10+)
pip install -r requirements.txt

# Run complete regression suite (Parts 1 to 7)
python3 tests/test_part1.py
python3 tests/test_part2.py
python3 tests/test_part3.py
python3 tests/test_part4.py
python3 tests/test_part5.py
python3 tests/test_part6.py
python3 tests/test_part7.py

# Run standalone capabilities via CLI
python3 demo.py --cap R1            # Part 2: Triage (100% zeroed, rules + model)
python3 demo.py --cap R2 --msg m008   # Part 3: Grounded draft citing m003
python3 demo.py --cap R3 --dry-run   # Part 4: Safety gate intercept
python3 demo.py --cap R4            # Part 5: Standing instructions persistence
python3 demo.py --cap R5            # Part 6: Hostile attack defense & refusal
python3 demo.py --cap R6            # Part 7: Three-pane dashboard (HTML + JSON)
python3 demo.py --cap X1            # Part 8: Follow-up tracker (m044 chase)
python3 demo.py --cap X2            # Part 8: Multi-message thread summarizer
python3 demo.py --cap X3            # Part 8: Smart daily digest with persistent memory
```

---

## Final Report

### 1. What did you refuse to automate?
We strictly refused to automate outbound email dispatch (`send`) and message deletion (`delete`), gating both behind human authorization in `SafetyGate` (`safety.py`). In an executive inbox, an autonomous send or delete is completely irreversible and carries serious financial, legal, and operational consequences. For example, message `m018` (Marcus Vance regarding the revised SAFE agreement) requires legal review and founder signature; autonomously sending an unvetted reply or commitment could legally bind the company. Furthermore, for inquiries lacking factual context in the inbox (such as `m012` asking about SOC 2 audit timelines), the system adheres to the *cite-or-silence* principle: it strictly refuses to generate speculative or placating "canned" drafts, instead flagging the item for human resolution.

### 2. Where does untrusted text enter your system?
Untrusted text enters the system through all incoming email fields in `inbox.json` (`subject`, `body`, `from_addr`, and display names). Attackers exploit these fields in adversarial emails like `m024` (delimiter escape prompt injection) and `m039` (system prompt override instructing the model to exfiltrate all emails). We defend against this by enforcing strict structural boundaries: all message contents passed to language models are wrapped in passive XML tags (`<untrusted_email id='...'>`) preceded by explicit meta-instructions declaring the enclosed content to be passive data rather than executable instructions. In addition, deterministic security heuristics (`security.py`) scan for injection syntax, domain spoofing (e.g. `m023` using `@paperjet.co` instead of `@paperjet.io`), and credential harvesting links (`m045`) prior to model evaluation.

### 3. Who is accountable when it sends the wrong thing?
The human supervisor who explicitly confirms the transmission at the `SafetyGate` prompt is accountable for any erroneous email sent. Because `inboxHero` is architected as an intelligence amplifier with human-in-the-loop oversight rather than an unchecked autonomous agent, no external email can be dispatched without human verification. The system provides transparency—surfacing cited message IDs, proposed recipient, and rationale—enabling the user to make an informed decision. If an internal component produces an incorrect draft or triage label before human review, the responsibility rests with the system developers for maintaining verification test suites and prompt guardrails.

### 4. Name your own machinery.
`inboxHero` is powered by five interconnected subsystems:
1. **The Cite-or-Silence Grounding Engine (`drafting.py`):** Traverses conversational thread histories and validates that every asserted fact in a draft is traceable to exact message IDs, silencing the generator when facts are absent.
2. **The Dual-Pass Triage Pipeline (`rules.py` & `triage.py`):** Employs a zero-token regex rules engine to instantly triage 33 receipts, alerts, and notifications, passing only complex human correspondence to Qwen2.5:1.5b (via Ollama) in 10-message batches.
3. **The Irreversible Action Safety Gate (`safety.py`):** An atomic interceptor that blocks write operations to `outbox/` in dry-run mode and requires explicit terminal approval before persisting sent emails.
4. **The Cross-Process Preference Memory Store (`memory.py`):** Extracts standing instructions (such as CCing Priya on legal mail) and persists them to `prefs.json`, surviving full process restarts.
5. **The Three-Pane Glassmorphic Executive Dashboard (`dashboard.py` & `dashboard.html`):** Synthesizes pending gated actions, refused hostile threats, and a calendar view featuring multi-message schedule derivation (`m038` + `m040` $\rightarrow$ Sep 16 board deck) and collision detection (`m010` vs `m061`).

---

## Project Structure

```
inboxHero_MuraliKrishnaD/
├── CAPABILITIES.md        # Comprehensive human-readable pitch & capability manifest
├── capabilities.json      # Machine-readable capability manifest for auto-grading
├── README.md              # Project overview, setup, and Final Report answers
├── config.py              # Configuration loader (Ollama: qwen2.5:1.5b)
├── schemas.py             # Strongly typed data models (Pydantic / dataclasses)
├── store.py               # MailStore: chronological thread-walk & cross-thread retrieval
├── rules.py               # Zero-token deterministic triage rule engine
├── triage.py              # Dual-pass triage coordinator (Part 2 / R1)
├── drafting.py            # Grounded draft synthesis & citation verification (Part 3 / R2)
├── safety.py              # SafetyGate & Outbox writer (Part 4 / R3)
├── memory.py              # PreferenceStore: standing instruction persistence (Part 5 / R4)
├── security.py            # SecurityScanner: hostile injection & phishing defense (Part 6 / R5)
├── dashboard.py           # 3-Pane Dashboard generator (Part 7 / R6)
├── custom_caps.py         # Custom Capabilities X1, X2, X3 (Part 8)
├── demo.py                # Unified CLI runner for all capabilities (--cap <ID>)
├── data/
│   └── inbox.json         # Mock dataset (100 messages)
├── outbox/                # Outbox directory for approved emails
├── tests/                 # Complete verification test suite (Parts 1–7)
│   ├── test_part1.py
│   ├── test_part2.py
│   ├── test_part3.py
│   ├── test_part4.py
│   ├── test_part5.py
│   ├── test_part6.py
│   └── test_part7.py
├── decisions.json         # Output of R1 Triage
├── drafts.json            # Grounded drafts
├── prefs.json             # Persisted standing instructions
├── trace.jsonl            # Structured execution audit log
├── dashboard.html         # Interactive executive dashboard
└── dashboard.json         # Structured dashboard data
```
