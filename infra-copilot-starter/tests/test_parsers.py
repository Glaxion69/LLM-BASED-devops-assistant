from src.ingestors.prometheus import from_alertmanager
from src.ingestors.systemd import from_journal_record
from src.ingestors.nginx import from_log_record


def test_prometheus_parser_minimal():
    payload = {
        "alerts": [
            {
                "labels": {"alertname": "HighCPU", "service": "api", "instance": "node-1"},
                "annotations": {"summary": "CPU > 90%", "description": "Sustained high CPU"},
            }
        ]
    }
    evt = from_alertmanager(payload)
    assert evt.source == "prometheus"
    assert evt.service == "api"
    assert "CPU" in evt.summary


def test_systemd_parser_minimal():
    rec = {
        "_SYSTEMD_UNIT": "nginx.service",
        "MESSAGE": "worker process exited",
        "PRIORITY": "3",
        "SYSLOG_IDENTIFIER": "nginx",
    }
    evt = from_journal_record(rec)
    assert evt.source == "systemd"
    assert evt.service == "nginx"
    assert evt.severity in ("warning", "critical", "info")


def test_nginx_parser_minimal():
    rec = {
        "request": "GET /checkout HTTP/1.1",
        "status": 502,
        "upstream_status": "502",
        "request_time": 3.1,
        "upstream_connect_time": 3.0,
    }
    evt = from_log_record(rec)
    assert evt.source == "nginx"
    assert evt.service == "nginx"
    assert "502" in evt.summary


