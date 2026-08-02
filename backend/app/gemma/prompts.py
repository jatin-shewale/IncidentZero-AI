"""Prompt templates used by agents when calling Gemma (app/gemma/client.py)."""

PLANNER_PROMPT = """A SOC analyst has asked:

"{query}"

Based on this request, decide which evidence categories are required to
investigate it. Choose only from: authentication, process, network, dns,
sysmon, registry, file, threat_intel.

Respond with a short JSON object:
{{"investigation_goal": "...", "required_data": ["..."], "priority": "low|medium|high|critical"}}
"""

NARRATIVE_PROMPT = """Below is the evidence IncidentZero AI's agents collected for
investigation {investigation_id} on host {host}:

{evidence_block}

Write a 3-4 sentence investigation summary in the voice of a senior SOC
analyst, in plain English, strictly grounded in the evidence above. Do not
invent details. End by noting overall confidence as a percentage."""

CHAT_PROMPT = """The analyst asked the following question about investigation
{investigation_id}:

"{question}"

Here is the evidence and findings already collected for this investigation:

{evidence_block}

Answer the analyst's question using ONLY this evidence. If the evidence
does not support a confident answer, say so plainly. Keep the answer under
120 words, and end with a confidence percentage if you made a factual claim."""

REPORT_PROMPT = """Write a {kind} incident report for investigation
{investigation_id} using only the evidence, timeline and MITRE mapping
below. Use clear section headings. Do not invent facts.

{evidence_block}
"""
