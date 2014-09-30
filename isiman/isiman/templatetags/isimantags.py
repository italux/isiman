from django import template
from django.utils import timezone
from django.db.models import Sum
from django.utils.timesince import timesince
from datetime import datetime, timedelta
from isiman.models import *

register = template.Library()

@register.filter
def snapsize_bydate(cluster, date):
    day = date.split('/')[0]
    month = date.split('/')[1]
    year = date.split('/')[2]
    result = Snapshots.objects.filter(cluster=cluster, created__year=year, created__month=month, created__day=day).aggregate(Sum('size'))
    return result.get('size__sum')

@register.filter
def snapcount_bydate(cluster, date):
    day = date.split('/')[0]
    month = date.split('/')[1]
    year = date.split('/')[2]
    return Snapshots.objects.filter(cluster=cluster, created__year=year, created__month=month, created__day=day).count()

@register.filter
def nodesbymodel(model):
   return Nodes.objects.filter(model=model).count()

@register.filter
def cluster_nodesbymodel(cluster, model):
   return Nodes.objects.filter(cluster=cluster, model=model).count()

@register.filter
def clusternodes_bymodel(cluster, model):
   return Nodes.objects.filter(cluster=cluster, model=model).count()

@register.filter
def clusterevent_byseverity(model, severity):
    return model.events_set.filter(severity=severity).count()

@register.filter
def clusterjobs_bystate(model, state):
    return model.jobs_set.filter(state=state).count()

@register.filter
def jobstatecount(state):
    return Jobs.objects.filter(state=state).count()

@register.filter
def eventseveritycount(severity):
    return Events.objects.filter(severity=severity).count()

@register.filter
def clusterhddused(cluster):
    result = 0
    for smartpool in SmartPools.objects.filter(cluster=cluster):
        result += smartpool.hdd_used
    return result

@register.filter
def clusterhddsize(cluster):
    result = 0
    for smartpool in SmartPools.objects.filter(cluster=cluster):
        result += smartpool.hdd_size
    return result

@register.filter
def clusterssdused(cluster):
    result = 0
    for smartpool in SmartPools.objects.filter(cluster=cluster):
        result += smartpool.ssd_used
    return result

@register.filter
def clusterssdsize(cluster):
    result = 0
    for smartpool in SmartPools.objects.filter(cluster=cluster):
        result += smartpool.ssd_size
    return result

@register.filter
def clusterstatuscount(status):
    return Clusters.objects.filter(status=status).count()

@register.filter
def nodestatuscount(status, cluster):
    return Nodes.objects.filter(cluster=cluster, status__contains=status).count()

@register.filter
def clusterconncount(cluster):
    result = 0
    for node in Nodes.objects.filter(cluster=cluster):
        result += int(node.client_conn)
    return result

@register.filter    
def clustersdelayed(time):
    return Clusters.objects.filter(modified_at__lte=datetime.now()-timedelta(hours=time)).count()

@register.filter
def percentage(used, size):
        if size == 0 and used == 0:
            return "%d" % 0
        else:
            return "%.1f" % ((float(used) / float(size)) * 100)

@register.filter    
def sum(value, arg):
    return value + arg

@register.filter    
def sub(value, arg):
    return value - arg

@register.filter
def age(value):
    now = datetime.now()
    try:
        difference = now - value
    except:
        return value

    if difference <= timedelta(minutes=1):
        return 'just now'
    return '%(time)s ago' % {'time': timesince(value).split(', ')[0]}