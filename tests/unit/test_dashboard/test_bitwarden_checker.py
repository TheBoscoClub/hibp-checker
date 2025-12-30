"""Unit tests for dashboard/bitwarden_checker.py module.

Tests the BitwardenChecker class including:
- Prerequisite checking
- Task management
- Report handling
- Session management
"""

import json
import os
import sys
import threading
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / 'dashboard'))

from dashboard.bitwarden_checker import BitwardenChecker, BitwardenTask, TaskStatus


class TestTaskStatus:
    """Tests for the TaskStatus enum."""

    def test_pending_status(self):
        """Test PENDING status value."""
        assert TaskStatus.PENDING.value == "pending"

    def test_running_status(self):
        """Test RUNNING status value."""
        assert TaskStatus.RUNNING.value == "running"

    def test_completed_status(self):
        """Test COMPLETED status value."""
        assert TaskStatus.COMPLETED.value == "completed"

    def test_failed_status(self):
        """Test FAILED status value."""
        assert TaskStatus.FAILED.value == "failed"


class TestBitwardenTask:
    """Tests for the BitwardenTask dataclass."""

    def test_create_task(self):
        """Test creating a task."""
        task = BitwardenTask(
            task_id="abc123",
            status=TaskStatus.PENDING,
            started="2024-01-15T10:00:00"
        )

        assert task.task_id == "abc123"
        assert task.status == TaskStatus.PENDING
        assert task.started == "2024-01-15T10:00:00"
        assert task.completed is None
        assert task.progress == 0
        assert task.error is None

    def test_task_to_dict(self):
        """Test converting task to dictionary."""
        task = BitwardenTask(
            task_id="abc123",
            status=TaskStatus.RUNNING,
            started="2024-01-15T10:00:00",
            progress=50,
            total_items=100,
            current_item="Test Site"
        )

        result = task.to_dict()

        assert result['task_id'] == "abc123"
        assert result['status'] == "running"
        assert result['progress'] == 50
        assert result['total_items'] == 100
        assert result['current_item'] == "Test Site"

    def test_task_with_result(self):
        """Test task with completed result."""
        task = BitwardenTask(
            task_id="abc123",
            status=TaskStatus.COMPLETED,
            started="2024-01-15T10:00:00",
            completed="2024-01-15T10:05:00",
            progress=100,
            result={"summary": {"total": 10}}
        )

        result = task.to_dict()

        assert result['status'] == "completed"
        assert result['completed'] == "2024-01-15T10:05:00"
        assert result['result'] == {"summary": {"total": 10}}

    def test_task_with_error(self):
        """Test task with error."""
        task = BitwardenTask(
            task_id="abc123",
            status=TaskStatus.FAILED,
            started="2024-01-15T10:00:00",
            error="Connection failed"
        )

        result = task.to_dict()

        assert result['status'] == "failed"
        assert result['error'] == "Connection failed"


class TestBitwardenCheckerInit:
    """Tests for BitwardenChecker initialization."""

    def test_init_creates_reports_dir(self, temp_dir):
        """Test that initialization creates reports directory."""
        checker = BitwardenChecker(temp_dir)

        assert checker.reports_dir.exists()
        assert checker.reports_dir == temp_dir / 'reports' / 'bitwarden'

    def test_init_sets_base_dir(self, temp_dir):
        """Test that base directory is set correctly."""
        checker = BitwardenChecker(temp_dir)

        assert checker.base_dir == temp_dir

    def test_init_empty_tasks(self, temp_dir):
        """Test that active_tasks starts empty."""
        checker = BitwardenChecker(temp_dir)

        assert checker.active_tasks == {}

    def test_init_creates_lock(self, temp_dir):
        """Test that threading lock is created."""
        checker = BitwardenChecker(temp_dir)

        assert isinstance(checker.lock, type(threading.Lock()))


class TestGetSession:
    """Tests for the _get_session() method."""

    def test_get_session_from_env(self, temp_dir, monkeypatch):
        """Test getting session from environment variable."""
        monkeypatch.setenv('BW_SESSION', 'env_session_token')

        checker = BitwardenChecker(temp_dir)
        session = checker._get_session()

        assert session == 'env_session_token'

    def test_get_session_from_file(self, temp_dir, monkeypatch):
        """Test getting session from session file."""
        monkeypatch.delenv('BW_SESSION', raising=False)

        # Create session file
        session_file = Path.home() / '.bw_session'
        original_exists = session_file.exists()
        original_content = None
        if original_exists:
            original_content = session_file.read_text()

        try:
            session_file.write_text('file_session_token')

            checker = BitwardenChecker(temp_dir)
            # Clear env var that might have been set
            monkeypatch.delenv('BW_SESSION', raising=False)

            session = checker._get_session()

            assert session == 'file_session_token'
        finally:
            # Restore original state
            if original_content:
                session_file.write_text(original_content)
            elif not original_exists and session_file.exists():
                session_file.unlink()

    def test_get_session_none(self, temp_dir, monkeypatch):
        """Test when no session is available."""
        monkeypatch.delenv('BW_SESSION', raising=False)

        # Mock session file to not exist
        with patch.object(Path, 'exists', return_value=False):
            checker = BitwardenChecker(temp_dir)

            # Mock the SESSION_FILE
            checker.SESSION_FILE = temp_dir / 'nonexistent_session'

            session = checker._get_session()

        # Should return None or empty
        assert session is None or session == ''


class TestCheckPrerequisites:
    """Tests for the check_prerequisites() method."""

    def test_prerequisites_all_ok(self, temp_dir, monkeypatch):
        """Test when all prerequisites are met."""
        monkeypatch.setenv('BW_SESSION', 'test_session')

        checker = BitwardenChecker(temp_dir)

        with patch('subprocess.run') as mock_run:
            # Mock 'which bw' success
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout=json.dumps({"status": "unlocked"}),
                stderr=""
            )

            result = checker.check_prerequisites()

        assert result['bw_installed'] is True
        assert result['bw_session_set'] is True
        assert result['vault_unlocked'] is True
        assert result['errors'] == []

    def test_prerequisites_no_session(self, temp_dir, monkeypatch):
        """Test when BW_SESSION is not set."""
        monkeypatch.delenv('BW_SESSION', raising=False)

        checker = BitwardenChecker(temp_dir)
        checker.SESSION_FILE = temp_dir / 'nonexistent'

        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0)

            result = checker.check_prerequisites()

        assert result['bw_session_set'] is False
        assert len(result['errors']) > 0

    def test_prerequisites_bw_not_installed(self, temp_dir, monkeypatch):
        """Test when Bitwarden CLI is not installed."""
        monkeypatch.setenv('BW_SESSION', 'test_session')

        checker = BitwardenChecker(temp_dir)

        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=1)

            result = checker.check_prerequisites()

        assert result['bw_installed'] is False

    def test_prerequisites_vault_locked(self, temp_dir, monkeypatch):
        """Test when vault is locked."""
        monkeypatch.setenv('BW_SESSION', 'test_session')

        checker = BitwardenChecker(temp_dir)

        with patch('subprocess.run') as mock_run:
            # First call for 'which bw'
            # Second call for 'bw status'
            mock_run.side_effect = [
                MagicMock(returncode=0),  # which bw
                MagicMock(
                    returncode=0,
                    stdout=json.dumps({"status": "locked"}),
                    stderr=""
                )  # bw status
            ]

            result = checker.check_prerequisites()

        assert result['vault_unlocked'] is False


class TestStartCheck:
    """Tests for the start_check() method."""

    def test_start_check_returns_task_id(self, temp_dir, monkeypatch):
        """Test that start_check returns a task ID."""
        monkeypatch.setenv('BW_SESSION', 'test_session')

        checker = BitwardenChecker(temp_dir)

        with patch.object(checker, '_run_check'):
            task_id = checker.start_check()

        assert task_id is not None
        assert len(task_id) == 8  # UUID first 8 chars

    def test_start_check_creates_task(self, temp_dir, monkeypatch):
        """Test that start_check creates a task in active_tasks."""
        monkeypatch.setenv('BW_SESSION', 'test_session')

        checker = BitwardenChecker(temp_dir)

        with patch.object(checker, '_run_check'):
            task_id = checker.start_check()

        assert task_id in checker.active_tasks
        assert checker.active_tasks[task_id].status == TaskStatus.PENDING

    def test_start_check_starts_thread(self, temp_dir, monkeypatch):
        """Test that start_check starts a background thread."""
        monkeypatch.setenv('BW_SESSION', 'test_session')

        checker = BitwardenChecker(temp_dir)

        with patch('threading.Thread') as mock_thread:
            mock_thread.return_value = MagicMock()

            checker.start_check()

            mock_thread.assert_called_once()
            mock_thread.return_value.start.assert_called_once()


class TestGetTaskStatus:
    """Tests for the get_task_status() method."""

    def test_get_task_status_exists(self, temp_dir):
        """Test getting status of existing task."""
        checker = BitwardenChecker(temp_dir)

        # Add a task manually
        task = BitwardenTask(
            task_id="test123",
            status=TaskStatus.RUNNING,
            started="2024-01-15T10:00:00",
            progress=50
        )
        checker.active_tasks["test123"] = task

        result = checker.get_task_status("test123")

        assert result['task_id'] == "test123"
        assert result['status'] == "running"
        assert result['progress'] == 50

    def test_get_task_status_not_found(self, temp_dir):
        """Test getting status of non-existent task."""
        checker = BitwardenChecker(temp_dir)

        result = checker.get_task_status("nonexistent")

        assert result is None


class TestSaveReport:
    """Tests for the _save_report() method."""

    def test_save_report_creates_file(self, temp_dir):
        """Test that save_report creates a JSON file."""
        checker = BitwardenChecker(temp_dir)

        result = {
            "summary": {"total": 10, "safe": 8, "compromised": 2},
            "items": []
        }

        checker._save_report("task123", result)

        # Check that file was created
        files = list(checker.reports_dir.glob("*.json"))
        assert len(files) == 1

    def test_save_report_content(self, temp_dir):
        """Test that saved report has correct content."""
        checker = BitwardenChecker(temp_dir)

        result = {
            "summary": {"total": 10},
            "items": []
        }

        checker._save_report("task123", result)

        files = list(checker.reports_dir.glob("*.json"))
        with open(files[0]) as f:
            data = json.load(f)

        assert data['task_id'] == "task123"
        assert 'generated' in data
        assert data['summary'] == {"total": 10}


class TestCleanupOldReports:
    """Tests for the _cleanup_old_reports() method."""

    def test_cleanup_keeps_recent(self, temp_dir):
        """Test that cleanup keeps recent reports."""
        checker = BitwardenChecker(temp_dir)

        # Create 5 reports
        for i in range(5):
            report_file = checker.reports_dir / f"report_{i}.json"
            report_file.write_text(json.dumps({"id": i}))

        checker._cleanup_old_reports(keep=10)

        files = list(checker.reports_dir.glob("*.json"))
        assert len(files) == 5

    def test_cleanup_removes_old(self, temp_dir):
        """Test that cleanup removes old reports."""
        checker = BitwardenChecker(temp_dir)

        # Create 15 reports
        for i in range(15):
            report_file = checker.reports_dir / f"report_{i:02d}.json"
            report_file.write_text(json.dumps({"id": i}))
            # Touch file to set mtime (older files first)

        checker._cleanup_old_reports(keep=10)

        files = list(checker.reports_dir.glob("*.json"))
        assert len(files) == 10


class TestGetLatestReport:
    """Tests for the get_latest_report() method."""

    def test_get_latest_report_exists(self, temp_dir):
        """Test getting latest report when reports exist."""
        checker = BitwardenChecker(temp_dir)

        # Create a report
        report_data = {"summary": {"total": 10}}
        report_file = checker.reports_dir / "report_latest.json"
        report_file.write_text(json.dumps(report_data))

        result = checker.get_latest_report()

        assert result is not None
        assert result['summary']['total'] == 10

    def test_get_latest_report_empty(self, temp_dir):
        """Test getting latest report when none exist."""
        checker = BitwardenChecker(temp_dir)

        result = checker.get_latest_report()

        assert result is None


class TestGetAllReports:
    """Tests for the get_all_reports() method."""

    def test_get_all_reports(self, temp_dir):
        """Test getting all reports."""
        checker = BitwardenChecker(temp_dir)

        # Create multiple reports
        for i in range(3):
            report_file = checker.reports_dir / f"report_{i}.json"
            report_file.write_text(json.dumps({
                "generated": f"2024-01-{15+i}T10:00:00",
                "summary": {"total": i * 10}
            }))

        result = checker.get_all_reports()

        assert len(result) == 3
        assert all('filename' in r for r in result)
        assert all('generated' in r for r in result)
        assert all('summary' in r for r in result)

    def test_get_all_reports_empty(self, temp_dir):
        """Test getting reports when none exist."""
        checker = BitwardenChecker(temp_dir)

        result = checker.get_all_reports()

        assert result == []


class TestGetReportByFilename:
    """Tests for the get_report_by_filename() method."""

    def test_get_report_by_filename_exists(self, temp_dir):
        """Test getting report by filename."""
        checker = BitwardenChecker(temp_dir)

        # Create a report
        report_data = {"summary": {"total": 10}}
        report_file = checker.reports_dir / "test_report.json"
        report_file.write_text(json.dumps(report_data))

        result = checker.get_report_by_filename("test_report.json")

        assert result is not None
        assert result['summary']['total'] == 10

    def test_get_report_by_filename_not_found(self, temp_dir):
        """Test getting non-existent report."""
        checker = BitwardenChecker(temp_dir)

        result = checker.get_report_by_filename("nonexistent.json")

        assert result is None

    def test_get_report_by_filename_path_traversal(self, temp_dir):
        """Test that path traversal is prevented."""
        checker = BitwardenChecker(temp_dir)

        # Try path traversal
        result = checker.get_report_by_filename("../../../etc/passwd")

        assert result is None

    def test_get_report_by_filename_wrong_extension(self, temp_dir):
        """Test that non-JSON files are rejected."""
        checker = BitwardenChecker(temp_dir)

        # Create a text file
        text_file = checker.reports_dir / "test.txt"
        text_file.write_text("not json")

        result = checker.get_report_by_filename("test.txt")

        assert result is None


class TestRunCheck:
    """Tests for the _run_check() method."""

    def test_run_check_success(self, temp_dir, monkeypatch):
        """Test successful password check run."""
        monkeypatch.setenv('BW_SESSION', 'test_session')

        checker = BitwardenChecker(temp_dir)

        # Create the task
        task = BitwardenTask(
            task_id="test123",
            status=TaskStatus.PENDING,
            started=datetime.now().isoformat()
        )
        checker.active_tasks["test123"] = task

        # Create a mock script
        script_path = temp_dir / 'bw-hibp-stream.py'
        script_path.write_text("# mock script")

        mock_output = json.dumps({
            "summary": {"total": 10, "safe": 8, "compromised": 2},
            "items": []
        })

        with patch('subprocess.Popen') as mock_popen:
            # Mock bw process
            mock_bw_proc = MagicMock()
            mock_bw_proc.stdout = MagicMock()

            # Mock hibp process
            mock_hibp_proc = MagicMock()
            mock_hibp_proc.communicate.return_value = (mock_output, "")
            mock_hibp_proc.returncode = 0

            mock_popen.side_effect = [mock_bw_proc, mock_hibp_proc]

            checker._run_check("test123")

        assert task.status == TaskStatus.COMPLETED
        assert task.result is not None
        assert task.progress == 100

    def test_run_check_failure(self, temp_dir, monkeypatch):
        """Test failed password check run."""
        monkeypatch.setenv('BW_SESSION', 'test_session')

        checker = BitwardenChecker(temp_dir)

        task = BitwardenTask(
            task_id="test123",
            status=TaskStatus.PENDING,
            started=datetime.now().isoformat()
        )
        checker.active_tasks["test123"] = task

        script_path = temp_dir / 'bw-hibp-stream.py'
        script_path.write_text("# mock script")

        with patch('subprocess.Popen') as mock_popen:
            mock_bw_proc = MagicMock()
            mock_bw_proc.stdout = MagicMock()

            mock_hibp_proc = MagicMock()
            mock_hibp_proc.communicate.return_value = ("", "Error occurred")
            mock_hibp_proc.returncode = 1

            mock_popen.side_effect = [mock_bw_proc, mock_hibp_proc]

            checker._run_check("test123")

        assert task.status == TaskStatus.FAILED
        assert task.error is not None

    def test_run_check_script_not_found(self, temp_dir, monkeypatch):
        """Test when script file is not found."""
        monkeypatch.setenv('BW_SESSION', 'test_session')

        checker = BitwardenChecker(temp_dir)

        task = BitwardenTask(
            task_id="test123",
            status=TaskStatus.PENDING,
            started=datetime.now().isoformat()
        )
        checker.active_tasks["test123"] = task

        # Don't create the script file

        with patch('subprocess.Popen') as mock_popen:
            mock_popen.side_effect = FileNotFoundError("Script not found")

            checker._run_check("test123")

        assert task.status == TaskStatus.FAILED
        assert "not found" in task.error.lower()
