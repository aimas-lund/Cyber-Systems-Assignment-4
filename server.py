import machine
import network
import socket
import neopixel

clock = machine.Pin(22)
dat = machine.Pin(23)
i2c = machine.I2C(scl=clock, sda=dat)
np = neopixel.NeoPixel(machine.Pin(12), 8, bpp=3)
address = 24
temp_reg = 5
res_reg = 8  #work on temperature update tradeoff (time | precision)

def temp_c(input):
    value = (input[0] << 8) | input[1] #pass in the bitearray of data, to convert the bitearray into
    temp = ((value & 0xFFF) / 16.0) #Lower 12-bits of data, if the value ends with oxFFF (the signed bit value) and divide it by 16.0 you get a floating point value.
    if value & 0x1000:  #And now we want to check that 13-bit set, if its a non zero value
        temp -= 256.0   #So we can get a proper negative value
    return temp

TEMPERATURE = temp_c(i2c.readfrom_mem(address, temp_reg, 2))

if temp_c(TEMPERATURE) <= 27:
    np[0] = (255, 0, 0)
    np[1] = (0, 0, 0)
    np[2] = (0, 0, 0)
elif (temp_c(TEMPERATURE) > 15) and (temp_c(TEMPERATURE) <= 28):
    np[0] = (0, 0, 0)
    np[1] = (100, 70, 0)
    np[2] = (0, 0, 0)
else:
    np[0] = (0, 0, 0)
    np[1] = (0, 0, 0)
    np[2] = (0, 255, 0)

np.write()

print(TEMPERATURE)
#####################
ap = network.WLAN (network.AP_IF)
ap.active (True) #Activation of the station interface
ap.config (essid = 'SUPER_COOL_WIFI')
ap.config (authmode = 3, password = 'SECRET_PASSWORD')

pins = [(machine.Pin(i,machine.Pin.IN).value(),n) for (i,n) in [(13,"LED"),(12,"LED"),(33,"Button")]]
TempReader = [(TEMPERATURE,"Temperature")]
AllRead = pins + TempReader
print(pins)
html = """<!DOCTYPE html>
<html>
    <head> <title>Hvorfor er Aimas dum</title> </head>
    <body> <h1>Hvorfor er Aimas dum</h1>
        <table border="1"> <tr><th>Pin</th><th>Value</th></tr> %s </table>
    </body>
</html>
"""

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket() #Creates a new socket 
s.bind(addr) #Bind the socket to address
s.listen(1) #Enable a server to accept connections

print('listening on', addr)

while True:
    cl, addr = s.accept()  #Accept a connection, socket must be bound to an address and listening for connections. The return value is a a pair
    # (conn, address) where conn is a new socket object usable to send and receive data on the connection, and address is the address bound to the socket.
    print('client connected from', addr)
    cl_file = cl.makefile('rwb', 0) #return a file object associated with the socket.
    while True:
        line = cl_file.readline()
        print(line)
        if not line or line == b'\r\n':
            break
    rows = ['<tr><td>%s</td><td>%d</td></tr>' % (n,p) for (p,n) in AllRead]
    print(rows,"rows")
    response = html % '\n'.join(rows) 
    cl.send(response)
    cl.close()

# We first import all the useful modules in order to create our Internet-of-Things node
# The 4 ap. lines of code, permit us to activate our station interface for our private WLAN. By configurating a password and a name SSID
# We assign each 
#
#
#
#
#