from django.core.management.base import BaseCommand, CommandError
from isiman.libs import isilon
from isiman.models import *
import datetime

class Command(BaseCommand):
    args = ''
    help = 'test'

    def handle(self, *args, **options):

        clusters = Cluster.objects.all()
        last_jobs = Jobs.objects.all()
        curr_jobs = {}

        for cluster in clusters:
            for job in isilon.jobs(cluster).itervalues():
                if cluster.name in curr_jobs:
                    curr_jobs[cluster.name].append(job['type'])
                else:
                    curr_jobs[cluster.name] = [job['type']]
                try:
                    jobs = Jobs.objects.get(name=job['type'], cluster=cluster)
                    jobs.impact = job['impact']
                    jobs.priority = job['priority']
                    jobs.policy = job['policy']
                    print job['state']
                    jobs.state = job['state']
                    jobs.running_time = str(datetime.timedelta(seconds=int(job['running_time'])))
                    jobs.save()
                except:
                    jobs = Jobs()
                    jobs.cluster = cluster
                    jobs.name = job['type']
                    jobs.impact = job['impact']
                    jobs.priority = job['priority']
                    jobs.policy = job['policy']
                    jobs.state = job['state']
                    jobs.running_time = str(datetime.timedelta(seconds=int(job['running_time'])))
                    jobs.save()

        for cluster in clusters:
            if curr_jobs.get(cluster.name):
                for job in last_jobs.filter(cluster=cluster):
                    if job.name not in curr_jobs.get(cluster.name):
                        job.delete()
            else:
                for job in last_jobs.filter(cluster=cluster):
                        job.delete()