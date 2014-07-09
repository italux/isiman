from django.core.management.base import BaseCommand, CommandError
from isiman.libs import isilon
from isiman.models import *

class Command(BaseCommand):
    args = ''
    help = 'test'

    def handle(self, *args, **options):
        for cluster in Cluster.objects.all():
            cluster.status = isilon.status(cluster)
            cluster.cpu_usage = isilon.cpu_usage(cluster)
            cluster.save()