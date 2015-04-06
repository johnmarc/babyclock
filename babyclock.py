#!/usr/bin/python
from bibliopixel.led import *
from bibliopixel.animation import StripChannelTest
from bibliopixel.drivers.WS2801 import *
import time
import RPi.GPIO as io
io.setmode(io.BCM)
pir_pin = 18
io.setup(pir_pin, io.IN)
driver = DriverWS2801(24)
led = LEDStrip(driver)

class Lights:
    lights = {}
    pir_time = 0
    pir_on = False
    pir_start_time = 0

    
    base_brightness = 20
    max_brightness = 80
    brightness = 20
    fade_duration = 30

    time_on = 0
    time_off = 0
    off_time = 300
    start_time = 0
    led = None

    def __init__(self, led):
        self.led = led
        self.pir_time = time.time() - 30

    def zero_lights(self):
        for i in range(24):
            self.lights[i] = (255, 128, 0)

    def set_color(self, light, r, g, b):
        self.lights[light] = (r, g, b)

    def set_intensity(self):
        bright = self.brightness / 100.
        for i in range(24):
            self.lights[i] = ( int(self.lights[i][0] * bright), int(self.lights[i][1] * bright), int(self.lights[i][2] * bright))

    def start_bright(self):
        print "START BRIGHT"
        self.pir_time = time.time()
        self.pir_start_time = time.time()
        self.pir_on = True
        self.fade_brightness(self.pir_time, self.fade_duration, self.base_brightness, self.max_brightness)
    
    def start_dim(self):
        print "START DIM"
        self.pir_time = time.time()
        self.pir_on = False
        self.fade_brightness(self.pir_time, self.fade_duration, self.max_brightness, self.base_brightness)

    def set_time(self):
        localtime = time.localtime(time.time())
        hour = localtime.tm_hour % 12
        minute = round(localtime.tm_min / 60. * 12)
        self.set_color(hour,  0, 0, 0)
        self.set_color(hour + 12, 128, 128, 255)
        self.set_color(minute, 0, 0, 255)
        self.set_color(minute + 12, 0, 0, 255)

    def show_timer(self):
        if self.pir_on:
            time_in_sec = time.time() - self.pir_start_time
            max_light = int((time_in_sec / 3600. * 12) // 1)
            #print "time_in_sec: %s max_light: %s" % ( time_in_sec, max_light)
            if max_light < 0:
                return
            if max_light > 23:
                max_light = 23
            for x in range(max_light + 1):
                self.set_color(x, 255, 255, 0)
            

    def fade_brightness(self, start_time, duration, start_brightness, stop_brightness ):
        steps = abs(stop_brightness - start_brightness)
        increments = float(steps) / float(duration)
        ms_per_increase = (duration * 1000) / steps
        elapsed = int((time.time() - start_time) * 1000)
        steps_from_start = int(elapsed / ms_per_increase)
        if self.pir_on:
            self.brightness = start_brightness + steps_from_start
        else:
            self.brightness = start_brightness - steps_from_start
        
        if steps_from_start > steps:
            self.brightness = stop_brightness
        #print "steps: %s ms_per_increase: %s elapsed: %s step_from_start: %s brightness %s" % (steps, ms_per_increase, elapsed, steps_from_start, self.brightness)

    def tick(self):
        self.zero_lights()
        self.motion_detect()
        self.set_time()
        self.show_timer()
        self.set_intensity()
        self.update_lights()
        self.led.update()
        time.sleep(0.05)

    def motion_detect(self):
        if self.pir_on:
            #print "pir_on: True, fade_duration: %s, base_brightness: %s, max_brightness: %s, pir_time: %s" % (self.fade_duration, self.base_brightness, self.max_brightness, self.pir_time) 
            self.time_on = time.time() - self.pir_time
            self.fade_brightness(self.pir_time, self.fade_duration, self.base_brightness, self.max_brightness)
        else:
            self.time_off = time.time() - self.pir_time
            self.fade_brightness(self.pir_time, self.fade_duration, self.max_brightness, self.base_brightness)
            ##print "pir_on: False, fade_duration: %s, base_brightness: %s, max_brightness: %s, pir_time: %s" % (self.fade_duration, self.base_brightness, self.max_brightness, self.pir_time) 
#
        if self.time_on > self.fade_duration and self.pir_on:
            if io.input(pir_pin):
                #print "EXTEND TIME"
                self.pir_time = time.time() - self.fade_duration

        if round(self.time_on) > self.off_time and self.pir_on:
                self.time_off = 0
                self.start_dim()
        
        if not self.pir_on:
            if io.input(pir_pin):
                self.start_bright()

    def update_lights(self):
        for x in self.lights:
            #iprint x, lights[x]
            self.led.set(int(x), self.lights[x])



def set_intensity(r, g, b, intensity):
    red = int(round(r * (intensity / 100.)))
    green = int(round(g * (intensity / 100.)))
    blue = int(round(b * (intensity / 100.)))
    #print red, green, blue
    for i in range(24):
        lights[i] = (red, green, blue)

        


#def lights_to_bytes(lights):
#    light_bytes = bytearray(25 * 3)
#    for x in lights:
#        #print x, lights[x][0], lights[x][1], lights[x][2]
#        light_bytes[x*3] = gamma[lights[x][0]]
#        light_bytes[x*3 + 1] = gamma[lights[x][1]]
#        light_bytes[x*3 + 2] = gamma[lights[x][2]]
#    return light_bytes
#
#lights_to_bytes(lights)

def set_time():
    localtime = time.localtime(time.time())
    #sethour
    hour = localtime.tm_hour % 12
    lights[hour + 12] = (0, 0, 128)

    #setminute
    minute = int(5 * round(float(localtime.tm_min)/5) / 5)
    lights[minute] = (128, 0, 128)

    #setsecond
    light = int(5 * round(float(localtime.tm_sec)/5) / 5)
    lights[light] = (64, 64, 0)
    lights[light+12] = (64, 64, 0)

    #ticks
    #ticks = time.time() % 1
    #tick_round = round(ticks * 11)
    

    #lights[tick_round] = (64, 0, 64)
    #lights[tick_round + 12] = (64, 0, 64)

    #print hour, minute, light, time.time() % 1

my_lights = Lights(led)


#zero_lights()
#my_lights.start_bright()
while(True):
    my_lights.tick()
    led.update()
    #spidev.write(tick())
    #spidev.flush()
    #time.sleep(0.06) 

#
#test_set = bytearray(25 * 3);
#for y in range(255):
#	for x in range(25):
#		test_set[x*3    ] = gamma[y * x]
#        	test_set[x*3 + 1] = gamma[00]
#        	test_set[x*3 + 2] = gamma[255-(y *x)]
#	spidev.write(test_set)
#	spidev.flush()
#	time.sleep(0.06)
print "Done!"
