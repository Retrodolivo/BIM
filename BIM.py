import tkinter as tk
import matplotlib.pyplot as plt


import ADC_ad4020
import DAC_ad5791
import DAC_ad5543
import RPi.GPIO as GPIO

win = tk.Tk()
win.title("BIM GUI")


ADC = ADC_ad4020.AD4020(port = 1, cs = 0, mode = 0, speed = 2000000)
DAC = DAC_ad5791.AD5791(port = 0, cs = 0, mode = 1, speed = 2000000)
Divider = DAC_ad5543.AD5543(port = 1, cs = 2, mode = 0, speed = 1000000)

#_________global flags__________________
adc_stop = True
graph_run = False
#_______________________________________
adc_val_list = [ ]

#_______________DEFINES_________________
def adc_read_start():
    global adc_stop
    global graph_run
    if adc_stop:
        adc_label["text"] = str("%.6f" %adc_average_val() + " V")
        adc_btn_stop["state"] = "normal"
        adc_btn_start["state"] = "disabled"
        win.after(100, adc_read_start)
        graph_run = True
    else:
        adc_stop = True
        graph_run = False
        return
        
def adc_read_stop():
    global adc_stop
    adc_stop = False
    adc_btn_start["state"] = "normal"
    adc_btn_stop["state"] = "disabled"        

def adc_average_val():
    max_counts = 1
    sum_val = 0
    global adc_val_list
    global graph_run
    
    for count in range(max_counts):
        sum_val += ADC.read()
    average_val = sum_val / max_counts
    if graph_run:
        adc_val_list.append(average_val)
    return average_val

def dac_set():
    DAC.set(dac_entry.get())

def divider_set(event):
    Divider.set(Kd.get())

def graph_plot():
##    global graph_run
##    graph_run = True

    fig = plt.figure()
    
    plt.title("ADC_graph")
    plt.xlabel("N")
    plt.ylabel("Voltage, V")
    
    plt.plot(list(range(len(adc_val_list))), adc_val_list, color='pink')
    plt.show()

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
adc_ad4020_lframe = tk.LabelFrame(win, text = "ADC ad4020", font = "Arial 12 bold", width=200, height=100)
adc_ad4020_lframe.grid(row = 0, column = 1, pady = 10, padx = 10)

adc_label = tk.Label(adc_ad4020_lframe, text = "_.______V", height = 2, font = "Arial 20 bold", bg = "pink")
adc_label.grid(in_ = adc_ad4020_lframe, pady = 10, padx = 10)

adc_btn_start = tk.Button(text = "Start", font = "Arial 11", width = 7, command = adc_read_start)
adc_btn_start.bind("<Button-1>")
adc_btn_start.grid(in_ = adc_ad4020_lframe)
adc_btn_stop = tk.Button(text = "Stop", font = "Arial 11", width = 7, command = adc_read_stop)
adc_btn_stop.bind("<Button-1>")
adc_btn_stop.grid(in_ = adc_ad4020_lframe)

graph_btn = tk.Button(text = "Graph", font = "Arial 12 bold", command = graph_plot)
graph_btn.bind("<Button-1>")
graph_btn.grid(in_ = adc_ad4020_lframe)

#--------------DAC_AD5543-------------------#
divider_lframe = tk.LabelFrame(win, text = "Divider", font = "Arial 12 bold", width=200, height=100)
divider_lframe.grid(row = 1, column = 0, pady = 10, padx = 10)

KD_MIN = 0
KD_MAX = 1

Kd = tk.DoubleVar()
divider_slide = tk.Scale(divider_lframe, font = "Arial 12 bold", orient = tk.HORIZONTAL, \
                     from_ = KD_MIN, to_ = KD_MAX, resolution = 0.1, variable = Kd, command = divider_set)
divider_slide.grid(in_ = divider_lframe, pady = 10, padx = 10)

#-------------------------------------------#

exit_btn = tk.Button(text = "Exit", font = "Arial 11", width = 7, command = close )
exit_btn.bind("<Button-1>")
exit_btn.grid(row = 1, column = 1)

win.geometry("350x370")
win.mainloop()
