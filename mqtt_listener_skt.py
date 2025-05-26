# mqtt_listener_skt.py / mqtt_listener_sskt.py / mqtt_listener_lgu.py
# carrier 이름만 각각 skt, Sskt, LGU+ 로 바꿔서 저장하세요

import paho.mqtt.client as mqtt
import requests
import http.client

MQTT_BROKER = "broker.emqx.io"
MQTT_TOPIC = "dnscheck/skt"  # ✅ skt/Sskt/LGU+ 에 따라 "dnscheck/sskt", "dnscheck/lgu" 로 변경
CARRIER = "skt"  # ✅ 해당 파일에 맞게 "Sskt" 또는 "LGU+"로 변경
REPORT_URL = "https://brodbot-gyunle025.replit.app/mobile-report"

def classify(domain, protocol):
    try:
        conn = http.client.HTTPSConnection(domain, timeout=10) if protocol == "https" else http.client.HTTPConnection(domain, timeout=10)
        conn.request("GET", "/")
        res = conn.getresponse()
        html = res.read().decode(errors="ignore")
        location = res.getheader("Location", "")

        if any(w in html for w in ["불법", "유해", "경고", "harmful", "watch"]) or "warning" in location:
            return f"차단({protocol} warning redirect)"
        return f"정상({protocol})"
    except:
        return "응답없음"

def check_domain(domain):
    print(f"[{CARRIER}] 검사 시작: {domain}")
    https_result = classify(domain, "https")
    if "정상" in https_result:
        final = https_result
    elif "차단" in https_result:
        final = https_result
    else:
        final = classify(domain, "http")

    print(f"[{CARRIER}] 결과 전송됨: {final}")
    try:
        requests.post(REPORT_URL, json={
            "domain": domain,
            "isp": CARRIER,
            "result": final
        }, timeout=10)
    except Exception as e:
        print(f"[❌ {CARRIER}] 전송 실패: {e}")

def on_connect(client, userdata, flags, rc):
    print(f"✅ MQTT 연결됨: {CARRIER}")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    domain = msg.payload.decode().strip()
    if "." not in domain:
        print(f"[⛔ 무시됨] {domain}")
        return
    check_domain(domain)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER, 1883, 60)
client.loop_forever()
