from django import forms
from django.contrib import admin
from isiman.models import Clusters, Events

class MyModelForm(forms.ModelForm):
    ssh_key = forms.CharField(widget=forms.Textarea)

class ClusterAdmin(admin.ModelAdmin):
    form = MyModelForm
    fields = ['name', 'address', 'version', 'username', 'password', 'ssh_key']
    list_display = ('name', 'version', 'status', 'username', 'modified_at')

admin.site.register(Clusters, ClusterAdmin)