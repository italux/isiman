from django.core.management.base import BaseCommand, CommandError
from isiman.libs import isilon
from isiman.models import *

class Command(BaseCommand):
    args = ''
    help = 'test'

    def handle(self, *args, **options):
        
        clusters = Cluster.objects.all()
        last_events = Events.objects.all()
        curr_events = {}

        for cluster in clusters:
            for event in isilon.events(cluster):
                event_id = event[0]
                event_lnn = event[1]
                event_sev = event[2]
                event_msg = event[3]
                if cluster.name in curr_events:
                    curr_events[cluster.name].append(event_id)
                else:
                    curr_events[cluster.name] = [event_id]
                try:
                    events = Events.objects.get(event_id=event_id, cluster=cluster)
                    events.save()
                except:
                    events = Events()
                    events.cluster = cluster
                    events.event_id = event_id
                    events.severity = event_sev
                    events.node_lnn = event_lnn
                    events.message = event_msg
                    events.save()

        for cluster in clusters:
            if curr_events.get(cluster.name):
                for event in last_events.filter(cluster=cluster):
                    if event.event_id not in curr_events.get(cluster.name):
                        event.delete()
            else:
                for event in last_events.filter(cluster=cluster):
                        event.delete()