import os
import json
import requests
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler


def create_app() -> App:
    bot_token = os.getenv("SLACK_BOT_TOKEN")
    app = App(token=bot_token)

    @app.command("/infra-copilot")
    def handle_copilot_command(ack, body, client):
        ack()
        trigger_id = body.get("trigger_id")
        client.views_open(
            trigger_id=trigger_id,
            view={
                "type": "modal",
                "callback_id": "infra_copilot_modal",
                "title": {"type": "plain_text", "text": "Infra Copilot"},
                "submit": {"type": "plain_text", "text": "Submit"},
                "close": {"type": "plain_text", "text": "Cancel"},
                "blocks": [
                    {
                        "type": "input",
                        "block_id": "src_block",
                        "label": {"type": "plain_text", "text": "Source"},
                        "element": {
                            "type": "static_select",
                            "action_id": "source",
                            "options": [
                                {"text": {"type": "plain_text", "text": "nginx"}, "value": "nginx"},
                                {"text": {"type": "plain_text", "text": "systemd"}, "value": "systemd"},
                                {"text": {"type": "plain_text", "text": "custom"}, "value": "custom"},
                            ],
                        },
                    },
                    {
                        "type": "input",
                        "block_id": "log_block",
                        "label": {"type": "plain_text", "text": "Log snippet"},
                        "element": {"type": "plain_text_input", "action_id": "log", "multiline": True},
                    },
                ],
            },
        )

    @app.view("infra_copilot_modal")
    def handle_submit(ack, body, client, view):
        ack()
        state = view.get("state", {}).get("values", {})
        source = state.get("src_block", {}).get("source", {}).get("selected_option", {}).get("value", "custom")
        log_text = state.get("log_block", {}).get("log", {}).get("value", "")
        port = int(os.getenv("PORT", "8000"))
        api_url = f"http://127.0.0.1:{port}"
        payload = {"source": source, "summary": log_text[:100], "details": log_text}
        r = requests.post(f"{api_url}/ingest/log", json=payload)
        suggestions = r.json() if r.status_code == 200 else []
        top = suggestions[0] if suggestions else {"title": "No suggestions", "rationale": "", "id": ""}
        channel = body.get("user", {}).get("id")
        blocks = [
            {"type": "section", "text": {"type": "mrkdwn", "text": f"*{top.get('title','')}*\n{top.get('rationale','')}"}},
        ]
        if top.get("id"):
            blocks.append({
                "type": "actions",
                "elements": [
                    {"type": "button", "text": {"type": "plain_text", "text": "Approve"}, "style": "primary", "action_id": "approve", "value": top.get("id")},
                    {"type": "button", "text": {"type": "plain_text", "text": "Explain"}, "action_id": "explain", "value": top.get("id")},
                ]
            })
        client.chat_postMessage(channel=channel, blocks=blocks, text=top.get('title','Infra Copilot'))

    @app.action("approve")
    def handle_approve(ack, body, client, action):
        ack()
        sid = action.get("value")
        token = os.getenv("SLACK_APP_TOKEN", "token")
        port = int(os.getenv("PORT", "8000"))
        api_url = f"http://127.0.0.1:{port}"
        r = requests.post(f"{api_url}/suggestions/{sid}/apply", headers={"X-Copilot-Approval": token})
        cmds = r.json().get("commands", []) if r.status_code == 200 else []
        client.chat_postMessage(channel=body["user"]["id"], text="\n".join(cmds) or "No commands")

    @app.action("explain")
    def handle_explain(ack, body, client, action):
        ack()
        client.chat_postMessage(channel=body["user"]["id"], text="All actions require approval and run as dry-run.")

    return app


def run():
    app = create_app()
    app_token = os.getenv("SLACK_APP_TOKEN")
    if not app_token:
        raise RuntimeError("SLACK_APP_TOKEN not set")
    SocketModeHandler(app, app_token).start()


