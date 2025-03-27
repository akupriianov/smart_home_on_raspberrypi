# v1/acces_control/tests.py
import json
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch, MagicMock
import threading
import time
from acces_control.models import RFIDCard, LatestScan, AccessLog
from .tests_base import VerboseTestCase

class RFIDCardModelTest(VerboseTestCase):
    """
    Testy jednostkowe modelu RFIDCard.
    """
    def test_create_rfid_card(self):
        user = User.objects.create_user(username='testuser', password='testpass')
        card = RFIDCard.objects.create(uid='ABC123', owner=user)
        self.assertEqual(card.uid, 'ABC123')
        self.assertEqual(card.owner, user)
        self.assertIn('Karta ABC123', str(card))

class LatestScanModelTest(VerboseTestCase):
    """
    Testy jednostkowe modelu LatestScan.
    """
    def test_create_latest_scan(self):
        scan = LatestScan.objects.create(uid='LAST_UID')
        self.assertEqual(scan.uid, 'LAST_UID')
        self.assertIn('Ostatni skan', str(scan))

class AccessLogModelTest(VerboseTestCase):
    """
    Testy jednostkowe modelu AccessLog.
    """
    def test_create_access_log(self):
        log = AccessLog.objects.create(message='Karta znana')
        self.assertIn('Karta znana', str(log))
        self.assertIsNotNone(log.timestamp)

class AccessControlViewsTest(VerboseTestCase):
    """
    Testy widoków listy kart, dodawania, usuwania i logów dostępu (widoki opierają się na CBV).
    """
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='admin', password='adminpass')
        self.client.login(username='admin', password='adminpass')

    def test_card_list_view(self):
        url = reverse('card-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'acces_control/card_list.html')

    def test_card_add_view(self):
        url = reverse('card-add')
        # Dodaj nową kartę
        response = self.client.post(url, {'uid': 'NEWCARD', 'owner': self.user.id})
        self.assertEqual(response.status_code, 302)  # przekierowanie
        # Sprawdź, czy karta została dodana
        self.assertTrue(RFIDCard.objects.filter(uid='NEWCARD').exists())

    def test_card_delete_view(self):
        card = RFIDCard.objects.create(uid='TODELETE')
        url = reverse('card-delete', args=[card.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  # przekierowanie
        # Sprawdź, czy karta została usunięta
        self.assertFalse(RFIDCard.objects.filter(uid='TODELETE').exists())

    def test_get_latest_card_view(self):
        """
        Test sprawdzający poprawne zwracanie ostatnio zeskanowanej karty w formacie JSON.
        """
        LatestScan.objects.create(pk=1, uid='XYZ123')
        url = reverse('get-latest-card')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['last_card_uid'], 'XYZ123')

    def test_logs_view(self):
        """
        Sprawdzenie, czy widok logów działa i używa właściwego szablonu.
        """
        url = reverse('access-log-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'acces_control/log_list.html')

class AccesControlSecurityTest(VerboseTestCase):
    """
    Testy bezpieczeństwa dla aplikacji acces_control.
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='secureuser', password='securepass')

    def test_protected_views_without_login(self):
        """
        Sprawdza, czy niezalogowany użytkownik nie ma dostępu do widoku listy kart
        (card-list) i zostanie przekierowany do strony logowania.
        """
        url = reverse('card-list')  # Widok listy kart (LoginRequiredMixin)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url, "Powinno przekierować na /login/")

    def test_brute_force_simulation(self):
        """
        Przykładowa symulacja kilku nieudanych prób logowania (atak siłowy).
        Nie testujemy realnego blokowania – jedynie sprawdzamy, że logowanie 
        ciągle się nie udaje, a status to 200 (formularz).
        """
        login_url = reverse('login')
        for i in range(3):  # kilka prób zły login/hasło
            response = self.client.post(login_url, {'username': 'wrong', 'password': f'invalid{i}'})
            self.assertEqual(response.status_code, 200)  # dalej formularz logowania
            self.assertFalse('_auth_user_id' in self.client.session, "User nadal niezalogowany")

    def test_unauthorized_gpio_access(self):
        """
        Sprawdza, czy niezalogowany użytkownik nie może wywołać widoku get_latest_card 
        lub innego widoku kontrolującego dostęp do RFID.
        """
        get_card_url = reverse('get-latest-card')
        response = self.client.get(get_card_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

class AccesControlPerformanceTest(VerboseTestCase):
    """
    Prosty test wydajnościowy dla acces_control (pokazowy).
    Wysyłamy sekwencyjnie kilka żądań GET do widoku 'card-list'.
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='perfuser', password='perfpass')
        self.client.login(username='perfuser', password='perfpass')
        # np. widok listy kart
        self.url = reverse('card-list')

    def test_sequential_requests(self):
        """
        Wysyła np. 10 żądań GET sekwencyjnie i mierzy łączny czas wykonania.
        """
        start_time = time.time()
        num_requests = 10

        for _ in range(num_requests):
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 200)

        total_time = time.time() - start_time
        # Zakładamy, że 10 zapytań powinno się zmieścić np. w 3 sekundach
        self.assertLess(total_time, 3.0,
                        f"Łączny czas {num_requests} zapytań = {total_time:.2f}s, oczekiwano < 3s")

        print(f"[ACCES_CONTROL] Wykonano {num_requests} zapytań w czasie {total_time:.2f}s")
        