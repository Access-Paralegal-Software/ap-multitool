# apmultitool_qt/telemetry.py

"""Telemetry Management module for APMultitool Qt."""

import os
import json
import threading
from datetime import datetime
from core import __version__, __channel__

# Telemetry file saved to user's home folder (matches security license file strategy)
TELEMETRY_FILE = os.path.join(os.path.expanduser("~"), ".access_paralegal_telemetry.json")

class TelemetryManager:
    """Manages tracking, aggregation, and persistent logging of job failure/success metrics."""
    def __init__(self):
        self._lock = threading.Lock()
        self.stats = {
            "build_id": f"v{__version__}{__channel__}",
            "total_runs": 0,
            "success_runs": 0,
            "failed_runs": 0,
            "cancelled_runs": 0,
            "operations": {
                "merge": {"total": 0, "success": 0, "failed": 0, "cancelled": 0},
                "bates_stamp": {"total": 0, "success": 0, "failed": 0, "cancelled": 0},
                "folder_tree": {"total": 0, "success": 0, "failed": 0, "cancelled": 0}
            },
            "last_error": "",
            "last_error_time": ""
        }
        self.load()

    def load(self):
        """Loads telemetry logs from the local filesystem."""
        with self._lock:
            current_build = f"v{__version__}{__channel__}"
            self.stats["build_id"] = current_build
            if os.path.exists(TELEMETRY_FILE):
                try:
                    with open(TELEMETRY_FILE, 'r') as f:
                        data = json.load(f)
                        # Deep merge to maintain default values in case of schema update
                        for k, v in data.items():
                            if k in self.stats:
                                if isinstance(v, dict) and isinstance(self.stats[k], dict):
                                    self.stats[k].update(v)
                                else:
                                    self.stats[k] = v
                        # Force overwrite with current build ID
                        self.stats["build_id"] = current_build
                except Exception:
                    pass

    def save(self):
        """Persists telemetry logs safely to the local filesystem."""
        with self._lock:
            try:
                # Ensure the folder structure is present
                os.makedirs(os.path.dirname(TELEMETRY_FILE), exist_ok=True)
                with open(TELEMETRY_FILE, 'w') as f:
                    json.dump(self.stats, f, indent=4)
            except Exception:
                pass

    def log_job_started(self, operation: str):
        """Registers a job start for the given operation type."""
        # Normalize operation if unrecognized
        if not operation:
            operation = "unknown"
            
        with self._lock:
            if operation not in self.stats["operations"]:
                self.stats["operations"][operation] = {"total": 0, "success": 0, "failed": 0, "cancelled": 0}
            
            self.stats["total_runs"] += 1
            self.stats["operations"][operation]["total"] += 1
            
        # Save outside of manual lock to avoid nesting
        self.save()

    def log_job_finished(self, operation: str, success: bool, cancelled: bool, error_msg: str = ""):
        """Registers a job finish outcome with details of success, cancellation, or failure."""
        if not operation:
            operation = "unknown"
            
        with self._lock:
            if operation not in self.stats["operations"]:
                self.stats["operations"][operation] = {"total": 0, "success": 0, "failed": 0, "cancelled": 0}
            
            ops_stats = self.stats["operations"][operation]
            
            if success:
                self.stats["success_runs"] += 1
                ops_stats["success"] += 1
            elif cancelled or error_msg == "Operation cancelled.":
                self.stats["cancelled_runs"] += 1
                ops_stats["cancelled"] += 1
            else:
                self.stats["failed_runs"] += 1
                ops_stats["failed"] += 1
                self.stats["last_error"] = error_msg
                self.stats["last_error_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
        self.save()

    def get_success_rate(self) -> float:
        """Computes the current success rate percentage, ignoring active cancellations."""
        with self._lock:
            # Exclude cancellations to measure actual software failure rate
            denom = self.stats["success_runs"] + self.stats["failed_runs"]
            if denom == 0:
                return 100.0
            return (self.stats["success_runs"] / denom) * 100.0

    def reset(self):
        """Resets all aggregated metrics back to zeroes."""
        with self._lock:
            self.stats = {
                "build_id": f"v{__version__}{__channel__}",
                "total_runs": 0,
                "success_runs": 0,
                "failed_runs": 0,
                "cancelled_runs": 0,
                "operations": {
                    "merge": {"total": 0, "success": 0, "failed": 0, "cancelled": 0},
                    "bates_stamp": {"total": 0, "success": 0, "failed": 0, "cancelled": 0},
                    "folder_tree": {"total": 0, "success": 0, "failed": 0, "cancelled": 0}
                },
                "last_error": "",
                "last_error_time": ""
            }
        self.save()

# Global singleton instance
telemetry_manager = TelemetryManager()
