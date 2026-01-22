from django.apps import AppConfig
from .functions.graph_setup import graph_process


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    graph = None

    def ready(self):
        print("Loading Logistics API...")

        try:
            self.graph = graph_process()
        except Exception as e:
            print(f"Error during graph processing: {e}")

    