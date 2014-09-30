from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from isiman.libs import isilon, utils
from isiman.models import *
import math

@login_required
def dashboard(request):
    clusters = Clusters.objects.all()
    eventscrit = Events.objects.filter(severity='C').count()
    smartpools = SmartPools.objects.all()
    nodes = Nodes.objects.all()
    smartpools_hdd_used = SmartPools.objects.aggregate(total=Sum('hdd_used'))
    smartpools_hdd_size = SmartPools.objects.aggregate(total=Sum('hdd_size'))
    nodes_models_list = Nodes.objects.values_list('model', flat=True).distinct()
    models = utils.uniq(nodes_models_list)
    return render_to_response('isiman/dashboard.html', {
                                'clusters': clusters,
                                'eventscrit': eventscrit,
                                'smartpools': smartpools,
                                'smartpools_hdd_used': smartpools_hdd_used,
                                'smartpools_hdd_size': smartpools_hdd_size,
                                'nodes': nodes,
                                'models': models
                            }, context_instance=RequestContext(request))

@login_required
def clusters(request):
    clusters = Clusters.objects.all()
    eventscrit = Events.objects.filter(severity='C').count()
    return render_to_response('isiman/clusters.html', {
                                'clusters': clusters,
                                'eventscrit': eventscrit
                            }, context_instance=RequestContext(request))

@login_required
def jobs(request):
    clusters = Clusters.objects.all()
    eventscrit = Events.objects.filter(severity='C').count()
    return render_to_response('isiman/jobs.html', {
                                'clusters': clusters,
                                'eventscrit': eventscrit
                            }, context_instance=RequestContext(request))

@login_required
def events(request):
    clusters = Clusters.objects.all()
    eventscrit = Events.objects.filter(severity='C').count()
    return render_to_response('isiman/events.html', {
                                'clusters': clusters,
                                'eventscrit': eventscrit
                            }, context_instance=RequestContext(request))

@login_required
def details(request, cluster):
    clusters = Clusters.objects.all()
    cluster = Clusters.objects.get(name=cluster)
    eventscrit = Events.objects.filter(severity='C').count()
    smartpools_hdd_used = SmartPools.objects.filter(cluster=cluster).aggregate(total=Sum('hdd_used'))
    smartpools_hdd_size = SmartPools.objects.filter(cluster=cluster).aggregate(total=Sum('hdd_size'))
    nodes_model_list = Nodes.objects.filter(cluster=cluster).values_list('model', flat=True).distinct()
    nodes_model = utils.uniq(nodes_model_list)
    snaplist_bydate = []
    snapdates = Snapshots.objects.filter(cluster=cluster).values_list('created', flat=True).distinct()
    for date in snapdates:
        snaplist_bydate.append(date.strftime('%d/%m/%Y'))
    snapshots_bydate = utils.uniq(reversed(snaplist_bydate))
    return render_to_response('isiman/details.html', {
                                'cluster': cluster,
                                'clusters': clusters,
                                'eventscrit': eventscrit,
                                'smartpools_hdd_used':smartpools_hdd_used,
                                'smartpools_hdd_size':smartpools_hdd_size,
                                'nodes_model': nodes_model,
                                'snapshots_bydate': snapshots_bydate
                            }, context_instance=RequestContext(request))

def calculator(request):
    clusters = Clusters.objects.all()
    if request.method == 'POST':
        nodes = request.POST.get('nodes')
        drives = request.POST.get('drives')
        drivesize = request.POST.get('drivesize')
        protection = request.POST.get('protection')
        vhs_qtd =  request.POST.get('vhs')
        raw_b10 = (int(nodes) * int(drives) * float(drivesize))
        raw_b2 = float(int(raw_b10) * float((1000**4))/(1024**4))
        os = raw_b2 * 0.01
        filesystem = (raw_b2 - os) * 0.000083
        vhs = int(vhs_qtd) * float(drivesize)
        percent_overhead = float(isilon.isi_protection_overhead(protection, int(nodes))/100)
        overhead = ((raw_b2 - os - filesystem) * percent_overhead)
        result = math.ceil(raw_b2 - os - filesystem - overhead - vhs)
        return render_to_response('isiman/calculator.html', {'result': result, 'clusters': clusters}, context_instance=RequestContext(request))
    else:
        return render_to_response('isiman/calculator.html', {'clusters': clusters}, context_instance=RequestContext(request))
