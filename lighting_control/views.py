from django.shortcuts import render, redirect
from . import gpio_setup
from django.contrib.auth.decorators import login_required

@login_required
def control_light(request):
    """
    Widok obsługujący włączanie/wyłączanie światła.

    Funkcjonalności:
        - Obsługuje żądania POST do włączania i wyłączania światła.
        - Odczytuje aktualny stan światła i przekazuje go do szablonu.
    """
    if request.method == 'POST':
        # Pobranie akcji z żądania POST
        action = request.POST.get('action')
        
        # Włączenie światła
        if action == 'on':
            gpio_setup.turn_light_on()
        
        # Wyłączenie światła
        elif action == 'off':
            gpio_setup.turn_light_off()
        
        # Przekierowanie na tę samą stronę po przetworzeniu akcji
        return redirect('control-light')

    # Odczytanie aktualnego stanu światła z GPIO (np. czy jest włączone)
    light_is_on = gpio_setup.get_light_state()
    
    # Kontekst dla szablonu, przekazanie informacji o stanie światła
    context = {
        'light_is_on': light_is_on,
    }
    
    # Renderowanie szablonu z panelem kontrolnym
    return render(request, 'lighting_control/control_panel.html', context)

