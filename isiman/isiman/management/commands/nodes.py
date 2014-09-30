from django.core.management.base import BaseCommand, CommandError
from isiman.libs import isilon, utils
from isiman.models import *

class Command(BaseCommand):
    
    help = 'Get nodes information and update database'

    def handle(self, *args, **options):

        clusters = Clusters.objects.all()
        last_nodes = Nodes.objects.all()
        curr_nodes = {}

        for cluster in clusters:
            new_nodes = 0
            updated_nodes = 0
            try:
                connections = isilon.clients_connected_bynode(cluster)
                for key, node in isilon.nodes(cluster).iteritems():
                    if cluster.name in curr_nodes:
                        curr_nodes[cluster.name].append(key)
                    else:
                        curr_nodes[cluster.name] = [key]
                    try:
                        nodes = Nodes.objects.get(name=key, cluster=cluster)
                        nodes.ipaddress = node.get('ipaddress')
                        if "A" in node.get('health'):
                            nodes.status = "ATTN"
                        elif "D" in node.get('health'):
                            nodes.status = "DOWN"
                        elif "S" in node.get('health'):
                            nodes.status = "SMARTFAILED"
                        elif "R" in node.get('health'):
                            nodes.status = "READ_ONLY"
                        else:
                            nodes.status = node.get('health')

                        if node.get('sn').split('-')[0].startswith('M1'):
                            nodes.model = "108NL"
                        else:
                            nodes.model = node.get('sn').split('-')[0].split('S',1)[1]
                        
                        nodes.serial = node.get('sn')
                        if node.get('lnn'):
                            if connections.get(node.get('lnn')):
                                nodes.client_conn = connections.get(node.get('lnn')).get('total')
                            else:
                                nodes.client_conn = 0
                        nodes.save()
                        updated_nodes += 1
                    except:
                        nodes = Nodes()
                        nodes.node_id = node.get('id')
                        nodes.cluster = cluster
                        nodes.name = key
                        nodes.ipaddress = node.get('ipaddress')
                        nodes.lnn = node.get('lnn')
                        if "A" in node.get('health'):
                            nodes.status = "ATTN"
                        elif "D" in node.get('health'):
                            nodes.status = "DOWN"
                        elif "S" in node.get('health'):
                            nodes.status = "SMARTFAILED"
                        elif "R" in node.get('health'):
                            nodes.status = "READ_ONLY"
                        else:
                            nodes.status = node.get('health')

                        if node.get('sn').split('-')[0].startswith('M1'):
                            nodes.model = "108NL"
                        else:
                            nodes.model = node.get('sn').split('-')[0].split('S',1)[1]

                        nodes.serial = node.get('sn')
                        if node.get('lnn'):
                            if connections.get(node.get('lnn')):
                                nodes.client_conn = connections.get(node.get('lnn')).get('total')
                            else:
                                nodes.client_conn = 0
                        nodes.save()
                        new_nodes += 1
                utils.log('INFO: %s - %s nodes ADDED to database' % (cluster.name, new_nodes))
                utils.log('INFO: %s - %s nodes UPDATED on database' % (cluster.name, updated_nodes))
            except Exception, e:
                utils.log('FAILED: %s - ERROR to get Nodes information (%s)' % (cluster.name, e))

        for cluster in clusters:
            lost_nodes = 0
            if curr_nodes.get(cluster.name):
                for node in last_nodes.filter(cluster=cluster):
                    if node.name not in curr_nodes.get(cluster.name):
                        node.delete()
                        lost_nodes += 1
            else:
                for node in last_nodes.filter(cluster=cluster):
                        node.delete()
                        lost_nodes += 1
            utils.log('INFO: %s - %s OLD nodes removed from database' % (cluster.name, lost_nodes))