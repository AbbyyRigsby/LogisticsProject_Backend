from django.apps import apps
from django.urls import reverse

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse

import networkx as nx

from .serializers import LogisticsPathSerializer, PortListSerializer
from .functions import shortest_path

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'ports': reverse('ports-list', request=request, format=format),
        'shortest-path': reverse('shortest-path', request=request, format=format),
        'status': 'Logistics Engine Online',
        'version': 'v1.0.0'
    })

class ShortestPathView(APIView):
    def post(self, request, *args, **kwargs):
        # Placeholder for actual shortest path logic
        graph = apps.get_app_config('api').graph

        start_point = request.data.get('start_point')
        end_point = request.data.get('end_point')

        if not start_point or not end_point:
            return Response({"error": "Start and end points are required."})

        try:
            result = shortest_path.find_shortest_path(graph, start_point, end_point)
            serializer = LogisticsPathSerializer(data=result)
            
            if not serializer.is_valid():
                print(serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except (nx.NodeNotFound, nx.NetworkXNoPath):
            return Response(
                {"error": "One or both ports not found, or no path exists."},
                status= status.HTTP_404_NOT_FOUND
            )
        
class PortsListView(APIView):
    def get(self, request, *args, **kwargs):
        graph = apps.get_app_config('api').graph
        # Just get a list of names
        port_names = sorted(list(graph.nodes))

        # Wrap it in a dict: {"ports": ["Name 1", "Name 2"]}
        serializer = PortListSerializer(data={"ports": port_names})
        
        if serializer.is_valid():
            return Response(serializer.data)
        return Response(serializer.errors, status=400)