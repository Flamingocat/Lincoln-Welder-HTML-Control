import network
import socket
from machine import Pin, PWM
import time
import ure

# Setup Access Point
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid='Tylar H Welder', password='TylarLincoln1967')

print('Access Point started')
print('Network configuration:', ap.ifconfig())

# Initialize the servo on GPIO 15
servo_pin = PWM(Pin(15))
servo_pin.freq(50)  # 50 Hz is standard for servos

# Initialize relays on GPIO 16 and GPIO 17
relay_pin_16 = Pin(16, Pin.OUT)
relay_pin_17 = Pin(17, Pin.OUT)

# Set Servo Angle
def set_servo_angle(angle):
    # Adjust pulse width mapping here
    # Map 0 to 114 degrees to a suitable pulse width (1ms to 1.5ms)
    pulse_width = (0.5 + angle * 1 / 180) / 20  # Adjust this line if necessary
    duty = int(pulse_width * 65535)
    servo_pin.duty_u16(duty)
    print(f"Servo moving to {angle} degrees")

# Function to toggle relay state
def toggle_relay(relay_pin):
    relay_pin.value(not relay_pin.value())  # Toggle the relay state

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

# Load the HTML content from the filesystem
html_content = load_html()

# Create a socket and listen for connections
addr = socket.getaddrinfo('0.0.0.0', 180)[0][-1]
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
            toggle_relay(relay_pin_16)
        elif 'GET /toggle_relay_17' in request:
            toggle_relay(relay_pin_17)

        serve_page(client, html_content)
        client.close()
    except OSError as e:
        print('Connection closed', e)
