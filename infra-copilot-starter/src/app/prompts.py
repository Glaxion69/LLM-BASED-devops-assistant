from typing import Final

# Keep prompts concise and versioned; outputs must be short and safe to log.

CLASSIFY_PROMPT_V1: Final[str] = (
    """
You are an incident triage assistant. Classify the source and severity for this event.
Return JSON with keys: source, severity.
Only choose source from: [prometheus, systemd, nginx, custom].
Only choose severity from: [info, warning, critical].
Event:
summary: {summary}
details: {details}
service: {service}
node: {node}
labels: {labels}
""".strip()
)

SUMMARIZE_PROMPT_V1: Final[str] = (
    """
You are concise. Summarize likely root cause in 1-2 short sentences.
Return JSON with key: root_cause.
Event:
summary: {summary}
details: {details}
""".strip()
)

CATEGORY_PROMPT_V1: Final[str] = (
    """
Map this incident to a playbook category.
Return JSON with key: category.
Pick one short label (kebab-case) like: nginx-502, high-cpu, systemd-crash-loop, oom-kill, disk-full, tls-handshake, dns-failure, network-timeout, db-connection.
Event:
summary: {summary}
details: {details}
""".strip()
)

SUGGEST_PROMPT_V1: Final[str] = (
    """
Generate up to 3 SAFE shell commands or minimal config diffs to investigate/mitigate.
Keep commands read-only or low-risk; do not destroy data; prefer status, logs, validation.
Return JSON with keys: title, rationale, items (array of {type: "command"|"diff", content, explanation}).
Inputs:
category: {category}
root_cause: {root_cause}
source: {source}
severity: {severity}
service: {service}
""".strip()
)


