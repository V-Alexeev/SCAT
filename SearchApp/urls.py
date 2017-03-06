from django.conf.urls.defaults import *
from django.views.generic import DetailView, ListView, RedirectView
from models import Word, Manuscript
from django.core.urlresolvers import reverse

urlpatterns = patterns('SearchApp.views',
    url(r'^word/(?P<word_id>[^/]+)/page/$', 'showWordPage', name="scat-show-word-page"),    
    url(r'^word/(?P<pk>[^/]+)/details/$', DetailView.as_view(
            model=Word,
            template_name='SearchApp/WordDetails.html'), name="scat-show-word-details"),
    url(r'^search/$', 'search', name="scat-search"),
    url(r'^uploadGramData/$', 'uploadGramData'),
    url(r'^uploadManuscript/$', 'uploadManuscript'),
    url(r'^manuscript/(?P<man_slug>[^/]+)/page/(?P<page_number>\d+)(?P<back>b?)/$', 'showManuscriptPage', name="scat-show-page"),
    url(r'^manuscript/(?P<man_slug>[^/]+)/$', RedirectView.as_view(url="../../word/%(man_slug)s.1/page/", permanent=False),
    	name="scat-show-manuscript"),
    url(r'^$',  ListView.as_view(template_name='SearchApp/Index.html', queryset=Manuscript.objects.all().order_by("name")))
)

