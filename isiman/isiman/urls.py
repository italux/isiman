from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'isiman.views.index'),
    url(r'^clusters/$', 'isiman.views.clusters'),
    url(r'^clusters/(?P<cluster>\d+)/$', 'isiman.views.details'),
    url(r'^clusters/(?P<cluster>\d+)/nodes/$', 'isiman.views.nodes'),
    url(r'^jobs/$', 'isiman.views.jobs'),
    url(r'^events/$', 'isiman.views.events'),
    url(r'^admin/', include(admin.site.urls)),
)