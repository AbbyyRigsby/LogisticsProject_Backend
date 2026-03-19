from django.urls import include, path
from .views import PortsListView, ShortestPathView, api_root

urlpatterns = [
    path('', 
         api_root, 
         name='api-root'),
    
    path('shortest-path/', 
         ShortestPathView.as_view(), 
         name='shortest-path'),

     path('ports',
           PortsListView.as_view(),
           name='ports-list'
      ),
]