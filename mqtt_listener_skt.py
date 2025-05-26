import paho.mqtt.client as mqtt
import requests
import time
import http.client

MQTT_BROKER = "broker.emqx.io"
MQTT_TOPIC = "dnscheck/skt"
REPORT_URL = "https://brodbot-gyunle025.replit.app/mobile-report"

def check_domain(domain):
    try:
        def classify(protocol):
            try:
                conn = http.client.HTTPSConnection(domain, timeout=10) if protocol == "https" else http.client.HTTPConnection(domain, timeout=10)
                conn.request("GET", "/")
                res = conn.getresponse()
                html = res.read().decode(errors="ignore")
                location = res.getheader("Location", "")

                if any(w in html for w in ["불법", "유해", "경고", "watch", "harmful"]) or "warning" in location:
                    return f"차단({protocol} warning redirect)"
                return f"정상({protocol})"
            except Exception:
                return "응답없음"

        https_result = classify("https")
        if "정상" in https_result:
            final = https_result
        elif "차단" in https_result:
            final = https_result
        else:
            final = classify("http")

        print(f"[SKT ✅] {domain} = {final}")
        requests.post(REPORT_URL, json={"domain": domain, "isp": "SKT", "status": final})

    except Exception as e:
        print("[❌] 검사 오류", e)

def on_connect(client, userdata, flags, rc):
    print("📶 MQTT 연결됨 (SKT)")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    domain = msg.payload.decode().strip()
    if "." not in domain:
        return
    check_domain(domain)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER, 1883, 60)
client.loop_forever()
