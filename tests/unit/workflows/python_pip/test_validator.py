from unittest import TestCase, mock

from parameterized import parameterized

from aws_lambda_builders.exceptions import MisMatchRuntimeError
from aws_lambda_builders.workflows.python_pip.validator import PythonRuntimeValidator
from aws_lambda_builders.exceptions import UnsupportedRuntimeError, UnsupportedArchitectureError


class MockSubProcess(object):
    def __init__(self, returncode):
        self.returncode = returncode

    def communicate(self):
        pass


class TestPythonRuntimeValidator(TestCase):
    def setUp(self):
        self.validator = PythonRuntimeValidator(runtime="python3.7", architecture="x86_64")

    def test_runtime_validate_unsupported_language_fail_open(self):
        validator = PythonRuntimeValidator(runtime="python2.6", architecture="arm64")
        with self.assertRaises(UnsupportedRuntimeError):
            validator.validate(runtime_path="/usr/bin/python2.6")

    def test_runtime_validate_supported_version_runtime(self):
        with mock.patch("subprocess.Popen") as mock_subprocess:
            mock_subprocess.return_value = MockSubProcess(0)
            self.validator.validate(runtime_path="/usr/bin/python3.7")
            self.assertTrue(mock_subprocess.call_count, 1)

    def test_runtime_validate_mismatch_version_runtime(self):
        with mock.patch("subprocess.Popen") as mock_subprocess:
            mock_subprocess.return_value = MockSubProcess(1)
            with self.assertRaises(MisMatchRuntimeError):
                self.validator.validate(runtime_path="/usr/bin/python3.9")
                self.assertTrue(mock_subprocess.call_count, 1)

    def test_python_command(self):
        cmd = self.validator._validate_python_cmd(runtime_path="/usr/bin/python3.7")
        version_strings = ["sys.version_info.major == 3", "sys.version_info.minor == 7"]
        for version_string in version_strings:
            self.assertTrue(all([part for part in cmd if version_string in part]))

    @parameterized.expand(
        [
            ("python3.7", "arm64"),
        ]
    )
    def test_runtime_validate_with_incompatible_architecture(self, runtime, architecture):
        validator = PythonRuntimeValidator(runtime=runtime, architecture=architecture)
        with self.assertRaises(UnsupportedArchitectureError):
            validator.validate(runtime_path="/usr/bin/python")
