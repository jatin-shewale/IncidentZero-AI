# IncidentZero AI
### Autonomous Multi-Agent SOC Analyst, powered by Gemma4

---

## Background

Every company with an IT team has a security operations center, or SOC, where analysts spend their day watching for signs of compromise.

The tools they use, like SIEM platforms such as Elastic Security or Splunk, are very good at one thing: collecting logs. Every login, every process execution, every DNS query, every network connection is recorded somewhere.

The real problem begins after that.

When something suspicious shows up, a human analyst has to open multiple log sources, line up timestamps by hand, compare events across systems, and answer a long list of questions: Is this really an attack? What happened first? What did the attacker touch? Which machines are affected? What should we do next?

That work is slow. A trained analyst can spend **30 to 60 minutes per alert**, and a mid-size company can receive thousands of alerts a day.

The result is what the industry calls **alert fatigue**. Real attacks get buried under noise, response becomes slower, and analysts burn out. The bottleneck was never a lack of data. The bottleneck was that nobody, and nothing, was investigating that data fast enough.

---

## The problem statement

> Can an AI system take a plain-English request like "investigate this workstation" and autonomously do what a senior Tier-3 analyst does: decide what evidence it needs, pull it from the SIEM, correlate it across log sources, determine whether it is really an attack, explain why with cited evidence, map it to known attacker techniques in MITRE ATT&CK, and recommend a response in minutes instead of an hour, without making anything up?

That last part is the hard constraint.

A security tool that hallucinates an IP address or invents a compromised account is worse than useless. In incident response, confidence without evidence is a liability.

---

## Our solution - technical approach

**IncidentZero AI** is a multi-agent investigation platform where the detection logic and the reasoning logic are deliberately kept separate, with **Gemma4** as the centerpiece of the hackathon story.

- A **deterministic, rule-based detection engine** looks for real malicious behavior such as encoded PowerShell, LSASS credential access, registry persistence, malicious DNS or IP resolution against threat intel, C2 beaconing patterns, and anomalous logins. It never guesses. Every finding is tied to a real log record.
- **Gemma4** sits on top of that verified evidence as the reasoning layer. It plans which log categories to pull for a given request, writes the plain-English investigation narrative, answers analyst follow-up questions in chat, and drafts the final report, always grounded in the evidence the rule engine already found.
- On top of MITRE ATT&CK mapping, the system now also translates findings into **OWASP Top 10** and **CIS Controls** themes so the same incident can be explained from an attacker-technique angle and a defensive-hardening angle.

This split means the system is explainable by construction. Every conclusion the analyst sees carries its supporting log record, a MITRE ATT&CK technique ID, and a confidence score.

---

## Workflow

```text
Analyst request ("Investigate FIN-PC-023")
        |
        v
  Planner Agent          -> decides which evidence categories are needed
        |
        v
  Elastic / MCP Agent    -> pulls auth, process, network, DNS, Sysmon, registry, file events
        |
        v
  Threat Hunter Agent    -> rule-based detection (encoded PowerShell, LSASS access,
                             persistence, C2 beaconing...) -- every finding cites its source event
        |---> IOC Agent            -> cross-references indicators against threat intel
        |---> Timeline Agent       -> merges everything into a chronological attack story
        |---> Attack Graph Agent   -> builds an interactive node/edge relationship graph
        |---> MITRE Agent          -> maps findings to ATT&CK techniques
        |---> Benchmark Agent      -> maps the same evidence to OWASP Top 10 and CIS themes
        |---> Risk Agent           -> scores overall incident severity
        |---> Response Agent       -> recommends immediate and long-term actions
        `---> Explainability Agent -> validates every finding, then asks Gemma4 to narrate it in plain English
        |
        v
  Report Agent            -> generates a technical or executive Markdown report
```

Every step streams live to the frontend over WebSocket, so the analyst watches the agents work in real time instead of staring at a spinner.

---

## Inspiration

The inspiration came from the daily reality of SOC work: a queue of alerts that never empties, and a job that is often 80% manual log-correlation and 20% actual decision-making.

We wanted to flip that ratio.

The goal was to let the AI do the correlation and the analyst do the decision-making, without asking anyone to just "trust the AI." That is why every output is evidence-cited by design, not just plausible-sounding. For this hackathon, **Gemma4 is the hero model** because it powers the planning, reasoning, and explanation layer that makes the entire system feel intelligent instead of just scripted.

We also wanted the same incident to speak two languages at once: attacker behavior through MITRE ATT&CK, and defense priorities through OWASP Top 10 and CIS Controls. That makes the writeup stronger for judges because it shows both the threat story and the security-hardening story.

---

## How we built it

- **Model:** **Gemma4**, run locally via [Ollama](https://ollama.com). No data ever leaves the machine. This is the model that powers the hackathon narrative and gives IncidentZero AI its intelligence layer. The architecture is model-size agnostic, so swapping to a lighter or larger Gemma variant is just a configuration change.
- **Prompt engineering, not fine-tuning or full RAG:** each agent that calls Gemma4 injects a tightly scoped block of already-verified evidence into the prompt, along with a system prompt that forbids inventing IPs, hashes, users, or events and requires a confidence score on every claim. We chose this over fine-tuning because the most important constraint here is zero hallucination, and strict grounding is easier to control than learned behavior.
- **Frameworks and stack:** FastAPI, SQLAlchemy, and WebSockets on the backend; React 19, Vite, and Tailwind on the frontend; Pandas for the local log engine; `elasticsearch-py` for optional Elasticsearch backing; and the official MCP Python SDK. The same security tools used by the in-process agents are also exposed through a standalone MCP server, so any MCP-compatible client can query the SOC data directly.
- **Benchmark-driven reporting:** the report layer now includes a dedicated OWASP / CIS benchmark view, not just a MITRE table. That means the same findings can be reviewed from attacker-technique, compliance-theme, and remediation perspectives without duplicating investigation logic.
- **Reliability design:** every Gemma4 call has a deterministic fallback. If Ollama is not running, the planner falls back to keyword-based planning and the narrative agent falls back to a template built directly from verified findings. The system never crashes and never blocks on the LLM being available, which is exactly what a real security tool needs.

---

## The prototype

- GitHub: https://github.com/jatin-shewale/IncidentZero-AI.git
- Google Drive: [Add your Google Drive demo/assets link here]

---

## Challenges we ran into

Building an 11-agent pipeline, a real MCP server, optional Elasticsearch integration, a live-updating React dashboard, a Gemma4-centered reasoning layer, and benchmark mapping for MITRE plus OWASP/CIS in one day surfaced a lot of very concrete problems.

- **MCP SDK version drift.** The `mcp` package changed between the versions we tried mid-build. `mcp.server.fastmcp.FastMCP` did not exist in the newer release we first installed, so we pinned to a known version to get a stable and documented API.
- **Evidence scoping bugs that could have caused false conclusions.** One network-log query was matching on the wrong field and silently returning every host's traffic instead of just the investigated host's traffic. That would have polluted the IOC list with unrelated noise, so we caught it by actually running the pipeline end to end against real data.
- **Keeping Gemma4 honest.** The easy version of this project would ask an LLM "was this machine compromised?" But that invites hallucinated IPs and invented timelines. Splitting detection into deterministic rules and keeping Gemma4 for narration solved the trust problem, even though it required more up-front engineering.
- **Making the demo resilient.** A hackathon demo cannot die because a laptop has no GPU or Ollama is not running. Every LLM-dependent path needed a deterministic twin, which made the agent logic bigger but also made the system usable anywhere, instantly.
- **Scoping down.** The original architecture sketch included LangGraph orchestration and a vector database memory of past incidents. In one day we prioritized a correct, explainable core pipeline over those extras, and documented them as the natural next steps instead of leaving them half-built.
- **Making benchmarks feel native.** OWASP and CIS could have been a tiny note in the report, but that would have made them feel secondary. Promoting them to a dedicated page and endpoint made the product feel more complete and gave reviewers a clearer view of the security-hardening story.

---

## Why this matters

IncidentZero AI is not just a demo that looks smart.

It is a working example of how to build security automation that is fast, explainable, and trustworthy at the same time. The system does not replace the analyst. It removes the most repetitive part of the analyst's job so the human can focus on judgment, containment, and response.

That is the real value: less log hunting, less noise, fewer false conclusions, and a clearer path from detection to action.

---

*IncidentZero AI - "Don't search logs. Understand attacks."*
