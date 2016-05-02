from django.conf.urls import url
from django.views.generic.base import RedirectView
from . import views

app_name = 'pt'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/favicon.ico', permanent=True))
]
