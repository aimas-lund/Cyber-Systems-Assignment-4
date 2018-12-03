import machine, time


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
    time_val = 0
    while counter>0:
        TEMPERATURE = temp_c(i2c.readfrom_mem(address, temp_reg, 2))
        if counter==1:
            f.write("%d,%d" % (TEMPERATURE,time_val))
            time_val += timer
            counter -= 1
            time.sleep(timer)
        else:
            f.write("%d,%d" % (TEMPERATURE,time_val))
            time_val += timer
            counter -= 1
            time.sleep(timer)
    f.close()
    break

#The document will have - for each line of the text file - the measured temperature "TEMPERATURE" at the time "time_val", both values seperated by commas. 
#This will form a text file will have two columns by importing this csv document to excel, and by applying the "Text to colums" implemented Excel function
#It will give another two columnds which can be plotted. First column as the temperature value and second as time corresponding to this temperature measured.