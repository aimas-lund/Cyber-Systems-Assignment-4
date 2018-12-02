import machine, network, socket, ujson

ap = network.WLAN (network.AP_IF)
ap.active (True)
ap.config (essid = 'CHAMPION-DU-MONDE')
ap.config (authmode = 3, password = 'france1820')

pins = [machine.Pin(i, machine.Pin.IN) for i in (0, 2, 4, 5, 12, 13, 14, 15)]

html = """<!DOCTYPE html>
<html>
    <head> <title>ESP32 Pins</title> </head>
    <body>
        %s
    </body>
</html>
"""

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

s = socket.socket()
s.bind(addr)
s.listen(1)

print('listening on', addr)

removelist = ['Referer', ' ', 'http://192.168.4.1/', '\r\n', ':']

while True:
    keylist = []
    req = ['']

    cl, addr = s.accept()
    print('client connected from', addr)
    cl_file = cl.makefile('rwb', 0)

    while True:
        line = cl_file.readline()
        req = line.decode('ascii')

        if 'Referer' in req:
            print(repr(req))
            for entry in removelist:
                req = req.replace(entry, '')
            keylist = req.split('/')

        if not line or line == b'\r\n':
            break

    print(keylist)
    x = """{\n   "pins": {\n      
    "1": "machine.Pin(1, machine.Pin.IN)",\n      
    "2": "machine.Pin(2, machine.Pin.IN)",\n      
    "3": "machine.Pin(3, machine.Pin.IN)",\n      
    "4": "machine.Pin(4, machine.Pin.IN)"\n   },\n   
    "sensor": {\n      
    "temperature": "temp_c(i2c.readfrom_mem(address, temp_reg, 2))"\n   }\n}"""
    x = x.replace("\n", "\r\n")
    response = html % x
    cl.send(response)
    cl.close()