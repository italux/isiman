from django.core.management.base import BaseCommand, CommandError
from isiman.libs import isilon, utils
from isiman.models import *

class Command(BaseCommand):

    help = 'Get clusters information and update database'

    def handle(self, *args, **options):
        for cluster in Clusters.objects.all():
            try:
                cluster.status = isilon.status(cluster)
                utils.log('INFO: %s status updated' % cluster.name)
                cluster.cpu_usage = isilon.cpu_usage(cluster)
                utils.log('INFO: %s CPU Usage updated' % cluster.name)
                cluster.version = isilon.version(cluster)
                utils.log('INFO: %s OneFS version updated' % cluster.name)
                cluster.save()
            except Exception, e:
                cluster.status = "ERROR"
                cluster.save()
                utils.log('FAILED: %s information update error (%s)' % (cluster.name, e))