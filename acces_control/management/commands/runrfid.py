# v1/acces_control/management/commands/runrfid.py

from django.core.management.base import BaseCommand
from acces_control.rfid_reader import run_rfid_loop

class Command(BaseCommand):
    help = "Uruchamia pętlę odczytu RFID w trybie polling (bez IRQ)."

    def handle(self, *args, **options):
        self.stdout.write("[runrfid] Uruchamiam pętlę RFID (polling)...")
        run_rfid_loop()
        self.stdout.write("[runrfid] Pętla RFID zakończona.")
