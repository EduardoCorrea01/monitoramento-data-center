"""Tests for optional SSH diagnostics; no remote VM or database required."""
import io
import os
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

import ssh_diagnostics


class DiagnosticsTests(unittest.TestCase):
    @patch.dict(os.environ, {
        'SSH_USER': 'monitor', 'SSH_KEY_PATH': '/example/id_ed25519',
        'VM1_IP': '192.168.56.11', 'VM2_IP': '192.168.56.12',
        'VM3_IP': '192.168.56.13',
    })
    @patch('ssh_diagnostics.collect_vm')
    def test_three_vms_and_no_database_usage(self, collect):
        collect.return_value = {'cpu': 30, 'memory': 45, 'disk': 55}
        with redirect_stdout(io.StringIO()) as output:
            result = ssh_diagnostics.main()
        self.assertEqual(result, 0)
        self.assertEqual(collect.call_count, 3)
        self.assertEqual([c.args[0]['ip'] for c in collect.call_args_list], [
            '192.168.56.11', '192.168.56.12', '192.168.56.13'
        ])
        self.assertNotIn('192.168.56.20', output.getvalue())

    @patch.dict(os.environ, {
        'SSH_USER': '', 'SSH_KEY_PATH': '',
        'VM1_IP': '192.168.56.11', 'VM2_IP': '192.168.56.12',
        'VM3_IP': '192.168.56.13',
    })
    def test_no_ssh_credentials(self):
        self.assertEqual(ssh_diagnostics.main(), 2)


if __name__ == '__main__':
    unittest.main()
