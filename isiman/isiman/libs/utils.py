import os, commands, paramiko
# from isiman.models import Cluster

def which(command):
    envpath=os.getenv('PATH')
    for path in envpath.split(os.path.pathsep):
        path=os.path.join(path,command)
        if os.path.exists(path) and os.access(path,os.X_OK):
            return path

def snmpget(host, oid, version="v2c", community="public"):
    try:
        snmpget = which('snmpget')
        command = '%s -%s -c %s %s %s' % (snmpget, version, community, host, oid)
        return commands.getoutput(command).split()[-1].strip('""')
    except Exception, e:
        return e

def remote_command(host, username, private_key, command):
    """Executes a remote command over ssh connection using ssh key to auth."""
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=username, key_filename=private_key)
        stdin, stdout, stderr = ssh.exec_command(command)
        return stdout.read()
    except Exception, e:
        raise(e)
    finally:
        ssh.close()

def human2bytes(size):
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
                raise ValueError("can't interpret %r" % init)
        prefix = {sset[0]:1}
        for i, s in enumerate(sset[1:]):
            prefix[s] = 1 << (i+1)*10
        return int(num * prefix[letter])