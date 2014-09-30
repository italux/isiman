from isiman.libs import utils
import requests
import re

def isi_protection_overhead(protection, nodes):
    """Matrix to calculate OneFS protection overhead"""

    # The table below was based on "Isilon OneFS 7.0 Administration Guide"
    # page 145, section "Data protection level disk space usage"
    percent_overhead = {
        "N+2:1": {
            3: 33.33, 4: 25.00,
            5: 20.00, 6: 16.67,
            7: 14.29, 8: 12.50,
            'default': 11.11
        },
        "N+3:1": {
            4: 25.00, 5: 20.00,
            6: 16.67, 7: 14.29,
            8: 12.50, 'default': 11.11
        },
        "N+2": {
            5: 40.00, 6: 33.33, 7: 28.57,
            8: 25.00, 9: 22.22, 10: 20.00,
            11: 18.18, 12: 16.67, 13: 15.38,
            14: 14.29, 15: 13.33, 16: 12.50,
            17: 11.76, 'default': 11.11
        },
        "N+3": {
            7: 42.86, 8: 37.50, 9: 33.33,
            10: 30.00, 11: 27.27, 12: 25.00,
            13: 23.08, 14: 21.43, 15: 20.00,
            16: 18.75, 17: 17.65, 18: 16.67,
            'default': 15.79
        }
    }

    # After a specifc number of nodes the protection overhead shall be constant,
    # so we pass to use "default" percent protection overhead
    if protection == "N+2:1" and nodes >= 9:
        return percent_overhead.get(protection).get('default')
    elif protection == "N+3:1" and nodes >= 9:
        return percent_overhead.get(protection).get('default')
    elif protection == "N+2" and nodes >= 18:
        return percent_overhead.get(protection).get('default')
    elif protection == "N+3" and nodes >= 19:
        return percent_overhead.get(protection).get('default')
    else:
        return percent_overhead.get(protection).get(nodes)

def isiremote(address, username, ssh_key, command):
    """Remote intereaction with Isilon through SSH connection using private key.
    We'll check if user was different from root we'll add "sudo" before the command"""

    try:
        private_key = utils.ssh_private_key(ssh_key)
        if username != 'root':
            command = 'sudo ' + command
        output = utils.remote_command(address, username, private_key, command)
        return output
    except Exception, e:
        raise(e)

def version(cluster):
    """Get OneFS release version through SSH using isiremote()"""

    command = '/usr/bin/isi version osrelease'
    try:
        output = isiremote(cluster.address, cluster.username, cluster.ssh_key, command)
        return output.strip().replace('v', '')
    except Exception, e:
        raise(e)

def status(cluster):
    """Get Isilon cluster status using SNMP"""

    oid = '.1.3.6.1.4.1.12124.1.1.2.0'
    statusmap = {0: "OK", 1: "ATTN", 2: "OFFLINE", 3: "INVALID" }
    try:
        clusterstatus = utils.snmpget(cluster.address, oid)
        return statusmap.get(int(clusterstatus))
    except Exception, e:
            raise(e)

def cpu_usage(cluster):
    """Get Isilon cluster CPU usage using SNMP"""

    oid = '.1.3.6.1.4.1.12124.1.2.3.5.0'
    try:
        cpu_usage = utils.snmpget(cluster.address, oid)
        return float(100 - float(int(cpu_usage) / 10))
    except Exception, e:
        raise(e)

def nodes(cluster):
    """Get Isilon nodes basic information:
    
    Node LNN
    Node ID
    Node Name
    IP Address
    Health
    Serial Number
    """
    command = '/usr/bin/isi status -q -n | /usr/bin/egrep "Name|ID|LNN|Health|Address|SN:" | /usr/bin/paste - - - - - - | /usr/bin/sed "s/Node //g"'
    try:
        output = isiremote(cluster.address, cluster.username, cluster.ssh_key, command)
        nodes = {}
        nodeslist = [ line.split('\t') for line in output.split('\n') if len(line) > 0 ]
        [ nodes.update({node[2].replace(" ", "").split(':')[1]: {}}) for node in nodeslist ]
        [ nodes[node[2].replace(" ", "").split(':')[1]].update({
            node[0].replace(" ", "").lower().split(':')[0]:node[0].replace(" ", "").split(':')[1],
            node[1].replace(" ", "").lower().split(':')[0]:node[1].replace(" ", "").split(':')[1],
            node[3].replace(" ", "").lower().split(':')[0]:node[3].replace(" ", "").split(':')[1],
            node[4].replace(" ", "").lower().split(':')[0]:node[4].replace(" ", "").split(':')[1],
            node[5].replace(" ", "").lower().split(':')[0]:node[5].replace(" ", "").split(':')[1]
            }) for node in nodeslist ]
        return nodes
    except Exception, e:
        raise(e)

def servicelight(node, action):
    """Manage nodes servicelight through SSH using isiremote()"""

    command = '/usr/bin/isi servicelight %s' % action
    if action == "on" or action == "off":
        isiremote(node.ipaddress, node.cluster.username, node.cluster.ssh_key, command)

        # "isi" commands aways return status code 0 (zero), so after execute a command
        # we need validate if the service light status was changed as we expected

        statuscmd = '/usr/bin/isi servicelight status'
        output = isiremote(node.ipaddress, node.cluster.username, node.cluster.ssh_key, statuscmd)

        if output.split('\n')[0].split()[-1] == action:
            return output.split('\n')[0].split()[-1]
        else:
            raise Exception('Error change servicelight status')
    elif action == "status":
        output = isiremote(node.ipaddress, node.cluster.username, node.cluster.ssh_key, command)
        if output.split('\n')[0].split()[-1] == "on" or output.split('\n')[0].split()[-1] == "off":
            return output.split('\n')[0].split()[-1]
        else:
            raise Exception('Error getting servicelight status')
    else:
        raise Exception('Command not found')

def clients_connected_bynode(cluster):
    """Get nodes statistics informations about clients connections through SSH using "isi statistics query" command"""

    # We just get the clientstats.connected.[cifs, nfs]
    # because is that same information that we can see on the isilon cluster WebUI

    command = '/usr/bin/isi statistics query --nodes=all --stats=node.clientstats.connected.cifs,node.clientstats.connected.nfs --noheader --nofooter'
    try:
        output = isiremote(cluster.address, cluster.username, cluster.ssh_key, command)
        connections = {}
        connlist = [ line.split() for line in output.split('\n') if len(line) > 0 ]
        [ connections.update({conn[0]:{"cifs":int(conn[1]), "nfs":int(conn[2]), "total": (int(conn[1])+int(conn[2]))}}) for conn in connlist ]
        return connections
    except Exception, e:
        raise(e)

def events(cluster):
    """Get current cluster events through SSH using isiremote()"""

    command = '/usr/bin/isi events list --columns=id,lnn,severity,message,start_time,end_time -w --csv'
    try:
        output = isiremote(cluster.address, cluster.username, cluster.ssh_key, command)
        events = [ event.split(',', 5) for event in output.split('\n') if len(event) > 0 ]
        return events
    except Exception, e:
        raise(e)

def smartpools(cluster):
    """Get SmartPools created and the usage infotmation"""

    command = '/usr/bin/isi status -d -q | /usr/bin/egrep "\|" | /usr/bin/sed 1d'
    try:
        output = isiremote(cluster.address, cluster.username, cluster.ssh_key, command)
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
    except Exception, e:
        raise(e)

class RemoteSSH(object):
    """Remote intereaction with Isilon through SSH connection using private key.
    We'll check if user was different from root we'll add "sudo" before the command"""

    def __init__(self, cluster):
        super(RemoteSSH, self).__init__()
        self.cluster = cluster

    def get(self, resource):
        """Get information from Isilon Cluster through SSH connection"""

        if resource == '/platform/1/job/jobs':
            __command = '/usr/bin/isi job status -r'

        return self.__execute__(__command)

    def __execute__(self, command):
        try:
            __private_key = utils.ssh_private_key(self.cluster.ssh_key)
            if self.cluster.username != 'root':
                command = 'sudo ' + command
            output = utils.remote_command(self.cluster.address, self.cluster.username, __private_key, command)
            return output
        except Exception, e:
            raise(e)

class API(object):
    """Intereaction with Isilon built-in API through HTTP Basic Auth"""

    def __init__(self, cluster):
        super(API, self).__init__()
        self.cluster = cluster
        
    def get(self, resource):
        """Get information from Isilon Cluster through API"""

        __method = 'GET'
        try:
            return self.__api__(__method, resource)
        except Exception, e:
            raise(e)

    def __api__(self, method, resource):
        """Generic method to interact with Isilon Cluster through API"""

        __timeout = 30
        try:
            __url = "https://" + self.cluster.address + ":8080" + resource
            result = requests.request(method, __url, auth=(self.cluster.username, self.cluster.password), timeout=__timeout ,verify=False)
            return result.json()
        except Exception, e:
            raise(e)

class Jobs(object):
    """Interact and Manage Jobs on Isilon cluster"""
    
    def __init__(self, cluster):
        super(Jobs, self).__init__()
        self.cluster = cluster
        
    def list(self):
        """List current jobs on Isilon cluster"""

        resource = '/platform/1/job/jobs'
        try:
            result = self.__load__(resource)
            return result.get('jobs')
        except Exception, e:
            raise(e)

    def __load__(self, resource):
        
        # Some "isi job" commands was changed on OneFS version 7.1 or later
        # so we need check the cluster version before run the command.
        # 
        # The job status on OneFS version 7.1 will be obtained from Isilon API
        # in older versions, like 6.5 and/or 7.0 we'll need use SSH to do that.
        
        if self.cluster.version.startswith('7.1'):
            __api = API(self.cluster)
            return __api.get(resource)
        elif self.cluster.version.startswith('7.0') or self.cluster.version.startswith('6.5'):
            __ssh = RemoteSSH(self.cluster)
            __output = __ssh.get(resource)
            __jobs  ={}
            regex=re.compile("jobs.\d.(id|impact|description|phase_cur|state|priority|participants|create_time|policy|progress|retries|type|phase_total)=.*", re.MULTILINE|re.DOTALL)
            rawjobs = [ job.group() for line in utils.split_jobs_output(__output) for job in [regex.search(line)] if job]
            [ __jobs.update({job.split(".")[1]: {}}) for job in rawjobs ]
            [ __jobs[job.split(".")[1]].update({job.split(".")[2].split("=")[0]: job.split("=")[-1].replace('\n', ' ')}) for job in rawjobs ]
            return {'jobs': [ job for job in __jobs.itervalues() ] }
        else:
            raise Exception('OneFS version (%s) not supported.' % self.cluster.version)

class Snapshots(object):
    """Interact and Manage Snapshots on Isilon cluster"""
    def __init__(self, arg):
        super(Snapshots, self).__init__()
        self.api = API(self.cluster)

    def summary(self):
        resource = '/platform/1/snapshot/snapshots-summary'
        summary = self.__load__(self.cluster, resource).get('summary')
        return summary

    def list(self):
        resource = '/platform/1/snapshot/snapshots'
        snapshots = self.__load__(resource).get('snapshots')
        return snapshots

    def get(self, snap_id):
        resource = '/platform/1/snapshot/snapshots/%s' % snap_id
        snapshot = self.__load__(resource).get('snapshots')
        return snapshot

    def __load__(self, resource):
        """Get Snapshots data from Isilon API"""

        if self.cluster.version.startswith('7.'):
            try:
                result = self.api.get(resource)
                return result
            except Exception, e:
                raise(e)
        else:
            raise Exception('OneFS version (%s) not supported.' % self.cluster.version)
