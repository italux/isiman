from django.core.management.base import BaseCommand, CommandError
from isiman.libs import isilon, utils
from isiman.models import *

class Command(BaseCommand):
    
    help = 'Get smartpools information and update database'

    def handle(self, *args, **options):

        clusters = Clusters.objects.all()
        last_pools = SmartPools.objects.all()
        curr_pools = {}

        for cluster in clusters:
            new_pool = 0
            updated_pool = 0
            try:
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
                        updated_pool += 1
                    except:
                        smartpools = SmartPools()
                        smartpools.cluster = cluster
                        smartpools.name = key
                        smartpools.ssd_used = smartpool['ssd']['used']
                        smartpools.ssd_size = smartpool['ssd']['size']
                        smartpools.hdd_used = smartpool['hdd']['used']
                        smartpools.hdd_size = smartpool['hdd']['size']
                        smartpools.save()
                        new_pool += 1
                utils.log('INFO: %s - %s smartpools ADDED to database' % (cluster.name, new_pool))
                utils.log('INFO: %s - %s smartpools UPDATED on database' % (cluster.name, updated_pool))
            except Exception, e:
                utils.log('FAILED: %s - ERROR to get SmartPools information (%s)' % (cluster.name, e))

        for cluster in clusters:
            lost_pools = 0
            if curr_pools.get(cluster.name):
                for pool in last_pools.filter(cluster=cluster):
                    if pool.name not in curr_pools.get(cluster.name):
                        pool.delete()
                        lost_pools += 1
            else:
                for pool in last_pools.filter(cluster=cluster):
                        pool.delete()
                        lost_pools += 1
            utils.log('INFO: %s - %s OLD smartpools removed from database' % (cluster.name, lost_pools))