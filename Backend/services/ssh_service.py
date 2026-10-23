"""Read-only monitoring for Linux VMs through SSH with host-key verification."""
import time


def parse_cpu(line):
    parts = line.split()
    if not parts or parts[0] != 'cpu':
        raise ValueError('Invalid /proc/stat reading')
    counters = [int(x) for x in parts[1:]]
    if len(counters) < 4:
        raise ValueError('Missing CPU counters')
    idle = counters[3] + (counters[4] if len(counters) > 4 else 0)
    return sum(counters), idle


def cpu_percent(before, after):
    total_diff = after[0] - before[0]
    idle_diff = after[1] - before[1]
    if total_diff <= 0:
        raise ValueError('Invalid CPU sample interval')
    return max(0.0, min(100.0, 100 * (1 - idle_diff / total_diff)))


def parse_memory(raw):
    rows = {}
    for line in raw.splitlines():
        key, _, value = line.partition(':')
        if value:
            rows[key] = int(value.strip().split()[0])
    total = rows['MemTotal']
    available = rows['MemAvailable']
    if total <= 0:
        raise ValueError('Invalid memory total')
    return max(0.0, min(100.0, 100 * (total - available) / total))


def parse_disk(raw):
    lines = raw.strip().splitlines()
    if len(lines) < 2:
        raise ValueError('Invalid df output')
    return float(lines[-1].split()[4].rstrip('%'))


def _exec(client, command):
    _, stdout, stderr = client.exec_command(command, timeout=12)
    output = stdout.read().decode('utf-8', errors='replace')
    error = stderr.read().decode('utf-8', errors='replace')
    if stdout.channel.recv_exit_status() != 0:
        raise RuntimeError(f'Remote command failed: {error.strip()}')
    return output.strip()


def collect_vm(vm, username, key_path, known_hosts=None):
    """One SSH connection per VM; known hosts must be trusted beforehand."""
    import paramiko
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    if known_hosts:
        client.load_host_keys(known_hosts)
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    try:
        client.connect(hostname=vm['ip'], port=vm.get('port', 22),
                       username=vm.get('user', username),
                       key_filename=vm.get('key_path', key_path),
                       look_for_keys=False, allow_agent=False,
                       timeout=5, auth_timeout=5, banner_timeout=5)
        before = parse_cpu(_exec(client, 'head -n 1 /proc/stat'))
        memory = parse_memory(_exec(client, 'cat /proc/meminfo'))
        disk = parse_disk(_exec(client, 'df -P /'))
        name = _exec(client, 'hostname')
        os_name = _exec(client, 'uname -s')
        time.sleep(0.5)
        after = parse_cpu(_exec(client, 'head -n 1 /proc/stat'))
        return {'server': vm.get('name') or name, 'ip': vm['ip'],
                'cpu': cpu_percent(before, after), 'memory': memory,
                'disk': disk, 'network': 0, 'operating_system': os_name,
                'status': 'ONLINE'}
    finally:
        client.close()
