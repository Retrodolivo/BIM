################################
## GUI Module is controlling DAC ad5543  
################################

import tkinter as tk
import spidev


class AD5543:
    def __init__(self, port, cs, mode, speed):
        self.ad5543_spi = spidev.SpiDev(port, cs)
        self.ad5543_spi.mode = mode
        self.ad5543_spi.max_speed_hz = speed

        initial_value = 0
        self.set(initial_value)
        
    def set(self, vout):
        #vout = entry.get()
        dac_code = MAX_CODE * float(vout) / VREF
        print(int(dac_code))
        print(int(dac_code).to_bytes(2, "big"))
        dac_data_bytes = bytearray(int(dac_code).to_bytes(2, "big"))
        self.ad5543_spi.writebytes(dac_data_bytes)

#_______________DEFINES_________________
MAX_CODE = 2**16
if __name__ == "__main__":
    VREF = 10.0
else:
    VREF = 1.0
"""
def reverse_bits(byte):
    byte = ((byte & 0xF0) >> 4) | ((byte & 0x0F) << 4)
    byte = ((byte & 0xCC) >> 2) | ((byte & 0x33) << 2)
    byte = ((byte & 0xAA) >> 1) | ((byte & 0x55) << 1)
    return byte
"""
    
#_____________DEFINES END________________
if __name__ == "__main__":
    win = tk.Tk()
    win.title("DAC ad5543")
    entry = tk.Entry(win, width = 20, justify = "center")

    DAC = AD5543(port = 1, cs = 2, mode = 0, speed = 1000000)
    button = tk.Button(win, text = "Set", command = DAC.set)
    button.bind("<Button-1>")

    entry.pack()
    button.pack()

    win.mainloop()
