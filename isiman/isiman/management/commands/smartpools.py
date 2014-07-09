from django.core.management.base import BaseCommand, CommandError
from isiman.libs import isilon
from isiman.models import *

class Command(BaseCommand):
    args = ''
    help = 'test'

    def handle(self, *args, **options):

        clusters = Cluster.objects.all()
        last_pools = SmartPools.objects.all()
        curr_pools = {}

        for cluster in clusters:
            for key, smartpool in isilon.smartpools(cluster).iteritems():
                if cluster.name in curr_pools:
                    curr_pools[cluster.name].append(key)
                else:
                    curr_pools[cluster.name] = [key]
                try:
                    smartpools = SmartPools.objects.get(name=key, cluster=cluster)
                    smartpools.ssd_used = smartpool['ssd']['used']
                    smartpools.ssd_size = smartpool['ssd']['size']
                    smartpools.hdd_used = smartpool['hdd']['used']
                    smartpools.hdd_size = smartpool['hdd']['size']
                    smartpools.save()
                except:
                    smartpools = SmartPools()
                    smartpools.cluster = cluster
                    smartpools.name = key
                    smartpools.ssd_used = smartpool['ssd']['used']
                    smartpools.ssd_size = smartpool['ssd']['size']
                    smartpools.hdd_used = smartpool['hdd']['used']
                    smartpools.hdd_size = smartpool['hdd']['size']
                    smartpools.save()

        for cluster in clusters:
            if curr_pools.get(cluster.name):
                for pool in last_pools.filter(cluster=cluster):
                    if pool.name not in curr_pools.get(cluster.name):
                        pool.delete()
            else:
                for pool in last_pools.filter(cluster=cluster):
                        pool.delete()