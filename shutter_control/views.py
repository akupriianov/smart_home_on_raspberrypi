#v1/shutter_control/views.py
from django.shortcuts import render, redirect
from . import gpio_shutter
from django.contrib.auth.decorators import login_required

@login_required
def shutter_control_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'up':
            gpio_shutter.step_forward()
        elif action == 'down':
            gpio_shutter.step_backward()
        elif action == 'stop':
            gpio_shutter.stop_motor()
        return redirect('shutter-control')

    shutter_state = gpio_shutter.get_shutter_state()
    context = {
        'shutter_state': shutter_state,
    }
    return render(request, 'shutter_control/panel.html', context)
