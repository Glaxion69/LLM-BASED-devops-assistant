
from typing import List, Optional, Tuple
import os
import json
from .models import IncidentEvent, Suggestion

# LangChain imports are optional at runtime; import lazily
try:
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import JsonOutputParser
    from langchain_openai import ChatOpenAI
    from langchain_anthropic import ChatAnthropic
    LANGCHAIN_AVAILABLE = True
except Exception:
    LANGCHAIN_AVAILABLE = False


# Prompt versions (keep short and safe)
CLASSIFY_PROMPT_V1 = """
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

SUMMARIZE_PROMPT_V1 = """
You are concise. Summarize likely root cause in 1-2 short sentences.
Return JSON with key: root_cause.
Event:
summary: {summary}
details: {details}
""".strip()

CATEGORY_PROMPT_V1 = """
Map this incident to a playbook category.
Return JSON with key: category.
Pick one short label (kebab-case) like: nginx-502, high-cpu, systemd-crash-loop, oom-kill, disk-full, tls-handshake, dns-failure, network-timeout, db-connection.
Event:
summary: {summary}
details: {details}
""".strip()

SUGGEST_PROMPT_V1 = """
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


def _select_llm() -> Optional[object]:
    """Select an LLM based on available API keys.

    - Prefer OpenAI if OPENAI_API_KEY present
    - Else use Anthropic if ANTHROPIC_API_KEY present
    - Return None if neither is available or LangChain missing
    """
    if not LANGCHAIN_AVAILABLE:
        return None
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    model_temperature = 0.1
    if openai_key:
        # Model name intentionally short; user can control via env if needed
        return ChatOpenAI(model="gpt-4o-mini", temperature=model_temperature)
    if anthropic_key:
        return ChatAnthropic(model="claude-3-5-sonnet-latest", temperature=model_temperature)
    return None


def _heuristic_fallback(event: IncidentEvent) -> List[Suggestion]:
    base = {
        "event_id": event.id,
        "title": "Review service and restart gracefully",
        "rationale": f"Source={event.source}, severity={event.severity}. Start with safe checks.",
        "commands": [
            "sudo systemctl status " + (event.service or "SERVICE"),
            "sudo journalctl -u " + (event.service or "SERVICE") + " -n 200",
            "sudo systemctl restart " + (event.service or "SERVICE") + " --no-block",
        ],
        "diffs": [],
        "requires_approval": True,
    }
    if event.source == "nginx":
        base["title"] = "Inspect upstream timeouts and reload Nginx"
        base["commands"] = [
            "sudo tail -n 200 /var/log/nginx/error.log",
            "sudo nginx -t",
            "sudo systemctl reload nginx",
        ]
    return [Suggestion(**base)]


def _run_chain(llm, prompt: str, variables: dict) -> dict:
    prompt_tmpl = ChatPromptTemplate.from_template(prompt)
    parser = JsonOutputParser()
    chain = prompt_tmpl | llm | parser
    return chain.invoke(variables)


def _short(text: Optional[str], max_len: int = 240) -> str:
    if not text:
        return ""
    return text.strip()[:max_len]


def suggest(event: IncidentEvent) -> List[Suggestion]:
    llm = _select_llm()
    if llm is None:
        return _heuristic_fallback(event)

    # Prepare shared vars
    vars_common = {
        "summary": _short(event.summary, 400),
        "details": _short(event.details, 1000),
        "service": event.service or "",
        "node": event.node or "",
        "labels": json.dumps(event.labels or {}),
    }

    try:
        # 1) Classify source/severity
        classify = _run_chain(llm, CLASSIFY_PROMPT_V1, vars_common)
        source = classify.get("source") or event.source
        severity = classify.get("severity") or event.severity

        # 2) Summarize root cause
        root = _run_chain(llm, SUMMARIZE_PROMPT_V1, vars_common)
        root_cause = _short(root.get("root_cause", ""), 240)

        # 3) Category mapping
        categorization = _run_chain(llm, CATEGORY_PROMPT_V1, vars_common)
        category = _short(categorization.get("category", "custom"), 48)

        # 4) Suggestions
        suggest_vars = {
            "category": category,
            "root_cause": root_cause,
            "source": source,
            "severity": severity,
            "service": event.service or "",
        }
        sug = _run_chain(llm, SUGGEST_PROMPT_V1, suggest_vars)
        title = _short(sug.get("title") or f"Playbook: {category}", 80)
        rationale = _short(sug.get("rationale") or root_cause or "Triage steps", 240)
        items = sug.get("items") or []

        commands: List[str] = []
        diffs: List[str] = []
        for item in items[:3]:
            item_type = str(item.get("type", "command")).lower()
            content = _short(item.get("content", ""), 300)
            explanation = _short(item.get("explanation", ""), 160)
            if not content:
                continue
            if item_type == "diff":
                # Prepend explanation as a comment when available
                if explanation:
                    diffs.append(f"# {explanation}\n{content}")
                else:
                    diffs.append(content)
            else:
                if explanation:
                    commands.append(f"# {explanation}")
                commands.append(content)

        suggestion = Suggestion(
            event_id=event.id,
            title=title,
            rationale=rationale,
            commands=commands,
            diffs=diffs,
            requires_approval=True,
            confidence=0.6,
        )
        return [suggestion]
    except Exception:
        # Any issue falls back to heuristic
        return _heuristic_fallback(event)
