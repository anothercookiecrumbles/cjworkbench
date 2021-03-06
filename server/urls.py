from django.conf.urls import url
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from . import views
from .views.WfModule import wfmodule_detail,wfmodule_render,wfmodule_input,wfmodule_public_output


urlpatterns = [
    # ex: /
    #    url(r'^$', views.index, name='index'),

    url(r'^$', RedirectView.as_view(url='/workflows')),

    # list all workflows
    url(r'^workflows/$', views.workflows2),
    url(r'^api/workflows/?$', views.workflow_list),

    # list specific workflow ex: /workflows/5/
    url(r'^workflows/(?P<pk>[0-9]+)/$', TemplateView.as_view(template_name='workflow.html')),
    url(r'^api/workflows/(?P<pk>[0-9]+)/?$', views.workflow_detail),

    url(r'^api/workflows/(?P<pk>[0-9]+)/addmodule/?$', views.workflow_addmodule),

    # modules
    url(r'^api/modules/?$', views.module_list),
    url(r'^api/modules/(?P<pk>[0-9]+)/?$', views.module_detail),

    url(r'^api/initmodules/$', views.init_modules2),
    url(r'^api/importfromgithub/?$', views.import_from_github),
    url(r'^api/refreshfromgithub/?$', views.refresh_from_github),

    # WfModules (Modules applied in a workflow)
    url(r'^api/wfmodules/(?P<pk>[0-9]+)/?$', wfmodule_detail),
    url(r'^api/wfmodules/(?P<pk>[0-9]+)/render$', wfmodule_render),
    url(r'^api/wfmodules/(?P<pk>[0-9]+)/input$', wfmodule_input),

    url(r'^public/moduledata/live/(?P<pk>[0-9]+)\.(?P<type>(csv|json))?$', wfmodule_public_output),

    # Parameters
    url(r'^api/parameters/(?P<pk>[0-9]+)/?$', views.parameterval_detail),
    url(r'^api/parameters/(?P<pk>[0-9]+)/event/?$', views.parameterval_event),

    url(r'^public/paramdata/live/(?P<pk>[0-9]+).png$', views.parameterval_png)

]

