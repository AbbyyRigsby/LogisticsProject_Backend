from rest_framework import serializers
from .models import Path

class NodeDetailSerializer(serializers.Serializer):
    name = serializers.CharField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    country_code = serializers.CharField()
    category = serializers.CharField()

class LogisticsPathSerializer(serializers.Serializer):
    start_point = serializers.CharField()
    end_point = serializers.CharField()
    distance_miles = serializers.IntegerField()
    # For drawing the line on the map
    map_polyline = serializers.ListField(
        child=serializers.ListField(child=serializers.FloatField())
    )
    # For showing the stop-by-stop list
    path_details = NodeDetailSerializer(many=True)