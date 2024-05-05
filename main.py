import network
import socket
from machine import Pin, PWM
import time
import ure

def disconnect_and_disable_wifi():
    wlan = network.WLAN(network.STA_IF)
    ap = network.WLAN(network.AP_IF)
    if wlan.active() or ap.active():
        wlan.active(False)
        ap.active(False)
        print("Wi-Fi interfaces have been disabled.")

def reset_wifi():
    # This function simulates a "reset" by reinitializing the interfaces.
    wlan = network.WLAN(network.STA_IF)
    ap = network.WLAN(network.AP_IF)
    wlan.active(False)
    ap.active(False)
    print("Wi-Fi settings are reset.")


def setup_access_point():
    ap = network.WLAN(network.AP_IF)
    ap.active(True)  # Activate the AP interface
    ap.config(essid='Tylar H Welder', password='SA200TylarH')

    # Check current configuration
    print("Access Point Active:", ap.active())
    print("Network Name (SSID):", ap.config('essid'))
    print("IP Address:", ap.ifconfig()[0])

# Activate and configure the access point
setup_access_point()
# Main execution flow
disconnect_and_disable_wifi()  # First, disable any active interfaces
reset_wifi()                   # Reset configurations
# Activate and configure the access point
setup_access_point()

# Initialize the servo on GPIO 15
servo_pin = PWM(Pin(20))
servo_pin.freq(50)  # Standard frequency for servos

# Initialize relays and LEDs
relay_pin_16 = Pin(18, Pin.OUT)
relay_pin_17 = Pin(19, Pin.OUT)
led_system_enable = Pin(16, Pin.OUT, value=1)  # System Enable LED, always on
led_starter = Pin(17, Pin.OUT, value=0)        # Starter LED
led_choke = Pin(14, Pin.OUT, value=0)          # Choke LED
led_ignition = Pin(15, Pin.OUT, value=0)       # Ignition LED

# Set Servo Angle
def set_servo_angle(angle):
    pulse_width = (0.5 + angle * 1 / 180) / 20
    duty = int(pulse_width * 65535)
    servo_pin.duty_u16(duty)
    led_choke.value(1)  # Turn on Choke LED when adjusting the servo
    print(f"Servo moving to {angle} degrees")
    time.sleep(1)  # Keep the LED on for 1 second
    led_choke.value(0)  # Turn off Choke LED after 1 second

# Function to toggle relay and control corresponding LED
def toggle_relay(relay_pin, led_pin):
    relay_pin.value(not relay_pin.value())
    led_pin.value(relay_pin.value())  # Update LED state to match relay
    print(f"Relay {'ON' if relay_pin.value() else 'OFF'}")

# Function to serve the HTML page
def serve_page(client, content):
    client.send('HTTP/1.1 200 OK\n')
    client.send('Content-Type: text/html\n')
    client.send('Connection: close\n\n')
    client.sendall(content)

# Function to load HTML file
def load_html():
    with open('index.html', 'r') as file:
        html = file.read()
    return html

html_content = load_html()

# Create a socket and listen for connections
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)
print('Listening on', addr)

# Regular expression to extract angle from request
angle_regex = ure.compile("GET /\?angle=(\d+)")

while True:
    try:
        client, addr = s.accept()
        print('Client connected from', addr)
        request = client.recv(1024).decode()

        # Extract angle from request
        match = angle_regex.search(request)
        if match:
            angle = int(match.group(1))
            set_servo_angle(angle)

        # Process relay control requests
        if 'GET /toggle_relay_16' in request:
            toggle_relay(relay_pin_16, led_starter)
        elif 'GET /toggle_relay_17' in request:
            toggle_relay(relay_pin_17, led_ignition)

        serve_page(client, html_content)
        client.close()
    except OSError as e:
        print('Connection closed', e)

