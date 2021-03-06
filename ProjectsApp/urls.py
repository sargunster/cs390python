"""ProjectsApp URL Configuration

Created by Harris Christiansen on 10/02/16.
"""
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^project/all$', views.getProjects, name='Projects'),
    url(r'^project/form$', views.getProjectForm, name='ProjectForm'),
    url(r'^project$', views.getProject, name='Project'),
    url(r'^project/delete$', views.deleteProject, name='DeleteProject'),
    url(r'^project/edit$', views.update_project, name='UpdateProject')
]
