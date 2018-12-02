import machine, neopixel, network, socket, ujson

def switchLEDState(pinNo):
    boundPin = machine.Pin(pinNo, machine.Pin.IN)

    if boundPin == 0:
        boundPin.value(1)
    else:
        boundPin.value(0)

def changeNeoColor(pinNo, index, color):
    np = neopixel.NeoPixel(machine.Pin(pinNo), 8, bpp=3) #Pin 12
    colors = {
        "red": (0,255,0),
        "green": (255,0,0),
        "blue": (0,0,255),
        "purple": (0,128,128),
        "yellow": (200,60,0),
        "white": (255,255,255),
        "off": (0,0,0)
    }
    np[index] = colors[color]

def readPin(pinNo):
    boundPin = machine.Pin(pinNo, machine.Pin.OUT)
    value = boundPin.value()

    return(value)

#Setting up pins
clock = machine.Pin(22)
dat = machine.Pin(23)
i2c = machine.I2C(scl=clock, sda=dat)
pin12 = machine.Pin(12, machine.Pin.IN)
pin13 = machine.Pin(13, machine.Pin.IN)
pin33 = machine.Pin(33, machine.Pin.IN)

address = 24
temp_reg = 5
res_reg = 8  #work on temperature update tradeoff (time | precision)

def temp_c(input):
    value = (input[0] << 8) | input[1] #pass in the bitearray of data, to convert the bitearray into
    temp = ((value & 0xFFF) / 16.0) #Lower 12-bits of data, if the value ends with oxFFF (the signed bit value) and divide it by 16.0 you get a floating point value.
    if value & 0x1000:  #And now we want to check that 13-bit set, if its a non zero value
        temp -= 256.0   #So we can get a proper negative value
    return temp

ap = network.WLAN (network.AP_IF)
ap.active (True)
ap.config (essid = 'CHAMPION-DU-MONDE')
ap.config (authmode = 3, password = 'france1820')

pins = [machine.Pin(i, machine.Pin.IN) for i in (0, 2, 4, 5, 12, 13, 14, 15)]

html = """<!DOCTYPE html>
<html>
    <head> <title>ESP32 Pins</title> </head>
    <body> <h1>ESP32 Pins</h1>
        <table border="1"> <tr><th>Pin</th><th>Value</th></tr> %s </table>
    </body>
</html>
"""

commands = {
    "exit": "break",
    "changeled": "switchLEDState(pinNo)",
    "changecol": "changeNeoColor(pinNo, index, color)",
    "readpin": "readPin(pinNo)",
    "readtemp": "temp_c(i2c.readfrom_mem(address, temp_reg, 2))"
}

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

s = socket.socket()
s.bind(addr)
s.listen(1)

print('listening on', addr)

while True:
    cl, addr = s.accept()
    print('client connected from', addr)
    #cl_file = cl.makefile('rwb', 0)

    while True:
        command = cl.recv(1024)
        command = command.decode('ascii')
        print(command)
        command = command.split(" ")
        print(command)
        if command[0] in commands:
            key = "commands"
            for word in command:
                key += "[%s]" % word

            print(key)
            try:
                eval(key)
            except KeyError:
                msg = b'"Invalid key" + "\r\n"
                cl.send(msg)
            except TypeError:
                msg = b'"Invalid amount of arguments" + "\r\n"
                cl.send(msg)
        else:
            continue

    print("Disconnecting...")
    cl.close()