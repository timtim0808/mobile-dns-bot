import paho.mqtt.client as mqtt
import requests

MQTT_BROKER = "broker.emqx.io"
MQTT_TOPIC = "dnscheck/skt"

WARNING_KEYWORDS = [
    "불법", "유해", "경고", "접속할 수 없습니다", "서비스 이용이 제한", "위반", "차단",
    "위해 정보", "유해 정보", "유해사이트", "청소년 유해", "불법 사이트"
]
REDIRECT_KEYWORDS = ["warning.or.kr", "harmful.or.kr", "w.nprotect.net", "safevisit"]

def is_blocked(content, final_url):
    for keyword in WARNING_KEYWORDS:
        if keyword in content:
            return f"차단(https warning keyword)"
    for redirect in REDIRECT_KEYWORDS:
        if redirect in final_url:
            return f"차단(https warning redirect)"
    return None

def check_single(domain):
    for protocol in ["https", "http"]:
        try:
            url = f"{protocol}://{domain}"
            res = requests.get(url, timeout=10, allow_redirects=True)
            content = res.text[:3000]
            redirect_url = res.url

            blocked = is_blocked(content, redirect_url)
            if blocked:
                return blocked.replace("https", protocol)
            return "정상" if protocol == "https" else "정상(http)"
        except:
            continue
    return "응답없음"

def on_connect(client, userdata, flags, rc):
    print("📡 MQTT 연결됨 (SKT)")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    domain = msg.payload.decode().strip().replace("https://", "").replace("http://", "")
    if "." not in domain or " " in domain:
        print(f"⛔ 무시됨 (도메인 아님): {domain}")
        return
    result = check_single(domain)
    print(f"✅ 모바일버전 결과: {domain}\n- SKT: {result}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER, 1883, 60)
client.loop_forever()
