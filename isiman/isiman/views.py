from django.http import HttpResponse
from django.shortcuts import render_to_response
from isiman.libs import isilon, utils
from isiman.models import *
from django.contrib.auth.decorators import login_required

def index(request):
    clusters = Cluster.objects.all()
    events = Events.objects.all()
    smartpools = SmartPools.objects.all()
    jobs = Jobs.objects.all()
    return render_to_response('isiman/index.html',
                            {
                                'clusters': clusters,
                                'events': events,
                                'smartpools': smartpools,
                                'jobs': jobs
                            })

def clusters(request):
    clusters = Cluster.objects.all()
    return render_to_response('isiman/clusters.html', {'clusters': clusters})

def jobs(request):
    clusters = Cluster.objects.all()
    return render_to_response('isiman/jobs.html', {'clusters': clusters})

def events(request):
    clusters = Cluster.objects.all()
    return render_to_response('isiman/events.html', {'clusters': clusters})

def details(request, cluster):
    cluster = Cluster.objects.get(id=cluster)
    return render_to_response('isiman/details.html', {'cluster': cluster})

def nodes(request, cluster):
    cluster = Cluster.objects.get(id=cluster)
    return render_to_response('isiman/nodes.html', {'cluster': cluster})