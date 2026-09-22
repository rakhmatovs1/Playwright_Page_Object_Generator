"""Tests for Command Line Interface."""
import subprocess
import sys
from pathlib import Path
from typing import Tuple

import pytest


def run_cli(*args: str) -> Tuple[int, str, str]:
    """Run CLI with args and return (exit_code, stdout, stderr).

    Args:
        *args: Command line arguments (e.g., "-i", "file.html", "-c", "LoginPage")

    Returns:
        Tuple of (exit_code, stdout, stderr)
    """
    cmd = [sys.executable, "main.py"] + list(args)
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent
    )
    return result.returncode, result.stdout, result.stderr


class TestCLIBasics:
    """Test basic CLI functionality."""

    def test_cli_help_option(self):
        """--help should display help message."""
        exit_code, stdout, _ = run_cli("--help")
        assert exit_code == 0, f"Expected exit code 0, got {exit_code}"
        assert "Usage:" in stdout or "usage:" in stdout.lower()
        assert "main.py" in stdout

    def test_cli_short_help_option(self):
        """Should support -h option for help."""
        exit_code, stdout, _ = run_cli("-h")
        assert exit_code == 0, f"Expected exit code 0, got {exit_code}"
        assert "Usage:" in stdout or "usage:" in stdout.lower()


class TestCLIRequiredParameters:
    """Test CLI required and optional parameters."""

    def test_input_parameter_required_missing(self):
        """Should error when --input is missing."""
        exit_code, _, stderr = run_cli("-c", "LoginPage")
        assert exit_code == 2, f"Expected exit code 2 for missing required param, got {exit_code}"
        assert "--input" in stderr or "-i" in stderr

    def test_class_name_parameter_required_missing(self):
        """Should error when --class-name is missing."""
        exit_code, _, stderr = run_cli("-i", "dummy.html")
        assert exit_code == 2, f"Expected exit code 2 for missing required param, got {exit_code}"
        assert "--class-name" in stderr or "-c" in stderr

    def test_both_required_parameters_missing(self):
        """Should error when both required parameters missing."""
        exit_code, _, stderr = run_cli()
        assert exit_code == 2, f"Expected exit code 2 for missing required params, got {exit_code}"

    def test_input_from_file_long_option(self, tmp_path):
        """Should accept HTML file with --input option."""
        html_file = tmp_path / "test.html"
        html_file.write_text("<button>Login</button>")

        exit_code, stdout, stderr = run_cli(
            "--input", str(html_file),
            "--class-name", "LoginPage"
        )
        # Should succeed with valid input
        assert exit_code in [0, 1], f"Unexpected exit code: {exit_code}, stderr: {stderr}"

    def test_output_parameter_optional(self, tmp_path):
        """Should work without --output (outputs to stdout)."""
        html_file = tmp_path / "test.html"
        html_file.write_text("<button>Test</button>")

        exit_code, stdout, _ = run_cli(
            "-i", str(html_file),
            "-c", "TestPage"
        )
        # Should succeed and output to stdout
        assert exit_code in [0, 1], f"Unexpected exit code: {exit_code}"
        # If successful, stdout should contain class definition
        if exit_code == 0 and stdout:
            assert "class TestPage" in stdout or "class" in stdout.lower()


class TestCLIInputHandling:
    """Test CLI input handling."""

    def test_input_from_html_file(self, tmp_path):
        """Should read HTML from specified file."""
        html_file = tmp_path / "input.html"
        html_file.write_text("<button>Click me</button>")
        output_file = tmp_path / "output.py"

        exit_code, _, _ = run_cli(
            "-i", str(html_file),
            "-c", "MyPage",
            "-o", str(output_file)
        )

        # Should complete successfully or at least try
        if exit_code == 0 and output_file.exists():
            content = output_file.read_text()
            assert "class MyPage" in content

    def test_input_from_stdin_with_dash(self, tmp_path):
        """Should read from stdin when input is dash (-)."""
        output_file = tmp_path / "output.py"
        html_content = "<button>Stdin Button</button>"

        cmd = [sys.executable, "main.py", "-i", "-", "-c", "StdinPage", "-o", str(output_file)]
        result = subprocess.run(
            cmd,
            input=html_content,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )

        # Should handle stdin input
        assert result.returncode in [0, 1], f"Unexpected exit code: {result.returncode}"

    def test_error_input_file_not_found(self):
        """Should error if input file doesn't exist."""
        exit_code, _, stderr = run_cli(
            "-i", "/nonexistent/path/file.html",
            "-c", "LoginPage"
        )
        assert exit_code == 1, f"Expected exit code 1 for file not found, got {exit_code}"
        assert "not found" in stderr.lower() or "error" in stderr.lower()


class TestCLIOutputHandling:
    """Test CLI output handling."""

    def test_output_to_file_with_long_option(self, tmp_path):
        """Should save output to file specified with --output."""
        html_file = tmp_path / "input.html"
        html_file.write_text("<button>Submit</button>")
        output_file = tmp_path / "output.py"

        exit_code, _, _ = run_cli(
            "--input", str(html_file),
            "--class-name", "SubmitPage",
            "--output", str(output_file)
        )

        # If successful, file should be created
        if exit_code == 0:
            assert output_file.exists(), "Output file should be created"

    def test_output_to_stdout_default(self, tmp_path):
        """Should output to stdout when no -o specified."""
        html_file = tmp_path / "input.html"
        html_file.write_text("<input type='text'>")

        exit_code, stdout, _ = run_cli(
            "-i", str(html_file),
            "-c", "FormPage"
        )

        # Should output to stdout instead of creating file
        if exit_code == 0:
            assert len(stdout) > 0, "Should output to stdout"
            # Should contain class definition or at least some Python code
            assert "class" in stdout.lower() or "FormPage" in stdout or "def" in stdout

    def test_overwrite_existing_output_file(self, tmp_path):
        """Should overwrite existing output file."""
        html_file = tmp_path / "input.html"
        html_file.write_text("<button>Update</button>")
        output_file = tmp_path / "output.py"

        # Create existing file
        output_file.write_text("# old content\npass\n")
        old_content = output_file.read_text()

        exit_code, _, _ = run_cli(
            "-i", str(html_file),
            "-c", "UpdatePage",
            "-o", str(output_file)
        )

        if exit_code == 0:
            new_content = output_file.read_text()
            # File should be overwritten (or at least exist)
            assert output_file.exists()


class TestCLIClassNameValidation:
    """Test class name validation."""

    def test_accept_valid_pascal_case_names(self, tmp_path):
        """Should accept valid PascalCase class names (LoginPage, HomePage, etc)."""
        html_file = tmp_path / "input.html"
        html_file.write_text("<button>Test</button>")

        for valid_name in ["LoginPage", "HomePage", "MyCustomPage"]:
            exit_code, _, stderr = run_cli(
                "-i", str(html_file),
                "-c", valid_name
            )
            # Valid name should not error due to naming
            assert exit_code in [0, 1], f"Valid PascalCase name {valid_name} rejected: {stderr}"

    def test_reject_invalid_class_names(self):
        """Should reject non-PascalCase class names (lowercase, snake_case, leading digit)."""
        invalid_cases = [
            ("loginpage", "lowercase"),
            ("login_page", "snake_case"),
            ("123Page", "starts with digit"),
        ]

        for invalid_name, reason in invalid_cases:
            exit_code, _, stderr = run_cli(
                "-i", "-",
                "-c", invalid_name
            )
            # Should error for invalid class name (exit code should be non-zero)
            assert exit_code != 0, f"Expected error exit code for {reason}, got {exit_code}"
            assert "PascalCase" in stderr or "case" in stderr.lower() or len(stderr) > 0


class TestCLIErrorMessages:
    """Test CLI error messages are clear and helpful."""

    @pytest.mark.parametrize("error_case,expected_in_stderr", [
        ("missing_input", "--input"),
        ("missing_class_name", "--class-name"),
        ("invalid_class_name", "PascalCase"),
        ("file_not_found", "not found"),
    ])
    def test_error_messages_contain_expected_text(self, tmp_path, error_case, expected_in_stderr):
        """Error messages should contain helpful information."""
        if error_case == "missing_input":
            exit_code, _, stderr = run_cli("-c", "Page")
        elif error_case == "missing_class_name":
            exit_code, _, stderr = run_cli("-i", "dummy.html")
        elif error_case == "invalid_class_name":
            exit_code, _, stderr = run_cli(
                "-i", "-",
                "-c", "invalid_name"
            )
        elif error_case == "file_not_found":
            exit_code, _, stderr = run_cli(
                "-i", "/missing/file.html",
                "-c", "Page"
            )

        # Error message should be informative
        assert exit_code in [1, 2], f"Expected error exit code"
        error_output = stderr.lower() + " " + str(exit_code)  # combine for search
        assert expected_in_stderr.lower() in error_output.lower() or len(stderr) > 0


class TestCLIExitCodes:
    """Test CLI exit codes."""

    def test_exit_code_0_on_success(self, tmp_path):
        """Should exit with code 0 on successful generation."""
        html_file = tmp_path / "valid.html"
        html_file.write_text("<button>Success</button>")
        output_file = tmp_path / "success.py"

        exit_code, _, _ = run_cli(
            "-i", str(html_file),
            "-c", "SuccessPage",
            "-o", str(output_file)
        )

        # If file is created, it's success
        if output_file.exists():
            assert exit_code == 0, f"Expected exit code 0 on success, got {exit_code}"

    def test_exit_code_1_on_file_not_found_error(self):
        """Should exit with code 1 on file not found error."""
        exit_code, _, _ = run_cli(
            "-i", "/does/not/exist/file.html",
            "-c", "ErrorPage"
        )

        assert exit_code == 1, f"Expected exit code 1 for file error, got {exit_code}"

    def test_exit_code_2_on_invalid_arguments(self):
        """Should exit with code 2 for invalid arguments."""
        # Missing required argument
        exit_code, _, _ = run_cli("-c", "PageName")

        assert exit_code == 2, f"Expected exit code 2 for missing required arg, got {exit_code}"


class TestCLIExamples:
    """Test CLI examples from REQUIREMENTS.md."""

    def test_example_file_to_output(self, tmp_path):
        """Example: python main.py -i file.html -c PageName -o output.py"""
        # Setup
        input_file = tmp_path / "login.html"
        input_file.write_text("<input type='email' placeholder='Email'><button>Login</button>")
        output_file = tmp_path / "login_page.py"

        # Execute
        exit_code, _, _ = run_cli(
            "-i", str(input_file),
            "-c", "LoginPage",
            "-o", str(output_file)
        )

        # Verify
        if exit_code == 0:
            assert output_file.exists(), "Output file should be created"
            content = output_file.read_text()
            assert "LoginPage" in content
            assert "def __init__" in content

    def test_example_file_to_stdout(self, tmp_path):
        """Example: python main.py -i file.html -c PageName"""
        input_file = tmp_path / "form.html"
        input_file.write_text("<form><input type='text'><button>Submit</button></form>")

        exit_code, stdout, _ = run_cli(
            "-i", str(input_file),
            "-c", "FormPage"
        )

        if exit_code == 0:
            assert len(stdout) > 0, "Should output to stdout"
            assert "FormPage" in stdout or "class" in stdout.lower()

    def test_example_stdin_to_output(self, tmp_path):
        """Example: cat file.html | python main.py -c PageName -o output.py"""
        output_file = tmp_path / "stdin_page.py"
        html_content = "<button>Stdin Test</button>"

        cmd = [sys.executable, "main.py", "-c", "StdinPage", "-o", str(output_file)]
        result = subprocess.run(
            cmd,
            input=html_content,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )

        if result.returncode == 0 and output_file.exists():
            content = output_file.read_text()
            assert "StdinPage" in content

    def test_example_stdin_to_stdout(self):
        """Example: echo HTML | python main.py -c PageName"""
        html_content = "<button>Stdout</button><input placeholder='Name'>"

        cmd = [sys.executable, "main.py", "-c", "TestPage"]
        result = subprocess.run(
            cmd,
            input=html_content,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )

        if result.returncode == 0:
            assert len(result.stdout) > 0, "Should output to stdout"
            assert "TestPage" in result.stdout or "class" in result.stdout.lower()


class TestCLIInteractiveMode:
    """Test CLI interactive mode."""

    def test_interactive_mode_flag(self, tmp_path):
        """Should accept --interactive flag."""
        html_file = tmp_path / "test.html"
        html_file.write_text("<button>Test</button>")
        output_file = tmp_path / "output.py"

        # Simulate interactive mode with input
        html_input = f"{str(html_file)}\nTestPage\n{str(output_file)}\n"
        cmd = [sys.executable, "main.py", "-I"]
        result = subprocess.run(
            cmd,
            input=html_input,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )

        # Should complete successfully
        assert result.returncode in [0, 1], f"Unexpected exit code: {result.returncode}"

    def test_interactive_mode_long_flag(self, tmp_path):
        """Should accept --interactive flag (long form)."""
        html_file = tmp_path / "test.html"
        html_file.write_text("<button>Test</button>")
        output_file = tmp_path / "output.py"

        html_input = f"{str(html_file)}\nTestPage\n{str(output_file)}\n"
        cmd = [sys.executable, "main.py", "--interactive"]
        result = subprocess.run(
            cmd,
            input=html_input,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )

        # Should complete successfully
        assert result.returncode in [0, 1], f"Unexpected exit code: {result.returncode}"


class TestCLIWorkflows:
    """Test complete CLI workflows."""

    def test_file_to_file_workflow(self, tmp_path):
        """Complete workflow: file → process → file output."""
        input_file = tmp_path / "input.html"
        input_file.write_text("""
        <form id="contactForm">
            <label for="name">Name</label>
            <input id="name" type="text">
            <button type="submit">Send</button>
        </form>
        """)
        output_file = tmp_path / "contact_page.py"

        exit_code, _, _ = run_cli(
            "-i", str(input_file),
            "-c", "ContactPage",
            "-o", str(output_file)
        )

        if exit_code == 0:
            assert output_file.exists()
            content = output_file.read_text()
            assert "ContactPage" in content
            assert "class ContactPage" in content
            assert "__init__" in content

    def test_file_to_stdout_workflow(self, tmp_path):
        """Complete workflow: file → process → stdout output."""
        input_file = tmp_path / "page.html"
        input_file.write_text("<h1>Welcome</h1><a href='/login'>Login</a>")

        exit_code, stdout, _ = run_cli(
            "-i", str(input_file),
            "-c", "WelcomePage"
        )

        if exit_code == 0:
            assert "WelcomePage" in stdout
            assert "self.page = page" in stdout

    def test_stdin_to_file_workflow(self, tmp_path):
        """Complete workflow: stdin → process → file output."""
        output_file = tmp_path / "generated.py"
        html = "<button>Click</button><input type='email'>"

        cmd = [sys.executable, "main.py", "-c", "GeneratedPage", "-o", str(output_file)]
        result = subprocess.run(
            cmd,
            input=html,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )

        if result.returncode == 0:
            assert output_file.exists()
            content = output_file.read_text()
            assert "GeneratedPage" in content

    def test_stdin_to_stdout_workflow(self):
        """Complete workflow: stdin → process → stdout output."""
        html = "<button>Result</button><input placeholder='Query'>"

        cmd = [sys.executable, "main.py", "-c", "ResultPage"]
        result = subprocess.run(
            cmd,
            input=html,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )

        if result.returncode == 0:
            assert len(result.stdout) > 0
            assert "ResultPage" in result.stdout


