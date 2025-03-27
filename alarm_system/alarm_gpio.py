#v1/alarm_system/alarm_gpio.py
import RPi.GPIO as GPIO
import time
from django.utils import timezone
from alarm_system.models import AlarmEvent, AlarmSettings
import logging

logger = logging.getLogger(__name__)

ARMING_DELAY_SECONDS = 20
PIR_PIN = 23
DOOR_PIN = 16
ALARM_PIN = 20
LED_PIN = 24

previous_pir_state = 0
previous_door_state = 0

def setup_gpio():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PIR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(DOOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(ALARM_PIN, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(LED_PIN, GPIO.OUT, initial=GPIO.LOW)

def check_arming_status():
    """
    Jeśli is_arming=True i minęło >= ARMING_DELAY_SECONDS,
    przełącz is_armed=True, is_arming=False.
    """
    settings, _ = AlarmSettings.objects.get_or_create(pk=1)
    if settings.is_arming and settings.arming_start_time:
        now = timezone.now()
        delta = now - settings.arming_start_time
        if delta.total_seconds() >= ARMING_DELAY_SECONDS:
            settings.is_arming = False
            settings.is_armed = True
            settings.save()

            AlarmEvent.objects.create(
                event_type="System",
                message="Alarm uzbrojony (opóźnione)"
            )

def check_sensors():
    """
    Sprawdza stan czujników, loguje zmianę (otwarcie/zamknięcie, ruch/brak ruchu),
    ale zwraca True, jeśli aktualnie mamy stan alarmowy (PIR=1 / DOOR=1).
    """
    settings, _ = AlarmSettings.objects.get_or_create(pk=1)
    if not settings.is_armed:
        return False

    global previous_pir_state, previous_door_state

    pir_state = GPIO.input(PIR_PIN)   # 1 = ruch
    door_state = GPIO.input(DOOR_PIN) # 1 = otwarte (NO)

    # Sprawdź, czy PIR zmienił stan
    if settings.pir_enabled and (pir_state != previous_pir_state):
        if pir_state == 1:
            AlarmEvent.objects.create(event_type="PIR", message="Wykryto ruch (PIR).")
            logger.info("Wykryto ruch (PIR).")
        else:
            AlarmEvent.objects.create(event_type="PIR", message="Ruch (PIR) ustał.")
            logger.info("Ruch (PIR) ustał.")

        previous_pir_state = pir_state

    # Sprawdź, czy DOOR zmienił stan
    if settings.door_enabled and (door_state != previous_door_state):
        if door_state == 1:
            AlarmEvent.objects.create(event_type="Door", message="Drzwi/okno otwarte.")
            logger.info("Drzwi/okno otwarte.")
        else:
            AlarmEvent.objects.create(event_type="Door", message="Drzwi/okno zamknięte.")
            logger.info("Drzwi/okno zamknięte.")

        previous_door_state = door_state

    # Zwracamy True, jeśli PIR=1 lub DOOR=1 (i czujnik jest włączony)
    if (settings.pir_enabled and pir_state == 1) or (settings.door_enabled and door_state == 1):
        return True
    return False

def activate_alarm():
    """ Włącza syrenę i rozpoczyna miganie diody LED. """
    GPIO.output(ALARM_PIN, GPIO.HIGH)
    logger.info("Alarm aktywowany.")

    import threading
    def blink_led():
        while GPIO.input(ALARM_PIN) == GPIO.HIGH:
            GPIO.output(LED_PIN, not GPIO.input(LED_PIN))
            time.sleep(0.5)

    thread = threading.Thread(target=blink_led)
    thread.daemon = True
    thread.start()

def deactivate_alarm():
    """ Wyłącza syrenę i zatrzymuje miganie diody LED. """
    GPIO.output(ALARM_PIN, GPIO.LOW)
    GPIO.output(LED_PIN, GPIO.LOW)
    logger.info("Alarm deaktywowany.")
