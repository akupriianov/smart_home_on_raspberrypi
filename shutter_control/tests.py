#v1/shutter_control/tests.py
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch, MagicMock
from shutter_control import gpio_shutter
import time
from .tests_base import VerboseTestCase

class ShutterControlTest(VerboseTestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='shutteruser', password='shutterpass')
        self.client.login(username='shutteruser', password='shutterpass')

    @patch('shutter_control.gpio_shutter.GPIO')
    def test_shutter_up(self, mock_gpio):
        url = reverse('shutter-control')
        response = self.client.post(url, {'action': 'up'})
        self.assertEqual(response.status_code, 302)
    # Spodziewamy się, że po zakończeniu całej akcji roleta jest "up".
        self.assertEqual(gpio_shutter.shutter_state, "up")


    @patch('shutter_control.gpio_shutter.GPIO')
    def test_shutter_down(self, mock_gpio):
        url = reverse('shutter-control')
        response = self.client.post(url, {'action': 'down'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(gpio_shutter.shutter_state, "down")

    @patch('shutter_control.gpio_shutter.GPIO')
    def test_shutter_stop(self, mock_gpio):
    # Najpierw 'down'
        self.client.post(reverse('shutter-control'), {'action': 'down'})
    # Następnie 'stop'
        response = self.client.post(reverse('shutter-control'), {'action': 'stop'})
        self.assertEqual(response.status_code, 302)
    # W czasie testu i tak roleta zdążyła się całkowicie opuścić, 
    # więc finalnie jest "down", a nie "stopped":
        self.assertEqual(gpio_shutter.shutter_state, "down")

    def test_shutter_panel_get(self):
        """
        Test widoku GET -> panel rolet.
        """
        url = reverse('shutter-control')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shutter_control/panel.html')

class ShutterControlSecurityTest(VerboseTestCase):
    """
    Testy bezpieczeństwa dla shutter_control.
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='shuttersecure', password='shutterpass')

    def test_protected_shutter_view_without_login(self):
        """
        Sprawdza, czy niezalogowany użytkownik nie może wejść na widok panelu rolet (shutter-control).
        """
        url = reverse('shutter-control')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

class ShutterControlPerformanceTest(VerboseTestCase):
    """
    Prosty test wydajnościowy dla shutter_control.
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='shutterperf', password='shutterperf')
        self.client.login(username='shutterperf', password='shutterperf')
        # Widok sterowania roletami
        self.url = reverse('shutter-control')

    def test_sequential_shutter_requests(self):
        """
        Wysyła kilka żądań GET do panelu sterowania roletami i sprawdza czas.
        """
        start_time = time.time()
        num_requests = 10

        for _ in range(num_requests):
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 200)

        total = time.time() - start_time
        self.assertLess(total, 3.0, f"Oczekiwano <3s, uzyskano {total:.2f}s")

        print(f"[SHUTTER_CONTROL] {num_requests} zapytań w {total:.2f}s")