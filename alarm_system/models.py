# v1/alarm_system/models.py
from django.db import models
from django.utils import timezone

class AlarmEvent(models.Model):
    """
    Log zdarzeń alarmowych:
    - event_type: np. "PIR", "Kontaktron"
    - timestamp : czas wystąpienia
    - message   : np. "Wykryto ruch", "Drzwi otwarte"
    """
    event_type = models.CharField(max_length=50)
    timestamp = models.DateTimeField(default=timezone.now)
    message = models.CharField(max_length=200)

    def __str__(self):
        return f"[{self.timestamp}] {self.event_type}: {self.message}"

class AlarmSettings(models.Model):
    is_armed = models.BooleanField(default=False)       # w pełni uzbrojony
    is_arming = models.BooleanField(default=False)      # czy trwa odliczanie
    arming_start_time = models.DateTimeField(null=True, blank=True)

    # NOWE: które czujniki mają reagować
    pir_enabled = models.BooleanField(default=True)
    door_enabled = models.BooleanField(default=True)

    def __str__(self):
        status = "ARMED" if self.is_armed else "DISARMED"
        if self.is_arming:
            status = "ARMING..."
        return f"Alarm: {status} (PIR={self.pir_enabled}, DOOR={self.door_enabled})"