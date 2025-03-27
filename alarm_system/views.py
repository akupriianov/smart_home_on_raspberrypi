#v1/alarm_system/views.py
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.generic import ListView
from .models import AlarmEvent, AlarmSettings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

class AlarmEventListView(LoginRequiredMixin, ListView):
    """
    Widok listy zdarzeń alarmowych.

    Atrybuty:
        model: Model zdarzeń alarmowych (`AlarmEvent`).
        template_name (str): Ścieżka do szablonu HTML używanego do renderowania listy zdarzeń.
        context_object_name (str): Nazwa kontekstu, pod którą lista zdarzeń będzie dostępna w szablonie.
        ordering (list): Kolejność sortowania zdarzeń (od najnowszych do najstarszych).
        paginate_by (int): Liczba elementów na stronę (jeśli paginacja jest włączona).
    """
    model = AlarmEvent
    template_name = 'alarm_system/event_list.html'
    context_object_name = 'events'
    ordering = ['-timestamp']
    paginate_by = 20  # Liczba zdarzeń na stronę


ARMING_DELAY_SECONDS = 20  # Liczba sekund opóźnienia uzbrojenia alarmu

@login_required
def toggle_alarm_view(request):
    """
    Widok obsługujący przełączanie stanu systemu alarmowego.

    Funkcjonalności:
        - Uzbrajanie alarmu natychmiastowe lub z opóźnieniem.
        - Rozbrajanie alarmu.
        - Aktualizacja ustawień czujników PIR i kontaktronów.

    Kontekst dla szablonu:
        - is_armed (bool): Czy alarm jest uzbrojony.
        - is_arming (bool): Czy trwa proces uzbrajania.
        - arming_start_time (datetime): Czas rozpoczęcia uzbrajania.
        - pir_enabled (bool): Czy czujnik ruchu PIR jest aktywny.
        - door_enabled (bool): Czy czujnik drzwi jest aktywny.
        - seconds_left (int): Liczba sekund pozostałych do uzbrojenia (dla opóźnienia).
        - ARMING_DELAY_SECONDS (int): Stała określająca czas opóźnienia.
    """
    settings, _ = AlarmSettings.objects.get_or_create(pk=1)  # Pobranie lub utworzenie obiektu ustawień alarmu
    now = timezone.now()  # Bieżący czas

    if request.method == 'POST':
        action = request.POST.get('action')  # Pobranie akcji z formularza

        # Obsługa natychmiastowego uzbrojenia
        if action in [
            'arm_pir_only_immediate',
            'arm_door_only_immediate',
            'arm_both_immediate'
        ]:
            settings.is_armed = True
            settings.is_arming = False
            settings.arming_start_time = None  # Wyzerowanie czasu uzbrajania

            # Ustawienie aktywnych czujników
            if action == 'arm_pir_only_immediate':
                settings.pir_enabled = True
                settings.door_enabled = False
            elif action == 'arm_door_only_immediate':
                settings.pir_enabled = False
                settings.door_enabled = True
            elif action == 'arm_both_immediate':
                settings.pir_enabled = True
                settings.door_enabled = True

            settings.save()  # Zapisanie zmian

        # Obsługa uzbrojenia z opóźnieniem
        elif action in [
            'arm_pir_only_delay',
            'arm_door_only_delay',
            'arm_both_delay'
        ]:
            settings.is_armed = False
            settings.is_arming = True
            settings.arming_start_time = now  # Ustawienie czasu rozpoczęcia uzbrajania

            # Ustawienie aktywnych czujników
            if action == 'arm_pir_only_delay':
                settings.pir_enabled = True
                settings.door_enabled = False
            elif action == 'arm_door_only_delay':
                settings.pir_enabled = False
                settings.door_enabled = True
            elif action == 'arm_both_delay':
                settings.pir_enabled = True
                settings.door_enabled = True

            settings.save()  # Zapisanie zmian

        # Obsługa rozbrojenia
        elif action == 'disarm':
            settings.is_armed = False
            settings.is_arming = False
            settings.arming_start_time = None  # Wyzerowanie czasu uzbrajania
            settings.save()  # Zapisanie zmian

        # Przekierowanie po obsłużeniu akcji
        return redirect('alarm-toggle')

    # Obliczanie pozostałego czasu do uzbrojenia (dla opóźnienia)
    seconds_left = 0
    if settings.is_arming and settings.arming_start_time:
        delta = now - settings.arming_start_time
        left = ARMING_DELAY_SECONDS - delta.total_seconds()
        if left < 0:  # Jeśli opóźnienie minęło, ustaw na 0
            left = 0
        seconds_left = int(left)

    # Przygotowanie kontekstu do renderowania szablonu
    context = {
        'is_armed': settings.is_armed,
        'is_arming': settings.is_arming,
        'arming_start_time': settings.arming_start_time,
        'pir_enabled': settings.pir_enabled,
        'door_enabled': settings.door_enabled,
        'seconds_left': seconds_left,
        'ARMING_DELAY_SECONDS': ARMING_DELAY_SECONDS
    }
    return render(request, 'alarm_system/toggle_alarm.html', context)