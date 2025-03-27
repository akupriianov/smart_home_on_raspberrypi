# v1/alarm_system/test.py
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from unittest.mock import patch, MagicMock
import time
from alarm_system.models import AlarmEvent, AlarmSettings
from alarm_system.alarm_gpio import setup_gpio, check_arming_status, check_sensors, activate_alarm, deactivate_alarm
from .tests_base import VerboseTestCase

class AlarmModelsTest(VerboseTestCase):
    def test_alarm_event_creation(self):
        event = AlarmEvent.objects.create(
            event_type="PIR",
            message="Wykryto ruch"
        )
        self.assertIn("Wykryto ruch", str(event))
        self.assertEqual(event.event_type, "PIR")

    def test_alarm_settings_default(self):
        settings = AlarmSettings.objects.create()
        self.assertFalse(settings.is_armed)
        self.assertFalse(settings.is_arming)
        self.assertTrue(settings.pir_enabled)
        self.assertTrue(settings.door_enabled)

class AlarmViewsTest(VerboseTestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='user', password='pass')
        self.client.login(username='user', password='pass')

    def test_alarm_event_list_view(self):
        url = reverse('alarm-events-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'alarm_system/event_list.html')

    def test_toggle_alarm_view_disarm(self):
        """
        Test rozbrojenia alarmu.
        """
        settings = AlarmSettings.objects.create(is_armed=True, is_arming=False)
        url = reverse('alarm-toggle')
        response = self.client.post(url, {'action': 'disarm'})
        settings.refresh_from_db()
        self.assertFalse(settings.is_armed)
        self.assertFalse(settings.is_arming)
        self.assertEqual(response.status_code, 302)  # przekierowanie

    def test_toggle_alarm_view_arm_immediate(self):
        """
        Test uzbrojenia alarmu "natychmiast" przy włączonym PIR i drzwiach.
        """
        settings = AlarmSettings.objects.create()
        url = reverse('alarm-toggle')
        response = self.client.post(url, {'action': 'arm_both_immediate'})
        settings.refresh_from_db()
        self.assertTrue(settings.is_armed)
        self.assertFalse(settings.is_arming)
        self.assertTrue(settings.pir_enabled)
        self.assertTrue(settings.door_enabled)
        self.assertEqual(response.status_code, 302)

class AlarmGpioLogicTest(VerboseTestCase):
    """
    Testy funkcjonalne z mockowaniem GPIO.
    """
    def setUp(self):
        self.settings = AlarmSettings.objects.create()

    @patch('alarm_system.alarm_gpio.GPIO')
    def test_setup_gpio(self, mock_gpio):
        setup_gpio()
        # Sprawdzamy, czy wywołano GPIO.setup na określonych pinach
        mock_gpio.setmode.assert_called_once()
        mock_gpio.setup.assert_any_call(23, mock_gpio.IN, pull_up_down=mock_gpio.PUD_DOWN)
        mock_gpio.setup.assert_any_call(16, mock_gpio.IN, pull_up_down=mock_gpio.PUD_UP)
        mock_gpio.setup.assert_any_call(20, mock_gpio.OUT, initial=mock_gpio.LOW)

    @patch('alarm_system.alarm_gpio.GPIO')
    def test_check_arming_status(self, mock_gpio):
        """
        Test sprawdzający przejście z is_arming=True do is_armed=True
        po upływie ARMING_DELAY_SECONDS.
        """
        self.settings.is_arming = True
        self.settings.arming_start_time = timezone.now() - timezone.timedelta(seconds=21)
        self.settings.save()

        check_arming_status()
        self.settings.refresh_from_db()
        self.assertTrue(self.settings.is_armed)
        self.assertFalse(self.settings.is_arming)

    @patch('alarm_system.alarm_gpio.GPIO')
    def test_sensors_trigger(self, mock_gpio):
        """
        Sprawdzenie, czy przy uzbrojonym alarmie i stanie wysokim na PIR
        następuje aktywacja alarmu.
        """
        self.settings.is_armed = True
        self.settings.pir_enabled = True
        self.settings.save()

        # Symulacja stanu wysokiego na PIR
        mock_gpio.input.side_effect = [1, 0]  # PIR_PIN=1, DOOR_PIN=0
        triggered = check_sensors()
        self.assertTrue(triggered, "Alarm powinien zostać wzbudzony przez PIR=1")

    @patch('alarm_system.alarm_gpio.GPIO')
    def test_activate_deactivate_alarm(self, mock_gpio):
        """
        Test sprawdza, czy funkcje activate_alarm i deactivate_alarm
        sterują pinami ALARM_PIN i LED_PIN.
        """
        activate_alarm()
        mock_gpio.output.assert_any_call(20, mock_gpio.HIGH)  # ALARM_PIN
        deactivate_alarm()
        mock_gpio.output.assert_any_call(20, mock_gpio.LOW)

class AlarmSystemSecurityTest(VerboseTestCase):
    """
    Testy bezpieczeństwa dla alarm_system.
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='alarmsecure', password='alarmpass')

    def test_protected_alarm_view_without_login(self):
        """
        Sprawdza, czy niezalogowany użytkownik nie może wejść na widok alarmu (toggle).
        """
        url = reverse('alarm-toggle')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_brute_force_simulation(self):
        """
        Niewielka symulacja ataku siłowego na logowanie dla alarmu.
        """
        login_url = reverse('login')
        for i in range(3):
            response = self.client.post(login_url, {'username': 'nobody', 'password': f'fail{i}'})
            self.assertEqual(response.status_code, 200)  # dalej formularz
            self.assertFalse('_auth_user_id' in self.client.session)

class AlarmSystemPerformanceTest(VerboseTestCase):
    """
    Prosty test wydajnościowy dla alarm_system.
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='alarmperf', password='alarmperf')
        self.client.login(username='alarmperf', password='alarmperf')
        # Widok alarmu - np. listy zdarzeń alarmowych
        self.url = reverse('alarm-events-list')

    def test_sequential_requests_alarm_events(self):
        """
        Wysyła kilkanaście zapytań do listy zdarzeń alarmu (alarm-events-list).
        """
        start = time.time()
        num_requests = 10

        for _ in range(num_requests):
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 200)

        elapsed = time.time() - start
        self.assertLess(elapsed, 3.0,
                        f"Łączny czas {num_requests} zapytań = {elapsed:.2f}s, oczekiwano < 3s")

        print(f"[ALARM_SYSTEM] Wykonano {num_requests} zapytań w czasie {elapsed:.2f}s")