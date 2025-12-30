"""Bitwarden HIBP Password Checker Integration Module

Provides subprocess management and task tracking for running bw-hibp-stream.py
from the web dashboard.
"""

import os
import subprocess
import json
import uuid
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum


class TaskStatus(Enum):
    """Enumeration of possible states for a Bitwarden password check task.

    Attributes:
        PENDING: Task has been created but not yet started.
        RUNNING: Task is currently executing the password check.
        COMPLETED: Task finished successfully with results.
        FAILED: Task encountered an error and did not complete.
    """

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class BitwardenTask:
    """Represents a background task for checking Bitwarden passwords against HIBP.

    Tracks the lifecycle and results of an asynchronous password check operation,
    from creation through completion or failure.

    Attributes:
        task_id: Unique identifier for this task (8-character UUID).
        status: Current state of the task (pending, running, completed, failed).
        started: ISO format timestamp when the task was created.
        completed: ISO format timestamp when the task finished (None if still running).
        progress: Percentage of completion (0-100).
        total_items: Total number of password items to check.
        current_item: Name of the item currently being checked.
        result: Dict containing check results when completed successfully.
        error: Error message if the task failed.
    """

    task_id: str
    status: TaskStatus
    started: str
    completed: Optional[str] = None
    progress: int = 0
    total_items: int = 0
    current_item: str = ""
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary representation for JSON serialization."""
        return {
            'task_id': self.task_id,
            'status': self.status.value,
            'started': self.started,
            'completed': self.completed,
            'progress': self.progress,
            'total_items': self.total_items,
            'current_item': self.current_item,
            'result': self.result,
            'error': self.error
        }


class BitwardenChecker:
    """Manages Bitwarden CLI integration for HIBP password checking.

    Provides methods to check prerequisites, start background password checks,
    track task progress, and manage saved reports. Uses threading for non-blocking
    operations when invoked from the web dashboard.

    Attributes:
        SESSION_FILE: Path to persistent Bitwarden session token file (~/.bw_session).
        base_dir: Base directory of the HIBP project.
        reports_dir: Directory where Bitwarden HIBP reports are stored.
        active_tasks: Dict mapping task IDs to their BitwardenTask objects.
        lock: Threading lock for thread-safe task management.
    """

    # Path to persistent session file
    SESSION_FILE = Path.home() / '.bw_session'

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.reports_dir = base_dir / 'reports' / 'bitwarden'
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.active_tasks: Dict[str, BitwardenTask] = {}
        self.lock = threading.Lock()

    def _get_session(self) -> Optional[str]:
        """Get BW_SESSION from environment or persistent file."""
        # First check environment variable
        session = os.environ.get('BW_SESSION')
        if session:
            return session

        # Fall back to session file
        if self.SESSION_FILE.exists():
            try:
                session = self.SESSION_FILE.read_text().strip()
                if session:
                    # Also set in environment for subprocess calls
                    os.environ['BW_SESSION'] = session
                    return session
            except Exception:
                pass
        return None

    def check_prerequisites(self) -> Dict[str, Any]:
        """Check if Bitwarden CLI and session are available."""
        result = {
            'bw_installed': False,
            'bw_session_set': False,
            'vault_unlocked': False,
            'errors': []
        }

        # Check BW_SESSION (env var or session file)
        if self._get_session():
            result['bw_session_set'] = True
        else:
            result['errors'].append('BW_SESSION not found. Run: bw unlock --raw > ~/.bw_session')

        # Check bw CLI
        try:
            proc = subprocess.run(['which', 'bw'], capture_output=True, timeout=5)
            result['bw_installed'] = proc.returncode == 0
            if not result['bw_installed']:
                result['errors'].append('Bitwarden CLI (bw) not found. Install from: https://bitwarden.com/help/cli/')
        except Exception:
            result['errors'].append('Could not check for Bitwarden CLI')

        # Check vault status if session is set
        if result['bw_session_set'] and result['bw_installed']:
            try:
                proc = subprocess.run(
                    ['bw', 'status'],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    env={**os.environ}
                )
                if proc.returncode == 0:
                    status = json.loads(proc.stdout)
                    vault_status = status.get('status', 'unknown')
                    result['vault_unlocked'] = vault_status == 'unlocked'
                    if not result['vault_unlocked']:
                        result['errors'].append(f'Bitwarden vault is {vault_status}. Run: bw unlock')
            except json.JSONDecodeError:
                result['errors'].append('Could not parse Bitwarden status')
            except subprocess.TimeoutExpired:
                result['errors'].append('Bitwarden status check timed out')
            except Exception as e:
                result['errors'].append(f'Could not check vault status: {str(e)}')

        return result

    def start_check(self) -> str:
        """Start a new password check. Returns task_id."""
        task_id = str(uuid.uuid4())[:8]
        task = BitwardenTask(
            task_id=task_id,
            status=TaskStatus.PENDING,
            started=datetime.now().isoformat()
        )

        with self.lock:
            self.active_tasks[task_id] = task

        # Start background thread
        thread = threading.Thread(target=self._run_check, args=(task_id,), daemon=True)
        thread.start()

        return task_id

    def _run_check(self, task_id: str):
        """Background thread to run the password check."""
        task = self.active_tasks[task_id]
        task.status = TaskStatus.RUNNING

        try:
            script_path = self.base_dir / 'bw-hibp-stream.py'

            # Run: bw list items | python bw-hibp-stream.py --report json --quiet
            bw_proc = subprocess.Popen(
                ['bw', 'list', 'items'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env={**os.environ}
            )

            hibp_proc = subprocess.Popen(
                ['python3', str(script_path), '--report', 'json', '--quiet'],
                stdin=bw_proc.stdout,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Allow bw_proc to receive SIGPIPE if hibp_proc exits
            bw_proc.stdout.close()

            stdout, stderr = hibp_proc.communicate(timeout=600)  # 10 min timeout

            if hibp_proc.returncode == 0 and stdout.strip():
                result = json.loads(stdout)
                task.result = result
                task.status = TaskStatus.COMPLETED
                task.progress = 100
                task.total_items = result.get('summary', {}).get('total', 0)

                # Save to file
                self._save_report(task_id, result)
            else:
                task.status = TaskStatus.FAILED
                task.error = stderr.strip() if stderr.strip() else 'No output from password check'

        except subprocess.TimeoutExpired:
            task.status = TaskStatus.FAILED
            task.error = 'Check timed out after 10 minutes'
            # Kill processes
            try:
                hibp_proc.kill()
                bw_proc.kill()
            except Exception:
                pass
        except json.JSONDecodeError as e:
            task.status = TaskStatus.FAILED
            task.error = f'Invalid JSON response: {str(e)}'
        except FileNotFoundError:
            task.status = TaskStatus.FAILED
            task.error = 'bw-hibp-stream.py script not found'
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
        finally:
            task.completed = datetime.now().isoformat()

    def _save_report(self, task_id: str, result: Dict[str, Any]):
        """Save report to JSON file."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'bitwarden_hibp_{timestamp}.json'
        filepath = self.reports_dir / filename

        report = {
            'task_id': task_id,
            'generated': datetime.now().isoformat(),
            **result
        }

        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)

        # Cleanup old reports (keep last 10)
        self._cleanup_old_reports()

    def _cleanup_old_reports(self, keep: int = 10):
        """Remove old reports, keeping only the most recent."""
        reports = sorted(
            self.reports_dir.glob('*.json'),
            key=lambda p: p.stat().st_mtime
        )
        for old_report in reports[:-keep] if len(reports) > keep else []:
            try:
                old_report.unlink()
            except Exception:
                pass

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a running or completed task."""
        with self.lock:
            task = self.active_tasks.get(task_id)
            if task:
                return task.to_dict()
        return None

    def get_latest_report(self) -> Optional[Dict[str, Any]]:
        """Get the most recent saved report."""
        reports = sorted(
            self.reports_dir.glob('*.json'),
            key=lambda p: p.stat().st_mtime
        )
        if reports:
            try:
                with open(reports[-1]) as f:
                    return json.load(f)
            except Exception:
                pass
        return None

    def get_all_reports(self) -> list:
        """Get metadata for all saved reports."""
        reports = []
        for filepath in sorted(
            self.reports_dir.glob('*.json'),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        ):
            try:
                with open(filepath) as f:
                    data = json.load(f)
                    reports.append({
                        'filename': filepath.name,
                        'generated': data.get('generated'),
                        'summary': data.get('summary', {})
                    })
            except Exception:
                continue
        return reports

    def get_report_by_filename(self, filename: str) -> Optional[Dict[str, Any]]:
        """Get a specific report by filename."""
        # Sanitize filename to prevent path traversal
        safe_filename = Path(filename).name
        filepath = self.reports_dir / safe_filename

        if filepath.exists() and filepath.suffix == '.json':
            try:
                with open(filepath) as f:
                    return json.load(f)
            except Exception:
                pass
        return None
