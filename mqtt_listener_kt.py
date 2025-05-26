import paho.mqtt.client as mqtt
import requests

MQTT_BROKER = "broker.emqx.io"
MQTT_TOPIC = "dnscheck/kt"
POST_URL = "https://brodbot-gyunle025.replit.app/mobile-report"
MY_ISP = "KT"

def on_connect(client, userdata, flags, rc):
    print(f"[{MY_ISP}] MQTT 연결됨")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    domain = msg.payload.decode().strip()
    print(f"[{MY_ISP}] 검사 요청 도메인: {domain}")

    try:
        res = requests.get(f"http://210.126.12.123:5000/check?domain={domain}", timeout=20)
        result = res.json().get("result", {}).get(MY_ISP, "응답없음")
        requests.post(POST_URL, json={
            "domain": domain,
            "isp": MY_ISP,
            "result": result
        })
        print(f"[{MY_ISP}] 결과 전송됨: {result}")

    except Exception as e:
        print(f"[{MY_ISP}] 오류: {e}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER, 1883, 60)
client.loop_forever()
