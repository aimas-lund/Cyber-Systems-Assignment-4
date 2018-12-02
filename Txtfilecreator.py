import machine, time, os


#Setting up pins
clock = machine.Pin(22)
dat = machine.Pin(23)
i2c = machine.I2C(scl=clock, sda=dat)
address = 24
temp_reg = 5
res_reg = 8  

def temp_c(input):
    value = (input[0] << 8) | input[1] #pass in the bitearray of data, to convert the bitearray into
    temp = ((value & 0xFFF) / 16.0) #Lower 12-bits of data, if the value ends with oxFFF (the signed bit value) and divide it by 16.0 you get a floating point value.
    if value & 0x1000:  #And now we want to check that 13-bit set, if its a non zero value
        temp -= 256.0   #So we can get a proper negative value
    return temp

####Creating the text file####)
while True:
    counter = int(input("Number of measurements you wish to read?"))
    timer = int(input("How many seconds between each measuments?"))
    f = open("Temp_Measurements.txt","w")
    while counter>0:
        TEMPERATURE = temp_c(i2c.readfrom_mem(address, temp_reg, 2))
        f.write("%d," % TEMPERATURE)
        counter -= 1
        time.sleep(timer)
    f.close()
    break
