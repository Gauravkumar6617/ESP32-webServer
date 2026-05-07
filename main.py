import network
import socket
from machine import Pin

# LED setup (GPIO2 is onboard LED on most ESP32 boards)
led = Pin(2, Pin.OUT)

# Wi-Fi connect
wifi = network.WLAN(network.STA_IF)
wifi.active(True)

wifi.connect("WIFI_NAME", "your_password")

print("Connecting to WiFi...")

while not wifi.isconnected():
    pass

print("Connected!")
print(wifi.ifconfig())

ip = wifi.ifconfig()[0]

# Socket server
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
server = socket.socket()
server.bind(addr)
server.listen(5)

print("Server running at:")
print("http://{}".format(ip))


# HTML UI (with inline CSS)
def web_page():
    led_state = "ON" if led.value() else "OFF"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ESP32 Control Panel</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <style>
            body {{
                font-family: Arial;
                text-align: center;
                background: #0f172a;
                color: white;
                margin-top: 50px;
            }}

            h1 {{
                color: #38bdf8;
            }}

            .btn {{
                padding: 15px 30px;
                font-size: 20px;
                margin: 10px;
                border: none;
                border-radius: 10px;
                cursor: pointer;
            }}

            .on {{
                background: #22c55e;
                color: white;
            }}

            .off {{
                background: #ef4444;
                color: white;
            }}

            .card {{
                background: #1e293b;
                padding: 20px;
                border-radius: 15px;
                display: inline-block;
            }}
        </style>
    </head>

    <body>

        <div class="card">
            <h1>ESP32 Web Control</h1>
            <p>LED Status: <b>{led_state}</b></p>

            <a href="/on"><button class="btn on">TURN ON</button></a>
            <a href="/off"><button class="btn off">TURN OFF</button></a>
        </div>

    </body>
    </html>
    """
    return html


# Server loop
while True:
    client, addr = server.accept()
    print("Client:", addr)

    request = client.recv(1024).decode()

    print(request)

    if "/on" in request:
        led.value(1)

    if "/off" in request:
        led.value(0)

    response = web_page()

    client.send("HTTP/1.1 200 OK\n")
    client.send("Content-Type: text/html\n")
    client.send("Connection: close\n\n")
    client.send(response)

    client.close()