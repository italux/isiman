from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from isiman.libs import isilon

class Clusters(models.Model):
    name = models.CharField(max_length=100, blank=False)
    version = models.CharField(max_length=100)
    address = models.CharField(max_length=100, blank=False)
    username = models.CharField(max_length=100, blank=False)
    password = models.CharField(max_length=32, blank=False)
    ssh_key = models.CharField(max_length=5000, blank=False)
    status = models.CharField(max_length=100)
    cpu_usage = models.IntegerField(default=0)
    modified_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.name

class Nodes(models.Model):
    cluster = models.ForeignKey(Clusters)
    name = models.CharField(max_length=100)
    node_id = models.IntegerField()
    ipaddress = models.CharField(max_length=100)
    lnn = models.IntegerField()
    status = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    serial = models.CharField(max_length=100)
    client_conn = models.IntegerField(default=0)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['lnn']

    def __unicode__(self):
        return self.name

class Events(models.Model):
    id = models.FloatField(primary_key=True)
    cluster = models.ForeignKey(Clusters)
    node_lnn = models.CharField(max_length=10)
    severity = models.CharField(max_length=1)
    message = models.CharField(max_length=500)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['start_time']

    def __unicode__(self):
        return self.message

class Jobs(models.Model):
    id = models.IntegerField(primary_key=True)
    cluster = models.ForeignKey(Clusters)
    name = models.CharField(max_length=100)
    impact = models.CharField(max_length=50)
    priority = models.IntegerField(null=True)
    policy = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    progress = models.CharField(max_length=1000)
    create_time = models.CharField(max_length=100)
    running_time = models.CharField(max_length=100)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['state']

    def __unicode__(self):
        return self.name

class SmartPools(models.Model):
    cluster = models.ForeignKey(Clusters)
    name = models.CharField(max_length=100)
    ssd_used = models.BigIntegerField(default=0)
    ssd_size = models.BigIntegerField(default=0)
    hdd_used = models.BigIntegerField(default=0)
    hdd_size = models.BigIntegerField(default=0)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-name']

    def __unicode__(self):
        return self.name

class Snapshots(models.Model):
    id = models.IntegerField(primary_key=True)
    cluster = models.ForeignKey(Clusters)
    name = models.CharField(max_length=500)
    path = models.CharField(max_length=500)
    size = models.BigIntegerField(default=0)
    state = models.CharField(max_length=32)
    created = models.DateTimeField()
    expires = models.DateTimeField(null=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created']

    def __unicode__(self):
        return self.name