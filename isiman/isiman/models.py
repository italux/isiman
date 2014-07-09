from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from isiman.libs import isilon

class Cluster(models.Model):
    name = models.CharField(max_length=100)
    version = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    ssh_key = models.CharField(max_length=5000)
    status = models.CharField(max_length=100)
    cpu_usage = models.IntegerField(default=0)
    modified_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.name

class Nodes(models.Model):
    cluster = models.ForeignKey(Cluster)
    name = models.CharField(max_length=100)
    lnn = models.IntegerField()
    isilon_id = models.IntegerField()
    status = models.CharField(max_length=100)
    client_conn = models.IntegerField(default=0)
    modified_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['isilon_id']

    def __unicode__(self):
        return self.name

class Events(models.Model):
    cluster = models.ForeignKey(Cluster)
    event_id = models.CharField(max_length=30)
    node_lnn = models.CharField(max_length=10)
    severity = models.CharField(max_length=1)
    message = models.CharField(max_length=500)
    modified_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.message

class Jobs(models.Model):
    cluster = models.ForeignKey(Cluster)
    name = models.CharField(max_length=100)
    impact = models.CharField(max_length=50)
    priority = models.IntegerField(null=True)
    policy = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    running_time = models.CharField(max_length=100)
    modified_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['state']

    def __unicode__(self):
        return self.name

class SmartPools(models.Model):
    cluster = models.ForeignKey(Cluster)
    name = models.CharField(max_length=100)
    ssd_used = models.BigIntegerField(default=0)
    ssd_size = models.BigIntegerField(default=0)
    hdd_used = models.BigIntegerField(default=0)
    hdd_size = models.BigIntegerField(default=0)
    modified_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name