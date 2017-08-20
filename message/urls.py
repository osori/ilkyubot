from django.conf.urls import url

from . import views

app_name = 'message'

urlpatterns = [
	# keyboard
	url(r'^$', views.message, name='message'),
]