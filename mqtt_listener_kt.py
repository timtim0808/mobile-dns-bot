import os
import paho.mqtt.client as mqtt
import time
import datetime
import subprocess

MQTT_BROKER = "broker.emqx.io"
MQTT_TOPIC = "dnscheck/kt"

def on_connect(client, userdata, flags, rc):
    print("Connected with result code", rc)
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    try:
        domain = msg.payload.decode().strip()
        print(f"[RECEIVED] Domain to open: {domain}")

        os.system(f"termux-open-url http://{domain}")
        time.sleep(5)

        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"/sdcard/kt_{domain}_{now}.png"
        subprocess.run(["termux-screenshot", "-f", filename])
        print(f"[✅] Screenshot saved: {filename}")

    except Exception as e:
        print(f"[❌ ERROR] {e}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER, 1883, 60)
client.loop_forever()
