from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'isiman.views.dashboard'),
    url(r'^dashboard/$', 'isiman.views.dashboard'),
    url(r'^clusters/$', 'isiman.views.clusters'),
    # url(r'^clusters/(?P<cluster>\d+)/$', 'isiman.views.details'),
    url(r'^clusters/(?P<cluster>\S+)/$', 'isiman.views.details'),
    url(r'^jobs/$', 'isiman.views.jobs'),
    url(r'^events/$', 'isiman.views.events'),
    url(r'^calculator/$', 'isiman.views.calculator'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', 'django.contrib.auth.views.login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login'),
)