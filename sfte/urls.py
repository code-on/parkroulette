from django.conf.urls import patterns, include, url

from django.contrib.gis import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'content.views.home', name='home'),
    url(r'^chance/$', 'content.views.get_chance', name='get-chance'),
    url(r'^laws/$', 'content.views.get_laws', name='get-laws'),
    url(r'^heatmap/$', 'content.views.get_heatmap', name='get-heatmap'),
    url(r'^debug/$', 'content.views.debug', name='debug'),

    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('django.contrib.flatpages.views',
    url(r'^about/$', 'flatpage', {'url': '/about/'}, name='about'),
    url(r'^contact/$', 'flatpage', {'url': '/contact/'}, name='contact'),
    url(r'^privacy/$', 'flatpage', {'url': '/privacy/'}, name='privacy'),
    url(r'^disclaimer/$', 'flatpage', {'url': '/disclaimer/'}, name='disclaimer'),

)

urlpatterns += staticfiles_urlpatterns()
