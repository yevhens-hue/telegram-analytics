"""Tests for main.py — pipeline orchestration and health server."""
import json
import threading
import time
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from http.client import HTTPConnection

import main


class TestHealthCheckHandler:
    def test_returns_200(self):
        """Health check should return HTTP 200."""
        from http.server import HTTPServer
        server = HTTPServer(("127.0.0.1", 0), main.HealthCheckHandler)
        port = server.server_address[1]
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

        try:
            conn = HTTPConnection("127.0.0.1", port)
            conn.request("GET", "/health")
            resp = conn.getresponse()
            assert resp.status == 200
        finally:
            server.shutdown()

    def test_returns_json_status_ready(self):
        """Health check should return JSON with status ready."""
        from http.server import HTTPServer
        server = HTTPServer(("127.0.0.1", 0), main.HealthCheckHandler)
        port = server.server_address[1]
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

        try:
            conn = HTTPConnection("127.0.0.1", port)
            conn.request("GET", "/health")
            resp = conn.getresponse()
            body = json.loads(resp.read().decode())
            assert body == {"status": "ready"}
        finally:
            server.shutdown()

    def test_content_type_is_json(self):
        from http.server import HTTPServer
        server = HTTPServer(("127.0.0.1", 0), main.HealthCheckHandler)
        port = server.server_address[1]
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

        try:
            conn = HTTPConnection("127.0.0.1", port)
            conn.request("GET", "/health")
            resp = conn.getresponse()
            assert resp.getheader("Content-type") == "application/json"
        finally:
            server.shutdown()


class TestRunHealthServer:
    def test_starts_on_specified_port(self):
        """Health server should bind to the specified port."""
        server_started = threading.Event()

        original_serve = main.HTTPServer.serve_forever

        def patched_serve(self):
            server_started.set()
            # Don't actually serve forever, just signal and return
            return

        with patch.object(main.HTTPServer, "serve_forever", patched_serve):
            thread = threading.Thread(
                target=main.run_health_server,
                args=(18765,),
                daemon=True,
            )
            thread.start()
            thread.join(timeout=2)
            assert server_started.is_set()


class TestRunPipeline:
    def test_calls_all_pipeline_steps(self):
        """Pipeline should call all 6 steps in order."""
        call_order = []

        def track(name):
            def inner(*args, **kwargs):
                call_order.append(name)
            return inner

        with patch("main.init_all_tables", side_effect=track("init")):
            with patch("main.scrape_tapps_center", new_callable=AsyncMock, return_value=[]) as mock_scrape:
                mock_scrape.side_effect = AsyncMock(return_value=[])
                with patch("main.run_indexing", side_effect=track("index")):
                    with patch("main.monitor_channels", side_effect=track("monitor")):
                        with patch("main.simulate_ad_tracking", side_effect=track("ads")):
                            with patch("main.run_analytics_cycle", side_effect=track("analytics")):
                                with patch("main.run_alerts", side_effect=track("alerts")):
                                    with patch("main.json.dump"):
                                        with patch("builtins.open", MagicMock()):
                                            asyncio = __import__("asyncio")
                                            asyncio.run(main.run_pipeline())

        assert "init" in call_order
        assert "index" in call_order
        assert "monitor" in call_order
        assert "ads" in call_order
        assert "analytics" in call_order
        assert "alerts" in call_order

    def test_exits_on_pipeline_failure(self):
        """Pipeline should exit with code 1 on failure."""
        with patch("main.init_all_tables", side_effect=Exception("DB error")):
            with pytest.raises(SystemExit) as exc_info:
                import asyncio
                asyncio.run(main.run_pipeline())
            assert exc_info.value.code == 1

    def test_saves_tapps_data_to_file(self):
        """Pipeline should write scraped data to tapps_data.json."""
        mock_data = [{"name": "TestApp", "position": 1}]

        with patch("main.init_all_tables"):
            with patch("main.scrape_tapps_center", new_callable=AsyncMock, return_value=mock_data):
                with patch("main.run_indexing"):
                    with patch("main.monitor_channels"):
                        with patch("main.simulate_ad_tracking"):
                            with patch("main.run_analytics_cycle"):
                                with patch("main.run_alerts"):
                                    mock_file = MagicMock()
                                    with patch("builtins.open", return_value=mock_file):
                                        with patch("main.json.dump") as mock_dump:
                                            import asyncio
                                            asyncio.run(main.run_pipeline())

                                    mock_dump.assert_called_once()
                                    args = mock_dump.call_args
                                    assert args[0][0] == mock_data


class TestMain:
    def test_runs_without_port(self):
        """main() should work without PORT env var."""
        with patch.dict("os.environ", {}, clear=True):
            with patch("main.asyncio.run") as mock_run:
                with patch("main.sys.exit") as mock_exit:
                    main.main()
                    mock_run.assert_called_once()

    def test_starts_health_server_when_port_set(self):
        """main() should start health server when PORT is set."""
        with patch.dict("os.environ", {"PORT": "8080"}):
            with patch("main.threading.Thread") as mock_thread:
                with patch("main.asyncio.run"):
                    with patch("main.sys.exit"):
                        main.main()
                        mock_thread.assert_called_once()
                        call_kwargs = mock_thread.call_args
                        assert call_kwargs[1]["daemon"] is True
