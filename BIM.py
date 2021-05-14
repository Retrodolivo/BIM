import tkinter as tk
import matplotlib.pyplot as plt
import math


import ADC_ads1256
import DAC_ad5791
import DAC_ad5543
import RPi.GPIO as GPIO

win = tk.Tk()
win.geometry("350x600")
win.resizable(False, False)
win.title("BIM GUI")

ADC = ADC_ads1256.ADS1256()
ADC.ADS1256_init() ##spi port 0 cs 0 mode 1
DAC = DAC_ad5791.AD5791(port = 0, cs = 1, mode = 1, speed = 1000000)
Divider = DAC_ad5543.AD5543(port = 1, cs = 2, mode = 0, speed = 1000000)

#_________global flags__________________
adc_stop = True
graph_run = False
#_______________________________________
Rb = 0
Ppod = {"initial": 0, "delta": 0}
adc_val_list = [ ]
Nfilter = 0
Meas = {"current": 0, "Total": 0}

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
        sum_val += ADC.ADS1256_GetChannalValue(0)* 5.0 / 0x7fffff
    average_val = sum_val / max_counts
    if graph_run:
        adc_val_list.append(average_val)
    return average_val

def dac_set():
    DAC.set(dac_entry.get())

def divider_set(event):
    Divider.set(0)

def graph_plot():
##    global graph_run
##    graph_run = True

    fig = plt.figure()
    
    plt.title("ADC_graph")
    plt.xlabel("N")
    plt.ylabel("Voltage, V")
    
    plt.plot(list(range(len(adc_val_list))), adc_val_list, color='pink')
    plt.show()

def pbp_set():
    Rb = float(Rb_entry.get())
    Ppod['initial'] = float(Ppod_entry.get())
    Um = math.sqrt(Ppod["initial"] / Rb / 1000) * (Rb + 1400)
    print("Ppod = %f" %Ppod['initial'])
    print("Rb = %f" %Rb)
    print("Um = %f" %Um)
    Um_label["text"] = str("%.4f" %Um + " V")

def Um_Ppod_calc():
     pass   

def close():
    GPIO.cleanup()
    win.destroy()
#_____________DEFINES END________________ 

#--------------DAC-----------------------------------#
dac_ad5791_lframe = tk.LabelFrame(win, text = "DAC, V", font = "Arial 12 bold", width=200, height=100)
dac_ad5791_lframe.grid(row = 0, column = 1, pady = 10, padx = 10)

dac_entry = tk.Entry(dac_ad5791_lframe, width = 10, font = "Arial 12 bold", justify = "center")
dac_entry.grid(in_ = dac_ad5791_lframe, pady = 10, padx = 10)

dac_button = tk.Button(dac_ad5791_lframe, text = "Set Um", font = "Arial 11", width = 7, command = dac_set)
dac_button.grid(in_ = dac_ad5791_lframe)
dac_button = tk.Button(dac_ad5791_lframe, text = "Reset", font = "Arial 11", width = 7, command = dac_set)
dac_button.grid(in_ = dac_ad5791_lframe) 

#--------------Bridge output"-------------------#
adc_ads1256_lframe = tk.LabelFrame(win, text = "Bridge output", font = "Arial 12 bold", width=200, height=100)
adc_ads1256_lframe.grid(row = 0, column = 0, pady = 10, padx = 10)

adc_label = tk.Label(adc_ads1256_lframe, text = "_.______V", height = 2, font = "Arial 20 bold", bg = "white")
adc_label.grid(in_ = adc_ads1256_lframe, pady = 10, padx = 10)

adc_btn_start = tk.Button(text = "Start", font = "Arial 11", width = 7, command = adc_read_start)
adc_btn_start.bind("<Button-1>")
adc_btn_start.grid(in_ = adc_ads1256_lframe)
adc_btn_stop = tk.Button(text = "Stop", font = "Arial 11", width = 7, command = adc_read_stop)
adc_btn_stop.bind("<Button-1>")
adc_btn_stop.grid(in_ = adc_ads1256_lframe)

graph_btn = tk.Button(text = "Graph", font = "Arial 11 bold", command = graph_plot)
graph_btn.bind("<Button-1>")
graph_btn.grid(in_ = adc_ads1256_lframe)

#--------------Bridge resistance-------------------#
divider_lframe = tk.LabelFrame(win, text = "Bridge resistance", font = "Arial 12 bold", width=200, height=100)
divider_lframe.grid(row = 1, column = 1, pady = 10, padx = 10)

KD_MIN = 0
KD_MAX = 1

Kd = tk.DoubleVar()
divider_slide = tk.Scale(divider_lframe, font = "Arial 12 bold", orient = tk.HORIZONTAL, \
                     from_ = KD_MIN, to_ = KD_MAX, resolution = 0.1, variable = Kd, command = divider_set)
divider_slide.grid(in_ = divider_lframe, pady = 10, padx = 10)

#--------------PBP Parameters-------------------#
PBP_lframe = tk.LabelFrame(win, text = "PBP Parameters", font = "Arial 12 bold", width=200, height=100)
PBP_lframe.grid(row = 1, column = 0, pady = 10, padx = 10)

Rb_lframe = tk.LabelFrame(PBP_lframe, text = "Rb, Ohm", font = "Arial 12 bold", width=200, height=100)
Rb_lframe.grid(row = 0, column = 0, pady = 10, padx = 10)
Rb_entry = tk.Entry(Rb_lframe, width = 10, font = "Arial 12 bold", justify = "center")
Rb_entry.grid(in_ = Rb_lframe, pady = 10, padx = 10)

Ppod_lframe = tk.LabelFrame(PBP_lframe, text = "Ppod, mW", font = "Arial 12 bold", width=200, height=100)
Ppod_lframe.grid(row = 1, column = 0, pady = 10, padx = 10)
Ppod_entry = tk.Entry(Ppod_lframe, width = 10, font = "Arial 12 bold", justify = "center")
Ppod_entry.grid(in_ = Ppod_lframe, pady = 10, padx = 10)

set_button = tk.Button(PBP_lframe, text = "Set Um", font = "Arial 11", width = 7, command = pbp_set)
set_button.grid(in_ = PBP_lframe, pady = 10, padx = 10) 

#--------------Calculated Um-------------------#
Um_lframe = tk.LabelFrame(win, text = "Calculated Um", font = "Arial 12 bold", width=200, height=100)
Um_lframe.grid(row = 2, column = 0, pady = 10, padx = 10)
Um_label = tk.Label(Um_lframe, text = "__._____V", height = 1, font = "Arial 18 bold", bg = "white")
Um_label.grid(in_ = Um_lframe, pady = 10, padx = 10)

#--------------Choose Mode---------------------#
balance = tk.BooleanVar()
balance.set(0)

mode_1 = tk.Radiobutton(win, text = 'Autobalance', font = "Arial 11 bold", variable = balance, value = 0)
mode_2 = tk.Radiobutton(win, text = 'Setting Rb', font = "Arial 11 bold", variable = balance, value = 1)
mode_1.place(relx = 0.55, rely = 0.40)
mode_2.place(relx = 0.55, rely = 0.45)

#--------------Filter------------------------------------#
Nfilter_label = tk.Label(win, text = "Nfilter", height = 1, font = "Arial 12 bold")
Nfilter_label.place(relx = 0.55, rely = 0.75)
Nfilter_entry = tk.Entry(win, width = 3, font = "Arial 12 bold", justify = "center")
Nfilter_entry.place(relx = 0.70, rely = 0.75)

Meas_label = tk.Label(win, text = "iZ", height = 1, font = "Arial 12 bold")
Meas_label.place(relx = 0.55, rely = 0.80)
Meas_entry = tk.Entry(win, width = 3, font = "Arial 12 bold", justify = "center")
Meas_entry.place(relx = 0.70, rely = 0.80)



exit_btn = tk.Button(text = "Exit", font = "Arial 11", width = 7, command = close )
exit_btn.bind("<Button-1>")
exit_btn.grid(row = 2, column = 1)

win.mainloop()
