from django.core.management.base import BaseCommand, CommandError
from isiman.libs import isilon, utils
from isiman.models import *
import datetime

class Command(BaseCommand):

    help = 'Get snapshots from each cluster and update database'

    def handle(self, *args, **options):
        
        clusters = Clusters.objects.all()
        last_snaps = Snapshots.objects.all()
        curr_snaps = {}

        for cluster in clusters:
            snapshots = isilon.Snapshots(cluster)
            new_snaps = 0
            updated_snaps = 0
            try:         
                for snapshot in snapshots.list():
                    snap_id = int(snapshot.get('id'))
                    name = snapshot.get('name')
                    path = snapshot.get('path')
                    size = snapshot.get('size')
                    state = snapshot.get('state')
                    created = snapshot.get('created')
                    expires = snapshot.get('expires')

                    if cluster.name in curr_snaps:
                        curr_snaps[cluster.name].append(snap_id)
                    else:
                        curr_snaps[cluster.name] = [snap_id]
                    try:
                        snapshots = Snapshots.objects.get(snap_id=snap_id, cluster=cluster)
                        snapshots.save()
                        updated_snaps += 1
                    except:
                        snapshots = Snapshots()
                        snapshots.id = snap_id
                        snapshots.cluster = cluster
                        snapshots.name = name
                        snapshots.path = path
                        snapshots.size = size
                        snapshots.state = state
                        snapshots.created = datetime.datetime.fromtimestamp(int(created)).strftime('%Y-%m-%d %H:%M:%S')
                        if expires:
                            snapshots.expires = datetime.datetime.fromtimestamp(int(expires)).strftime('%Y-%m-%d %H:%M:%S')
                        else:
                            snapshots.expires = None
                        snapshots.save()
                        new_snaps += 1
                utils.log('INFO: %s - %s snapshots ADDED to database' % (new_snaps, cluster.name))
                utils.log('INFO: %s - %s snapshots UPDATED on database' % (updated_snaps, cluster.name))
            except Exception, e:
                utils.log('FAILED: %s - ERROR to get Snapshots information (%s)' % (cluster.name, e))

        for cluster in clusters:
            lost_snaps = 0
            if curr_snaps.get(cluster.name):
                for snapshot in last_snaps.filter(cluster=cluster):
                    if snapshot.id not in curr_snaps.get(cluster.name):
                        snapshot.delete()
                        lost_snaps += 1
            else:
                for snapshot in last_snaps.filter(cluster=cluster):
                        snapshot.delete()
                        lost_snaps += 1
            utils.log('INFO: %s - %s OLD snapshots removed from database' % (cluster.name, lost_snaps))