from django.core.management.base import BaseCommand, CommandError
from isiman.libs import isilon, utils
from isiman.models import *
import datetime

class Command(BaseCommand):
    
    help = 'Get current jobs on clusters events and update database'

    def handle(self, *args, **options):

        clusters = Clusters.objects.all()
        last_jobs = Jobs.objects.all()
        curr_jobs = {}

        for cluster in clusters:
            clusterjobs = isilon.Jobs(cluster)
            new_jobs = 0
            updated_jobs = 0
            try:
                for job in clusterjobs.list():
                    job_id = int(job.get('id'))
                    name = job.get('type')
                    impact = job.get('impact')
                    priority = job.get('priority')
                    policy = job.get('policy')
                    state = job.get('state').replace('_', " ").title()
                    progress = job.get('progress')
                    create_time = job.get('create_time')
                    if job.get('running_time'):
                        running_time = job.get('running_time')
                    else:
                        running_time = 0

                    if cluster.name in curr_jobs:
                        curr_jobs[cluster.name].append(job_id)
                    else:
                        curr_jobs[cluster.name] = [job_id]
                    try:
                        jobs = Jobs.objects.get(id=job_id, cluster=cluster)
                        jobs.id = job_id
                        jobs.impact = impact
                        jobs.priority = priority
                        jobs.policy = policy
                        jobs.state = state
                        jobs.progress = progress
                        jobs.create_time = str(datetime.timedelta(seconds=int(create_time)))
                        jobs.running_time = str(datetime.timedelta(seconds=int(running_time)))
                        jobs.save()
                        updated_jobs += 1
                    except:
                        jobs = Jobs()
                        jobs.id = job_id
                        jobs.cluster = cluster
                        jobs.name = name
                        jobs.impact = impact
                        jobs.priority = priority
                        jobs.policy = policy
                        jobs.state = state
                        jobs.progress = progress
                        jobs.create_time = str(datetime.timedelta(seconds=int(create_time)))
                        jobs.running_time = str(datetime.timedelta(seconds=int(running_time)))
                        jobs.save()
                        new_jobs += 1
                utils.log('INFO: %s - %s jobs ADDED to database' % (cluster.name, new_jobs))
                utils.log('INFO: %s - %s jobs UPDATED on database' % (cluster.name, updated_jobs))
            except Exception, e:
                utils.log('FAILED: %s - ERROR to get jobs (%s)' % (cluster.name, e))

        for cluster in clusters:
            lost_jobs = 0
            if curr_jobs.get(cluster.name):
                for job in last_jobs.filter(cluster=cluster):
                    if job.id not in curr_jobs.get(cluster.name):
                        job.delete()
                        lost_jobs += 1
            else:
                for job in last_jobs.filter(cluster=cluster):
                    job.delete()
                    lost_jobs += 1
            utils.log('INFO: %s - %s OLD jobs removed from database' % (cluster.name, lost_jobs))