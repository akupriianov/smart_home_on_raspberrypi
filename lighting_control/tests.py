#v1/lighting_control/tests.py

from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch, MagicMock
import time
from lighting_control import gpio_setup
from .tests_base import VerboseTestCase

class LightingControlTest(VerboseTestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='lightuser', password='lightpass')
        self.client.login(username='lightuser', password='lightpass')

    @patch('lighting_control.gpio_setup.GPIO')
    def test_turn_light_on(self, mock_gpio):
        """
        Test widoku włączenia światła.
        """
        url = reverse('control-light')
        response = self.client.post(url, {'action': 'on'})
        self.assertEqual(response.status_code, 302)  # przekierowanie
        # Sprawdzamy, czy pin został ustawiony w stan wysoki
        mock_gpio.output.assert_called_with(gpio_setup.RELAY_GPIO_PIN, mock_gpio.HIGH)

    @patch('lighting_control.gpio_setup.GPIO')
    def test_turn_light_off(self, mock_gpio):
        """
        Test widoku wyłączenia światła.
        """
        url = reverse('control-light')
        response = self.client.post(url, {'action': 'off'})
        self.assertEqual(response.status_code, 302)
        mock_gpio.output.assert_called_with(gpio_setup.RELAY_GPIO_PIN, mock_gpio.LOW)

    @patch('lighting_control.gpio_setup.GPIO')
    def test_get_light_state_view(self, mock_gpio):
    # Ustawiamy w mocku to, co w realnym RPi.GPIO
        mock_gpio.HIGH = 1
        mock_gpio.LOW = 0

    # Symulujemy, że odczyt pinu zwraca "HIGH"
        mock_gpio.input.return_value = mock_gpio.HIGH

        url = reverse('control-light')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lighting_control/control_panel.html')

    # Teraz oczekujemy, że w kontekście będzie light_is_on = True
        self.assertTrue(response.context['light_is_on'])

class LightingControlSecurityTest(VerboseTestCase):
    """
    Testy bezpieczeństwa dla lighting_control.
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='lightsecure', password='lightpass')

    def test_protected_lighting_view_without_login(self):
        """
        Sprawdza, czy niezalogowany użytkownik nie może wejść na widok sterowania oświetleniem (control-light).
        """
        url = reverse('control-light')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

class LightingControlPerformanceTest(VerboseTestCase):
    """
    Prosty test wydajnościowy dla lighting_control.
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='lightperf', password='lightperf')
        self.client.login(username='lightperf', password='lightperf')
        # Widok sterowania oświetleniem
        self.url = reverse('control-light')

    def test_sequential_light_requests(self):
        """
        Wysyła kilka zapytań GET do widoku sterowania oświetleniem i mierzy czas.
        """
        start_time = time.time()
        num_requests = 10

        for _ in range(num_requests):
            response = self.client.get(self.url)
            # Zakładamy, że widok GET wyświetla panel z buttonami
            self.assertEqual(response.status_code, 200)

        total_time = time.time() - start_time
        self.assertLess(total_time, 3.0,
                        f"Oczekiwano < 3s, a wykonanie trwało {total_time:.2f}s")

        print(f"[LIGHTING_CONTROL] {num_requests} zapytań w czasie {total_time:.2f}s")
