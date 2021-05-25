import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from functools import partial
import math
import time

import RPi.GPIO as GPIO
import ADC_ads1256
import DAC_ad5791
import DAC_ad5543


win = tk.Tk()
win.geometry("350x600")
#win.resizable(False, False)
win.title("BIM GUI")

ADC = ADC_ads1256.ADS1256()
ADC.ADS1256_init() #spi port 0 cs 0 mode 1
DAC = DAC_ad5791.AD5791(port = 3, cs = 0, mode = 1, speed = 1000000)
Divider = DAC_ad5543.AD5543(port = 1, cs = 0, mode = 0, speed = 1000000)

#_________global flags__________________
adc_stop = True
graph_run = False
#_______________________________________
Kop = 24 / 6.34 + 1
PBP = {
            "Rb": 950,
            "Ppod": {"initial": 60, "delta": 0},
            "Rs": 1400,
            "K1": 45,
            "K2": 150,
            "Um": 0,
            "Pizm": 0
           }

adc_val_list = [ ]
Nfilter = 5
Meas = {"current": 0, "total": 5}
v = 0
offset = 0.1533

#_______________DEFINES_________________
def init():
    Rb_entry.insert(0, str(PBP["Rb"]))
    Ppod_entry.insert(0, str(PBP["Ppod"]['initial']))
    Nfilter_entry.insert(0, str(Nfilter))
    Meas_entry.insert(0, str(Meas['total']))
    dac_entry.insert(0, '0')
    vout = dac_entry.get()
    
def adc_read_start():
    global adc_stop
    global graph_run
    if adc_stop:
        adc_label["text"] = str("%.5f" %(Um_buf_calc() ) + " V")
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

def dac_set(vout):
    DAC.set(vout)

def dac_reset():
    dac_entry.delete(0, 'end')
    dac_entry.insert(0, '0')
    DAC.set(0)
    
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

def pbp_set():
    PBP["Rb"] = float(Rb_entry.get())
    PBP["Ppod"]["initial"] = float(Ppod_entry.get())
    PBP['Um'] = math.sqrt(PBP["Ppod"]["initial"] / PBP["Rb"] / 1000) * (PBP["Rb"] + PBP["Rs"])
    print("Ppod = %f" %PBP["Ppod"]["initial"])
    print("Rb = %f" %PBP["Rb"])
    print("Um = %f" %PBP['Um'])
    Um_label["text"] = str("%.4f" %PBP['Um'] + " V")
    dac_set(PBP['Um'] / Kop)
    dac_entry.delete(0, 'end')
    formatter = "{0:.4f}" 
    dac_entry.insert(0, str(formatter.format(PBP['Um'] / Kop)))
    
def Um_Ppod_calc():
    Ud = [ ]
    while(Meas['current'] < Meas['total']):
        Ud.append(Um_buf_calc())
        dV = PBP['K1'] * Ud[Meas['current']]
        Meas['current'] += 1
    else:
        Udk = (np.polyfit(list(range(Meas['total'])), Ud, 1)[0] +
                   np.polyfit(list(range(Meas['total'])), Ud, 1)[1] * len(Ud))
        dV = PBP['K1'] * Udk + PBP['K2'] * np.polyfit(list(range(Meas['total'])), Ud, 1)[1]
        Ud = []
        Meas['current'] = 0

        a = 1 / (PBP['Rb'] / (PBP['Rb'] + PBP['Rs']) + Udk / PBP['Um'])
        ri = PBP['Rs'] / (a - 1)
        r = abs(dV)
        if r > 0.5:
            dV = 0.5 * dV / r
        PBP['Um'] = PBP['Um'] - dV
        u = PBP['Um'] - dV * 1.5
        dac_set(u)
        PBP['Pizm'] = 1000 * PBP['Um']**2 * ri / (ri + PBP['Rb']) / (ri + PBP['Rb'])
        print('Um:%.5f\nP:%.5f\n' %(PBP['Um'], PBP['Pizm']))
        
        return PBP['Pizm']

def Um_buf_calc():
    return -((adc_average_val() - 2.5) * 2 + offset)

def Ppod_get():
    while balance.get():
        Um_Ppod_calc()
        #time.sleep(0.5)
        
def close():
    GPIO.cleanup()
    win.destroy()
#_____________DEFINES END________________ 

#--------------DAC-----------------------------------#
dac_ad5791_lframe = tk.LabelFrame(win, text = "DAC, V", font = "Arial 12 bold", width=200, height=100)
dac_ad5791_lframe.grid(row = 0, column = 1, pady = 10, padx = 10)

dac_entry = tk.Entry(dac_ad5791_lframe, width = 10, font = "Arial 12 bold", justify = "center")
dac_entry.grid(in_ = dac_ad5791_lframe, pady = 10, padx = 10)

dac_button = tk.Button(dac_ad5791_lframe, text = "Set Um", font = "Arial 11", width = 7, command = partial(dac_set, dac_entry.get()))
dac_button.grid(in_ = dac_ad5791_lframe)
dac_button = tk.Button(dac_ad5791_lframe, text = "Reset", font = "Arial 11", width = 7, command = dac_reset)
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

KD = {'min': 0, 'max': 1}

Kd = tk.DoubleVar()
divider_slide = tk.Scale(divider_lframe, font = "Arial 12 bold", orient = tk.HORIZONTAL, \
                     from_ = KD['min'], to_ = KD['max'], resolution = 0.001, variable = Kd, command = divider_set)
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

mode_auto = tk.Radiobutton(win, text = 'Autobalance', font = "Arial 11 bold", variable = balance, value = 1, command = Ppod_get)
mode_nauto = tk.Radiobutton(win, text = 'Setting Rb', font = "Arial 11 bold", variable = balance, value = 0)
mode_auto.place(relx = 0.55, rely = 0.40)
mode_nauto.place(relx = 0.55, rely = 0.45)

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

init()
win.mainloop()
