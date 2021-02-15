import tkinter as tk
import ADC_ad4020
import RPi.GPIO as GPIO

win = tk.Tk()
win.title("BIM GUI")

ADC = ADC_ad4020.AD4020(1, 0, 0, 2000000)

#_______________DEFINES_________________
def close():
    GPIO.cleanup()
    win.destroy()

def adc_read():
    adc_label["text"] = str(ADC.read())

def dac_set():
    pass

#_____________DEFINES END________________ 

#--------------DAC_AD5791-------------------#
dac_ad5791_lframe = tk.LabelFrame(win, text = "DAC ad5791", font = "Arial 12 bold", width=200, height=100)
dac_ad5791_lframe.grid(row = 0, column = 0, pady = 10, padx = 10)

dac_entry = tk.Entry(dac_ad5791_lframe, width = 10, font = "Arial 12 bold", justify = "center")
dac_entry.grid(in_ = dac_ad5791_lframe, pady = 10, padx = 10)

dac_button = tk.Button(dac_ad5791_lframe, text = "Set Um", font = "Arial 11", width = 7)
dac_button.grid(in_ = dac_ad5791_lframe, pady = 10, padx = 10) 

#--------------ADC_AD4020-------------------#
dac_ad4020_lframe = tk.LabelFrame(win, text = "ADC ad4020", font = "Arial 12 bold", width=200, height=100)
dac_ad4020_lframe.grid(row = 0, column = 1, pady = 10, padx = 10)

adc_label = tk.Label(dac_ad4020_lframe, text = "_.______ V", height = 2, font = "Arial 20 bold", bg = "pink")
adc_label.grid(in_ = dac_ad4020_lframe, pady = 10, padx = 10)

adc_btn = tk.Button(text = "Start", font = "Arial 11", width = 7, command = adc_read)
adc_btn.bind("<Button-1>")
adc_btn.grid(in_ = dac_ad4020_lframe, pady = 10, padx = 10)

#--------------DAC_AD5543-------------------#
dac_ad5543_lframe = tk.LabelFrame(win, text = "DAC_AD5543", font = "Arial 12 bold", width=200, height=100)
dac_ad5543_lframe.grid(row = 1, column = 0, pady = 10, padx = 10)

MIN_CODE = 0
MAX_CODE = 2**16 - 1

dac_slide = tk.Scale(dac_ad5543_lframe, font = "Arial 12 bold", orient = tk.HORIZONTAL, from_ = MIN_CODE, to_ = MAX_CODE)
dac_slide.grid(in_ = dac_ad5543_lframe, pady = 10, padx = 10)

#-------------------------------------------#


graph_btn = tk.Button(win, text = "Graph", font = "Arial 12 bold")
graph_btn.bind("<Button-1>")
graph_btn.grid(row = 1, column = 1)

exit_btn = tk.Button(text = "Exit", font = "Arial 11", width = 7, command = close )
exit_btn.bind("<Button-1>")
exit_btn.grid(row = 2, column = 1)


win.geometry("350x330")
win.mainloop()
