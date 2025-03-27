#v1/shutter_control/gpio_shutter.py
import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

IN1, IN2, IN3, IN4 = 5, 6, 13, 19
PINS = [IN1, IN2, IN3, IN4]

for pin in PINS:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

FULL_STEP_SEQ = [
    [1, 0, 0, 0],
    [1, 1, 0, 0],
    [0, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 0],
    [0, 0, 1, 1],
    [0, 0, 0, 1],
    [1, 0, 0, 1],
]

running = False
shutter_state = "unknown"  # "up", "down", "moving", "stopped", "unknown"

def step_forward(delay=0.002, steps=512):
    """
    Ruch rolety w górę.
    """
    global running, shutter_state
    running = True
    shutter_state = "moving"

    # Flaga informująca, czy pętla zakończyła się normalnie
    completed = True

    for _ in range(steps):
        # Jeśli user kliknął "stop", to running=False => przerwij
        if not running:
            completed = False
            break

        for pattern in FULL_STEP_SEQ:
            if not running:
                completed = False
                break

            for pin, val in zip(PINS, pattern):
                GPIO.output(pin, val)
            time.sleep(delay)

        if not running:
            completed = False
            break

    stop_motor()

    # Jeśli nie przerwano ruchu, uznajemy, że roleta jest na górze
    if completed:
        shutter_state = "up"


def step_backward(delay=0.002, steps=512):
    """
    Ruch rolety w dół.
    """
    global running, shutter_state
    running = True
    shutter_state = "moving"

    completed = True

    for _ in range(steps):
        if not running:
            completed = False
            break

        for pattern in reversed(FULL_STEP_SEQ):
            if not running:
                completed = False
                break

            for pin, val in zip(PINS, pattern):
                GPIO.output(pin, val)
            time.sleep(delay)

        if not running:
            completed = False
            break

    stop_motor()

    if completed:
        shutter_state = "down"


def stop_motor():
    """
    Zatrzymanie silnika natychmiast.
    """
    global running, shutter_state
    running = False
    for pin in PINS:
        GPIO.output(pin, GPIO.LOW)

    # Jeżeli w momencie wywołania stopu stan był "moving",
    # to uznajemy, że jest "stopped". Jeśli pętla zakończyła się 
    # naturalnie (completed = True), stan zostanie ustawiony na "up"/"down".
    if shutter_state == "moving":
        shutter_state = "stopped"


def get_shutter_state():
    return shutter_state
