# v1/acces_control/models.py

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class RFIDCard(models.Model):
    """
    Reprezentacja karty RFID w bazie danych.
    uid: unikatowy identyfikator karty
    owner: informacja o właścicielu karty
    metoda zwraca tekstową reprezentację do wyświetlanaia
    """
    uid = models.CharField(max_length=50, unique=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return f"Karta {self.uid} (Właściciel: {self.owner or 'brak'})"
    

class LatestScan(models.Model):
    """
    Model przechowujący ostatni odczytany UID karty.
    uid: pole przechuwuję ostatnio zeskanowaną kartę
    metoda zwracą tekstową reprezentację odczytanej karty
    """
    uid = models.CharField(max_length=50, blank=True, null=True)
    def __str__(self):
        return f"Ostatni skan: {self.uid}"
    

class AccessLog(models.Model):
    """
    Log zdarzeń związanych z użyciem kart RFID
    card: powiązanie z kartą, której dotyczy log
    timestamp: data i godzina zdarzenia
    message: informacja dotycząca zdarzenia
    metoda zwraca czytelny czas i opis zdzrzenia
    """
    card = models.ForeignKey('RFIDCard', on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    message = models.CharField(max_length=200)
    def __str__(self):
        return f"[{self.timestamp}] {self.message}"
