from django.core.management.base import BaseCommand, CommandError
from isiman.libs import isilon
from isiman.models import *

class Command(BaseCommand):
    args = ''
    help = 'test'

    def handle(self, *args, **options):

        clusters = Cluster.objects.all()
        last_nodes = Nodes.objects.all()
        curr_nodes = {}

        for cluster in Cluster.objects.all():
            connections = isilon.clients_connected_bynode(cluster)
            for key, node in isilon.nodes(cluster).iteritems():
                if cluster.name in curr_nodes:
                    curr_nodes[cluster.name].append(key)
                else:
                    curr_nodes[cluster.name] = [key]
                try:
                    nodes = Nodes.objects.get(name=key, cluster=cluster)
                    nodes.status = node.get('health')
                    if node.get('lnn'):
                        nodes.client_conn = connections.get(node.get('lnn')).get('total')
                    nodes.save()
                except:
                    nodes = Nodes()
                    nodes.cluster = cluster
                    nodes.name = key
                    nodes.lnn = node.get('lnn')
                    nodes.isilon_id = node.get('id')
                    nodes.status = node.get('health')
                    if node.get('lnn'):
                        nodes.client_conn = connections.get(node.get('lnn')).get('total')
                    nodes.save()

        for cluster in clusters:
            if curr_nodes.get(cluster.name):
                for node in last_nodes.filter(cluster=cluster):
                    if node.name not in curr_nodes.get(cluster.name):
                        node.delete()
            else:
                for node in last_nodes.filter(cluster=cluster):
                        node.delete()