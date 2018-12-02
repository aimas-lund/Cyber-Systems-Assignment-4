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

#Remove these from the string
removelist = ['Referer', ' ', 'http://192.168.4.1/', '\r\n', ':']

while True:
    keylist = []
    req = ['']

    cl, addr = s.accept()
    print('client connected from', addr)
    cl_file = cl.makefile('rwb', 0)

    json = '{"pins": {"12": "%d","13": "%d","33": "%d"},"sensor": {"temperature": "%d"}}'
    json = json % (pin12.value(), pin13.value(),
                   pin33.value(), temp_c(i2c.readfrom_mem(address, temp_reg, 2)))
    jsonObject = ujson.loads(json)

    while True:
        line = cl_file.readline()
        req = line.decode('ascii')

        if 'Referer' in req:
            for entry in removelist:
                req = req.replace(entry, '')

            keylist = req.split('/')
        else:
            pass

        if not line or line == b'\r\n':
            break

    #Determine output
    if len(keylist) == 0:
        outputStr = json
    else:
        outputStr = "jsonObject"
        for entry in keylist:
            addKey = '[%s]' % repr(entry)
            outputStr = outputStr + addKey

    try:
        output = eval("ujson.dumps(" + str(eval(outputStr)) + ")")

    except KeyError:
        output = "No Result"

    print("This is the output: %s" % output)
    response = html % output #Some bug, where it does not show the output correctly in the browser
    cl.send(response)
    cl.close()