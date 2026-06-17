# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import time
import requests
from pathlib import Path
from typing import Dict, Optional


class MCPControlAgent:
    """
    Lazy, authenticated MCP lifecycle manager.
    MCP is ONLY touched when L1 escalates.
    """

    def __init__(
        self,
        mcp_url: str = "http://127.0.0.1:8000",
        startup_timeout: int = 30,
    ):
        self.mcp_url = mcp_url.rstrip("/")
        self.startup_timeout = startup_timeout

        # MCP token must exist
        self.mcp_token = os.getenv("MCP_TOKEN")
        if not self.mcp_token:
            raise RuntimeError("MCP_TOKEN environment variable is not set")

        self.headers = {
            "Authorization": f"Bearer {self.mcp_token}"
        }

        self.python_executable = sys.executable
        self.process: Optional[subprocess.Popen] = None
        self._mcp_workdir: Optional[Path] = None

    # --------------------------------------------------
    def _resolve_mcp_workdir(self) -> Path:
        if self._mcp_workdir:
            return self._mcp_workdir

        mcp_dir = os.getenv("MCP_SERVER_DIR")
        if not mcp_dir:
            raise RuntimeError(
                "MCP_SERVER_DIR must be set when L1 escalates.\n"
                "Example:\n"
                "  MCP_SERVER_DIR=C:/path/to/project/root"
            )

        path = Path(mcp_dir).resolve()
        if not path.exists():
            raise RuntimeError(f"MCP server directory not found: {path}")

        self._mcp_workdir = path
        return path

    # --------------------------------------------------
    def _ping(self) -> Dict:
        try:
            r = requests.get(
                f"{self.mcp_url}/logs",
                headers=self.headers,
                timeout=2,
            )
            if r.status_code == 200:
                return {"status": "running", "auth": "ok"}
            if r.status_code == 401:
                return {"status": "running", "auth": "invalid-token"}
            return {"status": "unknown", "http": r.status_code}
        except requests.exceptions.ConnectionError:
            return {"status": "down"}
        except requests.exceptions.Timeout:
            return {"status": "starting"}

    def is_running(self) -> Dict:
        return self._ping()

    # --------------------------------------------------
    # def ensure_running(self) -> Dict:
    #     health = self.is_running()

    #     if health.get("status") == "running" and health.get("auth") == "ok":
    #         return {"status": "running", "action": "none", "auth": "ok"}

    #     if health.get("auth") == "invalid-token":
    #         return {
    #             "status": "running",
    #             "action": "none",
    #             "auth": "invalid-token",
    #             "error": "Invalid MCP_TOKEN",
    #         }

    #     try:
    #         workdir = self._resolve_mcp_workdir()
    #     except RuntimeError as e:
    #         return {"status": "failed", "action": "missing-dir", "error": str(e)}

    #     start_cmd = [
    #         self.python_executable,
    #         "-m", "uvicorn",
    #         "api.main:app",
    #         "--host", "127.0.0.1",
    #         "--port", "8000",
    #     ]

    #     env = dict(os.environ)
    #     env["MCP_TOKEN"] = self.mcp_token

    #     try:
    #         self.process = subprocess.Popen(
    #             start_cmd,
    #             cwd=str(workdir),
    #             env=env,
    #             stdout=None,
    #             stderr=None,
    #             shell=False,
    #         )
    #     except Exception as e:
    #         return {"status": "failed", "action": "spawn-error", "error": str(e)}

    #     start_time = time.time()
    #     while time.time() - start_time < self.startup_timeout:
    #         health = self.is_running()
    #         if health.get("status") == "running":
    #             return {"status": "started", "action": "spawned", "auth": health.get("auth")}
    #         time.sleep(0.5)

    #     return {"status": "failed", "action": "timeout"}

    def ensure_running(self) -> dict:
        """
        Ensure MCP is running. This reproduces exactly:
        python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
        """

        health = self.is_running()

        # MCP already running and authenticated
        if health.get("status") == "running" and health.get("auth") == "ok":
            return {"status": "running", "action": "none", "auth": "ok"}

        # Auth problem → restarting will not help
        if health.get("auth") == "invalid-token":
            return {
                "status": "running",
                "action": "none",
                "auth": "invalid-token",
                "error": "Invalid MCP_TOKEN"
            }

        # ------------------------------------------------------------------
        # ✅ CRITICAL PART: reproduce manual startup EXACTLY
        # ------------------------------------------------------------------

        # Working directory MUST be the project root
        try:
            project_root = Path(os.getenv("MCP_SERVER_DIR")).resolve()
        except Exception:
            return {
                "status": "failed",
                "action": "missing-dir",
                "error": "MCP_SERVER_DIR must point to the project root",
            }

        start_cmd = [
            self.python_executable,
            "-m", "uvicorn",
            "api.main:app",              # ✅ EXACT entrypoint
            "--host", "127.0.0.1",
            "--port", "8000",
        ]

        env = dict(os.environ)
        env["MCP_TOKEN"] = self.mcp_token  # ✅ propagate token

        try:
            self.process = subprocess.Popen(
                start_cmd,
                cwd=str(project_root),     # ✅ CRITICAL
                env=env,
                stdout=None,               # show logs (dev)
                stderr=None,
                shell=False,
            )
        except Exception as e:
            return {
                "status": "failed",
                "action": "spawn-error",
                "error": str(e),
            }

        # Wait for MCP to accept authenticated requests
        start_time = time.time()
        while time.time() - start_time < self.startup_timeout:
            health = self.is_running()
            if health.get("status") == "running":
                return {
                    "status": "started",
                    "action": "spawned",
                    "auth": health.get("auth"),
                }
            time.sleep(0.5)

        return {
            "status": "failed",
            "action": "timeout",
            "auth": "unknown",
        }

    # --------------------------------------------------
    # def shutdown(self) -> Dict:
    #     if self.process and self.process.poll() is None:
    #         self.process.terminate()
    #         self.process.wait(timeout=5)
    #         return {"status": "stopped", "action": "terminated"}
    #     return {"status": "not-running"}

    def shutdown(self) -> dict:
        """
        Gracefully stop MCP by killing the entire process tree.
        This is REQUIRED on Windows for uvicorn.
        """
        if not self.process:
            return {"status": "not-running"}

        if self.process.poll() is None:
            try:
                # Kill process tree
                subprocess.run(
                    ["taskkill", "/PID", str(self.process.pid), "/T", "/F"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=True,
                )
                return {"status": "stopped", "action": "tree-killed"}
            except Exception as e:
                return {"status": "error", "error": str(e)}

        return {"status": "already-stopped"}
