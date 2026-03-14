import time
import board
import busio
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont
import psutil
import socket
import subprocess
import RPi.GPIO as GPIO

# GPIO setup
LED_PIN = 4
BUTTON_PIN = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# OLED setup
i2c = busio.I2C(board.SCL, board.SDA)
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)

def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except:
        return "No network"

def is_openclaw_running():
    try:
        output = subprocess.check_output(["pgrep", "-f", "openclaw"])
        return len(output) > 0
    except:
        return False

def update_display():
    oled.fill(0)
    image = Image.new("1", (128, 64))
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    ip = get_ip()
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory().percent
    openclaw = "RUNNING" if is_openclaw_running() else "STOPPED"

    draw.text((0, 0),  f"IP: {ip}",          font=font, fill=255)
    draw.text((0, 16), f"CPU: {cpu}%",        font=font, fill=255)
    draw.text((0, 32), f"RAM: {ram}%",        font=font, fill=255)
    draw.text((0, 48), f"OC: {openclaw}",     font=font, fill=255)

    oled.image(image)
    oled.show()

def button_callback(channel):
    print("Shutdown button pressed")
    GPIO.output(LED_PIN, GPIO.LOW)
    subprocess.call(["sudo", "shutdown", "-h", "now"])

GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING,
                      callback=button_callback, bouncetime=2000)

# Turn LED on — system is running
GPIO.output(LED_PIN, GPIO.HIGH)

try:
    while True:
        update_display()
        time.sleep(5)
except KeyboardInterrupt:
    GPIO.cleanup()
    oled.fill(0)
    oled.show()
