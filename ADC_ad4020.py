################################
## GUI Module is controlling ADC ad4020
## in bipolar [-10..+10]V single to 
## differencial conversions
################################

import tkinter as tk
import spidev
import RPi.GPIO as GPIO

class AD4020:
    def __init__(self, port, mode, cs, speed):
        self.ad4020_spi = spidev.SpiDev(port, cs)
        self.ad4020_spi.mode = mode
        self.ad4020_spi.max_speed_hz = speed

    def config(self):
        config_reg = (  0 << TURBO_EN
                      | 0 << HIGHZ_EN
                      | 0 << SPAN_COMPR_EN
                      | 0 << STATUS_EN)
        reg_val = [READ_REG, config_reg]
        self.ad4020_spi.writebytes(reg_val)

    def read(self):
        raw_code = 0

        #Make a pulse on CNV pin to start conversion
        GPIO.output(PIN_CNV, GPIO.HIGH)
        GPIO.output(PIN_CNV, GPIO.LOW)

        raw_code = raw_code.to_bytes(3, "big")
        raw_code = self.ad4020_spi.xfer(raw_code)
        #fit raw data to 20 bit value
        code = ( raw_code[0] << 12 |
                 raw_code[1] << 4  |
                 raw_code[2] >> 4)

        LOWEST_POS_CODE = 0x00001       #1           ->   0V
        HIGHEST_POS_CODE = 0x7FFFF      #524 287     ->   -10V
        LOWEST_NEG_CODE = 0x80000       #524 288     ->   10V
        HIGHEST_NEG_CODE = 0xFFFFF      #1 048 575   ->   0V
       
        if code >= LOWEST_POS_CODE and code <= HIGHEST_POS_CODE:
            voltage_val = float(code) / MAX_CODE * VREF
            if PRINTENABLE:
                print("voltage_in: %.3f" %(-(voltage_val)))# - OFFSET_ERR)))
            else:
                return voltage_val# - OFFSET_ERR
        

        if code >= LOWEST_NEG_CODE and code <= HIGHEST_NEG_CODE:
            voltage_val = (HIGHEST_NEG_CODE -  float(code)) / MAX_CODE * VREF
            if PRINTENABLE:
                print("voltage_in: %.3f" %(voltage_val))# + OFFSET_ERR))
            else:
                return voltage_val# + OFFSET_ERR

        if PRINTENABLE:  
            print(raw_code)
            print(code)


###TOGGLE PRINT TO SHELL###
PRINTENABLE = 1
########################
VREF = 10
MAX_CODE = 2**19 - 1
OFFSET_ERR = 2.5571 - 2.4399

#Register access command  (p.27)
WRITE_REG = 0b00010100
READ_REG  = 0b01010100

#Control register bits (p.26)
TURBO_EN      = 1
HIGHZ_EN      = 2
SPAN_COMPR_EN = 3
STATUS_EN     = 4

PIN_CNV = 23

#GPIO numbering, not a pin numbering
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_CNV, GPIO.OUT, GPIO.PUD_OFF, GPIO.LOW)

def close():
    GPIO.cleanup()
    win.destroy()

#_____________DEFINES END________________ 
if __name__ == "__main__":
    win = tk.Tk()
    entry = tk.Entry(win, width = 20)

    ADC = AD4020(1, 0, 0, 2000000)   

    button_config = tk.Button(win, text = "Config", command = ADC.config)
    button_config.bind("<Button-1>")

    button_read = tk.Button(win, text = "Read", command = ADC.read)
    button_read.bind("<Button-1>")

    button_exit = tk.Button(win, text = "Exit", command = close)
    button_exit.bind("<Button-1>")

    button_config.pack()
    button_read.pack()
    button_exit.pack()

    win.geometry("100x100")
    win.mainloop()



