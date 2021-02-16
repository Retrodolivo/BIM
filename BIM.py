import tkinter as tk
import ADC_ad4020
import DAC_ad5791
import RPi.GPIO as GPIO

win = tk.Tk()
win.title("BIM GUI")


ADC = ADC_ad4020.AD4020(1, 0, 0, 2000000)
DAC = DAC_ad5791.AD5791(0, 0, 1, 2000000)
#_________global flags__________________
adc_stop = True
#_______________________________________


#_______________DEFINES_________________
def adc_read_start():
    global adc_stop
    if adc_stop:
        adc_label["text"] = str("%.6f" %adc_average_val() + " V")
        adc_btn_stop["state"] = "normal"
        adc_btn_start["state"] = "disabled"
        win.after(100, adc_read_start)
    else:
        adc_stop = True
        return
        
def adc_read_stop():
    global adc_stop
    adc_stop = False
    adc_btn_start["state"] = "normal"
    adc_btn_stop["state"] = "disabled"

def adc_average_val():
    max_counts = 500
    sum_val = 0
    i = 0
    
    for i in range(max_counts):
        sum_val += ADC.read()
        i += 1
    average_val = sum_val / max_counts
    return average_val

def dac_set():
    DAC.set(dac_entry.get())

def close():
    GPIO.cleanup()
    win.destroy()
#_____________DEFINES END________________ 

#--------------DAC_AD5791-------------------#
dac_ad5791_lframe = tk.LabelFrame(win, text = "DAC ad5791", font = "Arial 12 bold", width=200, height=100)
dac_ad5791_lframe.grid(row = 0, column = 0, pady = 10, padx = 10)

dac_entry = tk.Entry(dac_ad5791_lframe, width = 10, font = "Arial 12 bold", justify = "center")
dac_entry.grid(in_ = dac_ad5791_lframe, pady = 10, padx = 10)

dac_button = tk.Button(dac_ad5791_lframe, text = "Set Um", font = "Arial 11", width = 7, command = dac_set)
dac_button.grid(in_ = dac_ad5791_lframe, pady = 10, padx = 10) 

#--------------ADC_AD4020-------------------#
dac_ad4020_lframe = tk.LabelFrame(win, text = "ADC ad4020", font = "Arial 12 bold", width=200, height=100)
dac_ad4020_lframe.grid(row = 0, column = 1, pady = 10, padx = 10)

adc_label = tk.Label(dac_ad4020_lframe, text = "_.______V", height = 2, font = "Arial 20 bold", bg = "pink")
adc_label.grid(in_ = dac_ad4020_lframe, pady = 10, padx = 10)

adc_btn_start = tk.Button(text = "Start", font = "Arial 11", width = 7, command = adc_read_start)
adc_btn_start.bind("<Button-1>")
adc_btn_start.grid(in_ = dac_ad4020_lframe)
adc_btn_stop = tk.Button(text = "Stop", font = "Arial 11", width = 7, command = adc_read_stop)
adc_btn_stop.bind("<Button-1>")
adc_btn_stop.grid(in_ = dac_ad4020_lframe)

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


win.geometry("350x370")
win.mainloop()
