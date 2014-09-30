import os, commands, syslog, tempfile
import paramiko

def log(message):
    """Log message with specifc priority to LOG_DAEMON"""
    syslog.openlog("isiman", syslog.LOG_PID, syslog.LOG_DAEMON)
    syslog.syslog(syslog.LOG_INFO, message)
    syslog.closelog()

def uniq(seq):
    """Unique items in a list"""
    checked = []
    for e in seq:
       if e not in checked:
           checked.append(e)
    return checked

def split_jobs_output(output):
    """Split Isilon jobs output over SSH connection to remove break lines from jobs.* lines"""
    result = []
    for line in output.splitlines():
        if (line.startswith("jobs.") and len(result) > 0):
            yield("\n".join(result))
            result = []
        if (line.strip() != ""):
            result.append(line)
    if (len(result) > 0):
        yield("\n".join(result))

def which(command):
    """Abstraction of posix command using on system PATH variable"""
    envpath=os.getenv('PATH')
    for path in envpath.split(os.path.pathsep):
        path=os.path.join(path,command)
        if os.path.exists(path) and os.access(path,os.X_OK):
            return path

def snmpget(host, oid, version="v2c", community="public", timeout=30):
    """Abstraction of "snmpget" posix command"""
    snmpget = which('snmpget')
    command = '%s -%s -c %s -t %s %s %s' % (snmpget, version, community, timeout, host, oid)
    status, output = commands.getstatusoutput(command)
    if status == 0:
        # remove quotation marks from snmp result value
        return output.split()[-1].strip('""')
    else:
        raise Exception("%s" % output)

def ssh_private_key(key):
    """Create a temporary ssh private key file"""
    temp = tempfile.NamedTemporaryFile(delete=False)
    f = open(temp.name,'w')
    f.write(key)
    f.close()
    return temp.name

def remote_command(host, username, private_key, command, timeout=30):
    """Executes a remote command over ssh connection using private ssh key"""
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=username, key_filename=private_key, timeout=timeout)
        stdin, stdout, stderr = ssh.exec_command(command)
        return stdout.read()
    except Exception, e:
        raise(e)
    finally:
        ssh.close()

def human2bytes(size):
    """Convert human binary prefix to bytes"""
    SYMBOLS = {
        'customary'     : ('B', 'K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y'),
        'customary_ext' : ('byte', 'kilo', 'mega', 'giga', 'tera', 'peta', 'exa',
                           'zetta', 'iotta'),
        'iec'           : ('Bi', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi', 'Yi'),
        'iec_ext'       : ('byte', 'kibi', 'mebi', 'gibi', 'tebi', 'pebi', 'exbi',
                           'zebi', 'yobi'),
    }

    init = size
    num = ""
    while size and size[0:1].isdigit() or size[0:1] == '.':
        num += size[0]
        size = size[1:]
    if num:
        num = float(num)
        letter = size.strip()
        for name, sset in SYMBOLS.items():
            if letter in sset:
                break
        else:
            if letter == 'k':
                # treat 'k' as an alias for 'K' as per: http://goo.gl/kTQMs
                sset = SYMBOLS['customary']
                letter = letter.upper()
            else:
                raise ValueError("Can't interpret %r" % init)
        prefix = {sset[0]:1}
        for i, s in enumerate(sset[1:]):
            prefix[s] = 1 << (i+1)*10
        return int(num * prefix[letter])