#v1/lighting_control/gpio_setup.py
import RPi.GPIO as GPIO

GPIO.setwarnings(False)
# Wybór trybu numeracji pinów (BCM)
GPIO.setmode(GPIO.BCM)

# Lista pinów, które będziemy obsługiwać
# (możesz dodać więcej, np. do sterowania wieloma przekaźnikami)
RELAY_GPIO_PIN = 17

# Inicjalizacja pinów jako wyjścia
GPIO.setup(RELAY_GPIO_PIN, GPIO.OUT, initial=GPIO.LOW)

def turn_light_on():
    """
    Ustawia GPIO na stan wysoki (włączenie światła).
    """
    GPIO.output(RELAY_GPIO_PIN, GPIO.HIGH)

def turn_light_off():
    """
    Ustawia GPIO na stan niski (wyłączenie światła).
    """
    GPIO.output(RELAY_GPIO_PIN, GPIO.LOW)

def get_light_state() -> bool:
    """
    Sprawdza aktualny stan pinu (True = HIGH, False = LOW).
    """
    return GPIO.input(RELAY_GPIO_PIN) == GPIO.HIGH
