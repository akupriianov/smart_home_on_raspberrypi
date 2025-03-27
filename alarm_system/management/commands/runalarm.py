# v1/alarm_system/management/commands/runalarm.py

from django.core.management.base import BaseCommand
import time
from alarm_system.alarm_gpio import (
    setup_gpio, check_arming_status, check_sensors,
    activate_alarm, deactivate_alarm
)
from alarm_system.models import AlarmSettings

class Command(BaseCommand):
    help = "Pętla alarmu, wyłączana tylko z systemu (nie po powrocie czujników)"

    def handle(self, *args, **options):
        self.stdout.write("[ALARM] Inicjalizacja GPIO...")
        setup_gpio()
        self.stdout.write("[ALARM] Start pętli alarmowej (Ctrl+C, aby przerwać)")

        alarm_active = False  # Czy alarm (syrena + dioda) jest obecnie włączony

        try:
            while True:
                # 1) Sprawdź, czy minęło opóźnienie (arming delay)
                check_arming_status()

                # 2) Pobierz aktualne ustawienia
                settings = AlarmSettings.objects.get(pk=1)

                # 3) Jeśli system jest uzbrojony, sprawdź czujniki
                if settings.is_armed:
                    triggered = check_sensors()  # True, jeśli czujniki sygnalizują stan alarmowy
                    if triggered and not alarm_active:
                        # Uruchamiamy alarm tylko wtedy, gdy jeszcze nie był aktywny
                        activate_alarm()
                        alarm_active = True
                else:
                    # System jest rozbrojony (lub w trakcie uzbrajania, ale is_armed=False) 
                    # -> jeśli alarm był aktywny, wyłącz go
                    if alarm_active:
                        deactivate_alarm()
                        alarm_active = False

                time.sleep(1)
        except KeyboardInterrupt:
            self.stdout.write("[ALARM] Przerwano pętlę ręcznie (Ctrl+C).")
        finally:
            deactivate_alarm()
            import RPi.GPIO as GPIO
            GPIO.cleanup()
