# v1/acces_control/rfid_reader.py
import RPi.GPIO as GPIO
import time
from pirc522 import RFID
from django.conf import settings

from acces_control.models import RFIDCard, LatestScan, AccessLog

# Zmienna globalna na ostatni odczytany UID (używana w tym samym procesie):
LATEST_CARD_UID = None

LOCK_PIN = 21  # pin do sterowania zamkiem/przekaźnikiem
RST_PIN = 25   # pin RST czytnika RC522

def run_rfid_loop():
    """
    Pętla odczytu kart RC522 w trybie polling (bez IRQ).
    Zapamiętuje ostatni UID, zapisuje go w LatestScan(pk=1),
    tworzy log w AccessLog (karta rozpoznana lub nieznana),
    i otwiera zamek w razie rozpoznania karty.
    """

    global LATEST_CARD_UID

    # Ustawienia GPIO
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LOCK_PIN, GPIO.OUT, initial=GPIO.LOW)

    # Inicjalizacja czytnika (bez pin_irq)
    rdr = RFID(pin_mode=GPIO.BCM, pin_rst=RST_PIN, pin_irq=None)

    print("[RFID] Start pętli polling... (Ctrl+C aby przerwać)")

    try:
        while True:
            # Odpytuj czytnik co ~0.2 s (polling)
            (error, tag_type) = rdr.request()
            if not error:
                (error, uid) = rdr.anticoll()
                if not error:
                    uid_str = "".join("{:02X}".format(x) for x in uid)
                    print(f"[RFID] Wykryto kartę: {uid_str}")

                    # 1. Zapis w LatestScan(pk=1)
                    LatestScan.objects.update_or_create(pk=1, defaults={"uid": uid_str})
                    LATEST_CARD_UID = uid_str

                    try:
                        # 2. Sprawdź, czy taka karta istnieje w RFIDCard
                        card = RFIDCard.objects.get(uid=uid_str)
                        message = f"Karta {uid_str} znaleziona w bazie, otwarto zamek"
                        print("[RFID]", message)

                        # 3. Zapis do AccessLog (karta rozpoznana)
                        AccessLog.objects.create(card=card, message=message)

                        # 4. Otwieramy zamek na 3 sekundy
                        open_lock(3)

                    except RFIDCard.DoesNotExist:
                        # Karta nie jest w bazie
                        message = f"Karta {uid_str} nieznana, odmowa dostępu."
                        print("[RFID]", message)

                        # Zapis do AccessLog (karta nieznana)
                        AccessLog.objects.create(card=None, message=message)

            time.sleep(0.2)

    except KeyboardInterrupt:
        print("[RFID] Przerwano pętlę klawiaturą.")
    finally:
        GPIO.cleanup()

def open_lock(duration=3):
    """
    Przykładowa funkcja otwierania zamka:
    - podaje HIGH na LOCK_PIN na określoną liczbę sekund
    - potem znowu LOW
    """
    GPIO.output(LOCK_PIN, GPIO.HIGH)
    time.sleep(duration)
    GPIO.output(LOCK_PIN, GPIO.LOW)
