from django.urls import path

from project.views import CreateProjectView

urlpatterns = [
    path('create/', CreateProjectView.as_view(), name='create_project'),
]
