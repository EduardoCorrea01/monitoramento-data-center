import unittest
from services.ssh_service import parse_cpu, cpu_percent, parse_memory, parse_disk


class SSHParserTests(unittest.TestCase):
    def test_cpu(self):
        self.assertAlmostEqual(cpu_percent((100, 60), (200, 90)), 70)
        self.assertEqual(parse_cpu('cpu 10 0 5 20 5 0 0 0'), (40, 25))

    def test_memory(self):
        self.assertEqual(parse_memory('MemTotal: 1000 kB\nMemAvailable: 300 kB'), 70)

    def test_disk(self):
        self.assertEqual(parse_disk('Filesystem 1024-blocks Used Available Capacity Mounted on\n/dev/sda 100 90 10 90% /'), 90)


if __name__ == '__main__':
    unittest.main()
