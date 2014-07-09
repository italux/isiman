import re
import tempfile
from isiman.libs import utils

def makesshkey(key):
    temp = tempfile.NamedTemporaryFile(delete=False)
    f = open(temp.name,'w')
    f.write(key)
    f.close()
    return temp.name

def isiremote(cluster, command):
    address = cluster.address
    username = cluster.username
    private_key = makesshkey(cluster.ssh_key)
    if username != 'root':
        command = 'sudo ' + command
    output = utils.remote_command(address, username, private_key, command)
    return output

def status(cluster):
    oid = '.1.3.6.1.4.1.12124.1.1.2.0'
    statusmap = {0: "OK", 1: "ATTN", 2: "OFFLINE", 3: "INVALID" }
    clusterstatus = utils.snmpget(cluster.address, oid)
    return statusmap.get(int(clusterstatus))

def cpu_usage(cluster):
    oid = '.1.3.6.1.4.1.12124.1.2.3.5.0'
    cpu_usage = utils.snmpget(cluster.address, oid)
    return float(100 - float(int(cpu_usage) / 10))

def nodes(cluster):
    command = '/usr/bin/isi status -q -n | /usr/bin/egrep "Name|ID|LNN|Health" | /usr/bin/paste - - - - | /usr/bin/sed "s/Node //g"'
    output = isiremote(cluster, command)
    nodes = {}
    nodeslist = [ line.split('\t') for line in output.split('\n') if len(line) > 0 ]
    [ nodes.update({node[2].replace(" ", "").split(':')[1]: {}}) for node in nodeslist ]
    [ nodes[node[2].replace(" ", "").split(':')[1]].update({node[0].replace(" ", "").lower().split(':')[0]:node[0].replace(" ", "").lower().split(':')[1], node[1].replace(" ", "").lower().split(':')[0]:node[1].replace(" ", "").lower().split(':')[1], node[3].replace(" ", "").lower().split(':')[0]:node[3].replace(" ", "").split(':')[1]}) for node in nodeslist ]
    return nodes

def clients_connected_bynode(cluster):
    command = '/usr/bin/isi statistics query --nodes=all --stats=node.clientstats.connected.cifs,node.clientstats.connected.nfs --noheader --nofooter'
    output = isiremote(cluster, command)
    connections = {}
    connlist = [ line.split() for line in output.split('\n') if len(line) > 0 ]
    [ connections.update({conn[0]:{"cifs":int(conn[1]), "nfs":int(conn[2]), "total": (int(conn[1])+int(conn[2]))}}) for conn in connlist ]
    return connections

def events(cluster):
    command = '/usr/bin/isi events list --columns=id,lnn,severity,message -w --csv'
    output = isiremote(cluster, command)
    events = [ event.split(',') for event in output.split('\n') if len(event) > 0 ]
    return events

def jobs(cluster):
    command = '/usr/bin/isi job status -r'
    output = isiremote(cluster, command)
    regex=re.compile("jobs.\d.(type|policy|impact|priority|state|running_time)=.*")
    jobs = {}
    joblist = [ job.group() for line in output.split('\n') for job in [regex.search(line)] if job]
    [ jobs.update({job.split(".")[1]: {}}) for job in joblist ]
    [ jobs[job.split(".")[1]].update({job.split(".")[2].split("=")[0]: job.split("=")[-1]}) for job in joblist ]
    return jobs

def smartpools(cluster):
    command = '/usr/bin/isi status -d -q | /usr/bin/egrep "\|" | /usr/bin/sed 1d'
    output = isiremote(cluster, command)
    pools = {}
    [ pools.update({pool.split("|")[0].strip(): {}}) for pool in output.split("\n") if len(pool) > 0 ]
    for pool in output.split("\n"):
        if len(pool) > 0:
            hdd_size = utils.human2bytes(pool.split("|")[5].split("/")[1].strip().split("(")[0])
            hdd_used = utils.human2bytes(pool.split("|")[5].split("/")[0].strip())
            if "No SSDs" in pool.split("|")[6].split("/")[0].strip():
                ssd_size = 0
                ssd_used = 0
            else:
                ssd_size = utils.human2bytes(pool.split("|")[6].split("/")[1].strip().split("(")[0])
                ssd_used = utils.human2bytes(pool.split("|")[6].split("/")[0].strip())

            pools[pool.split("|")[0].strip()].update({
                'hdd': {
                    'size': hdd_size, 
                    'used': hdd_used
                    },
                'ssd': {
                    'size': ssd_size, 
                    'used': ssd_used 
                    }})
    return pools