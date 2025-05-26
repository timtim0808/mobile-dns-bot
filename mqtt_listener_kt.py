import paho.mqtt.client as mqtt
import requests
import time

MQTT_BROKER = "broker.emqx.io"
MQTT_TOPIC = "dnscheck/kt"

def check_domain(domain):
    try:
        print(f"[🔍] 검사 중: {domain}")
        res = requests.get(f"http://210.126.12.123:5000/check?domain={domain}", timeout=20)
        data = res.json()
        result = data.get("result", {})
        print(f"✅ 모바일(KT) 결과: {domain}")
        print(f"- KT: {result.get('KT', '응답없음')}")
    except Exception as e:
        print(f"❌ 검사 실패: {e}")

def on_connect(client, userdata, flags, rc):
    print("✅ MQTT 연결됨")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    domain = msg.payload.decode().strip()
    if "." not in domain:
        print(f"⛔ 무시됨 (도메인 아님): {domain}")
        return
    check_domain(domain)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER, 1883, 60)
client.loop_forever()
