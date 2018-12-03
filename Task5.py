import machine, neopixel, network, socket, ujson

def switchPINState(pinNo): #Switches the state of an LED output
    try:
        boundPin = machine.Pin(pinNo, machine.Pin.OUT)

        if boundPin.value() == 0:
            boundPin(1)
        else:
            boundPin(0)
    except ValueError:
        print("Invalid pin number." + "\r\n")

def changeNeoColor(pinNo, index, color):#Changes the color of one LED
    np = neopixel.NeoPixel(machine.Pin(pinNo), 8, bpp=3) #Pin 12
    colors = {
        "red": (0,255,0),
        "green": (255,0,0),
        "blue": (0,0,255),
        "purple": (0,70,200),
        "yellow": (200,60,0),
        "white": (255,255,255),
        "off": (0,0,0)
    }
    try:
        np[index] = colors[color]
        np.write()
    except KeyError:
        print("Invalid key" + "\r\n" )

def readButton(pinNo):
    try:
        boundPin = machine.Pin(pinNo, machine.Pin.IN, machine.Pin.PULL_UP)
        value = boundPin.value()
    except ValueError:
        print("Invalid pin number." + "\r\n")
    return(value)

def readPin(pinNo):
    try:
        boundPin = machine.Pin(pinNo, machine.Pin.OUT)
        value = boundPin.value()
    except ValueError:
        print("Invalid pin number." + "\r\n")
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
    "changepin": "switchPINState(%d)",
    "changecol": "changeNeoColor(%d,%d,%s)",
    "readpin": "readPin(%d)",
    "readbutton": "readButton(%d)",
    "readtemp": "temp_c(i2c.readfrom_mem(%d, %d, %d))"
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

    while True: #Determine the arguments in the command
        command = cl.recv(1024)
        command = command.decode('ascii').lower()
        print(command)
        arg = command.split(" ")
        print(arg)
        if arg[0] not in commands:
            msg = "Invalid command" + "\r\n"
            cl.send(msg)
            continue

        elif command == "exit":
            cl.close()
            break

        else:
            key = arg[0]
            val = commands[key]
            del arg[0]

            for i in range(len(arg)): #Convert numbers to integers (if possible)
                try:
                    arg[i] = int(arg[i])
                except TypeError:
                    pass
                except ValueError:
                    pass

            try: #Execute the command
                command = val % tuple(arg)
                print(command)
                if ("readpin" in command.lower()) or ("readbutton" in command.lower()):
                    msg = "Reading of pin: " + str(eval(command)) + "\r\n"
                    cl.send(msg)
                else:
                    eval(command)
                    msg = "Command executed" + "\r\n"
                    cl.send(msg)
            except TypeError:
                msg = "Invalid amount of arguments" + "\r\n"
                cl.send(msg)
                continue
            except NameError:
                msg = "Invalid amount of arguments" + "\r\n"
                cl.send(msg)
                continue

            msg = None

    print("Disconnecting...")
    cl.close()
