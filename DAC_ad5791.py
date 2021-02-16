################################
## GUI Module is controlling DAC ad5791
## in bipolar output [-10..+10]V  
################################

import tkinter as tk
import spidev


class AD5791:
    def __init__(self, port, cs, mode, speed):
        self.ad5791_spi = spidev.SpiDev(port, cs)
        self.ad5791_spi.mode = mode
        self.ad5791_spi.max_speed_hz = speed

    def config(self):
        ctrl_reg = (WRITE_REG
                          | CTRL_REG_ADDR
                          | LIN_COMP[0] << LIN_COMP_REG
                          | 1 << SDODIS_BIT
                          | 1 << BIN_2sC_BIT          ##DAC reg coding selection. 1 - offset binary coding
                          | 0 << DACTRI_BIT
                          | 0 << OPGND_BIT
                          | 1 << RBUF_BIT)             ##unity-gain amp
        dac_data_bytes = ctrl_reg.to_bytes(3, "big")
        self.ad5791_spi.writebytes(dac_data_bytes)
        
    def set(self, vout):
        #vout =  entry.get()
        dac_code = int((float(vout) - VREFN) * MAX_CODE / (VREFP - VREFN))
        print("int dac_code: %d" %(dac_code))
        dac_code = dac_code.to_bytes(3, "big")
        print("dac_code[0]: %x" %(dac_code[0]))
        print("dac_code[1]: %x" %(dac_code[1]))
        print("dac_code[2]: %x" %(dac_code[2]))
        dac_reg = (WRITE_REG | DAC_REG_ADDR
                   | dac_code[0] << 16
                   | dac_code[1] << 8
                   | dac_code[2])
        dac_data_bytes = dac_reg.to_bytes(3, "big")
        self.ad5791_spi.writebytes(dac_data_bytes)
        print(dac_data_bytes)

    def read(self):
        ctrl_reg = READ_REG | CTRL_REG_ADDR
        ctrl_reg_bytes = ctrl_reg.to_bytes(3, "big")
        read_val = self.ad5791_spi.xfer(ctrl_reg_bytes)
        print(read_val)
        return read_val

    def reset(self):
        swctrl_reg = (WRITE_REG | SWCTRL_REG_ADDR
        | 1 << LDAC_BIT
        | 0 << CLR_BIT
        | 1 << RESET_BIT)
        dac_data_bytes = swctrl_reg.to_bytes(3, "big")
        self.ad5791_spi.writebytes(dac_data_bytes)

def close():
    win.destroy()

#_______________DEFINES_________________
VREFP = 10.0
VREFN = -10.0
MAX_CODE = 2**20 - 1

WRITE_REG = 0x00 << 23
READ_REG = 0x01 << 23

#DAC register (p.21)
DAC_REG_ADDR = 0b00000001 << 20
DAC_REG_DATA = 12

#Control register (p.22)
CTRL_REG_ADDR = 0b00000010 << 20
RBUF_BIT = 1
OPGND_BIT = 2
DACTRI_BIT = 3
BIN_2sC_BIT = 4
SDODIS_BIT = 5
LIN_COMP = [0b00000000, 0b00001001, 0b00001010, 0b0001100]
LIN_COMP_REG = 6

#Software control register (p.23)
SWCTRL_REG_ADDR = 0b00000100 << 20
LDAC_BIT = 0
CLR_BIT = 1
RESET_BIT = 2

#Clear code register (p.22)
CLR_REGISTER_ADDR = 0b00000011 << 20

#_____________DEFINES END________________    
if __name__ == "__main__":
    win = tk.Tk()
    win.title("DAC ad5791")
    entry = tk.Entry(width = 20, justify = "center")
    
    DAC = AD5791(0, 0, 1, 2000000)
    
    button_set = tk.Button(win, text = "Set", command = DAC.set)
    button_set.bind("<Button-1>")
    
    button_reset = tk.Button(win, text = "Reset", command = DAC.reset)
    button_reset.bind("<Button-1>")
    
    button_config = tk.Button(win, text = "Config", command = DAC.config)
    button_config.bind("<Button-1>")
    
    button_read = tk.Button(win, text = "Read",  command = DAC.read)
    button_read.bind("<Button-1>")
    
    button_exit = tk.Button(win, text = "Exit", command = close)
    button_exit.bind("<Button-1>")

    entry.pack()
    button_set.pack() 
    button_reset.pack()
    button_config.pack()
    button_read.pack()
    button_exit.pack()

    win.mainloop()

