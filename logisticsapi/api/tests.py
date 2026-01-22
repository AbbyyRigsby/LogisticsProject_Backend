from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

class LogisticsTests(APITestCase):
    def test_shortest_path_success(self):
        url = reverse('shortest-path')
        data = {
            'start_point': 'Addis Ababa Bole International Airport', 
            'end_point': 'Changdianhekou'
        }

        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        print(f"TEST ONE RESULTS: {response.data}")

    def test_invalid_port(self):
        url = reverse('shortest-path')
        data = {
            'start_point': 'Invalid Port Name', 
            'end_point': 'Invalid Port 2'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        print(f"TEST TWO RESULTS: {response.data}")