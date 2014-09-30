from django.core.management.base import BaseCommand, CommandError
from isiman.libs import isilon, utils
from isiman.models import *
import datetime

class Command(BaseCommand):

    help = 'Get ongoing events on clusters and update database'

    def handle(self, *args, **options):
        
        clusters = Clusters.objects.all()
        last_events = Events.objects.all()
        curr_events = {}

        for cluster in clusters:
            new_events = 0
            updated_events = 0
            try:         
                for event in isilon.events(cluster):
                    event_id = float(event[0])
                    event_lnn = event[1]
                    event_sev = event[2]
                    event_start = event[3]
                    if event[4] == "--":
                        event_end = None
                    else:
                        event_end = event[4]
                    event_msg = event[5]
                    if cluster.name in curr_events:
                        curr_events[cluster.name].append(event_id)
                    else:
                        curr_events[cluster.name] = [event_id]
                    try:
                        events = Events.objects.get(id=event_id, cluster=cluster)
                        events.save()
                        updated_events += 1
                    except:
                        events = Events()
                        events.cluster = cluster
                        events.id = event_id
                        events.severity = event_sev
                        events.node_lnn = event_lnn
                        events.message = event_msg
                        events.start_time = datetime.datetime.strptime(event_start, "%m/%d/%y %H:%M:%S")
                        if event_end:
                            events.end_time = datetime.datetime.strptime(event_end, "%m/%d/%y %H:%M:%S")
                        events.save()
                        new_events += 1
                utils.log('INFO: %s - %s events new UPDATED to database' % (updated_events, cluster.name))
                utils.log('INFO: %s - %s events new ADDED to database' % (new_events, cluster.name))
            except Exception, e:
                utils.log('FAILED: %s - ERROR to get Events information (%s)' % (cluster.name, e))

        for cluster in clusters:
            lost_events = 0
            if curr_events.get(cluster.name):
                for event in last_events.filter(cluster=cluster):
                    if event.id not in curr_events.get(cluster.name):
                        event.delete()
                        lost_events += 1
            else:
                for event in last_events.filter(cluster=cluster):
                    event.delete()
                    lost_events += 1
            utils.log('INFO: %s - %s OLD events removed from database' % (cluster.name, lost_events))