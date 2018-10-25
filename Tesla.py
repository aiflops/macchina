#!/usr/bin/env python
# -*- coding: utf-8 -*-
import serial
import threading
import RPi.GPIO as GPIO
import time
import picamera
from socket import error as SocketError
import socket


class Connection(threading.Thread):
    def __init__(self):
        super(Connection, self).__init__()
        self.strRaspData = '0_0'
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_socket.settimeout(1.0)


    def run(self):
        message = b'0_0'
        addr = ("192.168.0.100", 12016)


        self.client_socket.sendto(message, addr)
        count = 0
        data = None


        while 1:
            if data == None:
                self.client_socket.sendto(message, addr)
            try:
                self.strRaspData, server = self.client_socket.recvfrom(1024)
            except socket.timeout:
                print('REQUEST TIMED OUT')
                self.strRaspData = '0_0'
                count += 1
                if (count == 20):
                    self.strRaspData = None
                    break
        self.client_socket.close()
        GPIO.cleanup()

    def close(self):
        self.client_socket.close()

    def getData(self):
        return self.strRaspData

class Camera(threading.Thread):

    def __init__(self):
        super(Camera, self).__init__()

    def run(self):
        error = False
        with picamera.PiCamera() as self.camera:
            self.camera.resolution = (640, 480)
            self.camera.rotation = 180
            self.camera.framerate = 30

            server_socket = socket.socket()
            server_socket.bind(('0.0.0.0', 8080))
            server_socket.listen(0)

            # Accept a single connection and make a file-like object out of it
            connection = server_socket.accept()[0].makefile('wb')
            try:
                self.camera.start_recording(connection, format='h264')
                self.camera.wait_recording(24*60*60)
                self.camera.stop_recording()

            except SocketError as e:
                self.camera.stop_recording()
                self.camera.close()
                connection.close()
                server_socket.close()

            finally:
                self.camera.close()
                connection.close()
                server_socket.close()

    def stop_record(self):
        self.camera.close()


class Tesla:
     def __init__(self):
         GPIO.setmode(GPIO.BCM)

         self.pin4 = 4
         self.pin5 = 5
         self.pin6 = 6  # kierunek kola
         self.pin13 = 13  # kierunek kola
         self.pin17 = 17  # pwm
         self.pin19 = 19  # pwm
         self.pin22 = 22  # kierunek kola
         self.pin27 = 27  # kierunek kola

         self.SAMPLETIME = 1
         self.TARGET = 45
         self.KP = 0.01
         self.KD = 0.005
         self.KI = 0.005

         self.lastEnL = 0
         self.lastEnP = 0

         self.m1_speed = 0
         self.m2_speed = 0

         self.e1_prev_error = 0
         self.e2_prev_error = 0

         self.e1_sum_error = 0
         self.e2_sum_error = 0
         self.initGPIO()

         self.camera = Camera()
         self.camera.start()

         self.connection =  Connection()
         self.connection.start()


     def forward(self,lPwm,rPwm):
        # self.m1_speed = lPwm
        # self.m2_speed = rPwm
        self.pwmLeft.ChangeDutyCycle(lPwm)
        self.pwmRight.ChangeDutyCycle(rPwm)

     def forward_b(self,lPwm,rPwm):
        self.m1_speed = lPwm
        self.m2_speed = rPwm
        self.pwmLeft.ChangeDutyCycle(lPwm)
        self.pwmRight.ChangeDutyCycle(rPwm)

     def teslaStop(self):
         self.pwmLeft.ChangeDutyCycle(0)
         self.pwmRight.ChangeDutyCycle(0)

     def initGPIO(self):
         GPIO.setup(self.pin4, GPIO.OUT)
         GPIO.output(self.pin4, 1)
         GPIO.setup(self.pin5, GPIO.OUT)
         GPIO.output(self.pin5, 1)
         GPIO.setup(self.pin6, GPIO.OUT)
         GPIO.output(self.pin6, 1)
         GPIO.setup(self.pin13, GPIO.OUT)
         GPIO.output(self.pin13, 0)
         GPIO.setup(self.pin13, GPIO.OUT)
         GPIO.output(self.pin13, 0)
         GPIO.setup(self.pin6, GPIO.OUT)
         GPIO.output(self.pin6, 1)
         GPIO.setup(self.pin22, GPIO.OUT)
         GPIO.output(self.pin22, 0)
         GPIO.setup(self.pin27, GPIO.OUT)
         GPIO.output(self.pin27, 1)
         GPIO.setup(self.pin17, GPIO.OUT)
         GPIO.setup(self.pin19, GPIO.OUT)

     # --------------------------------------------------------------------------
         self.pwmRight = GPIO.PWM(self.pin17, 50)
         self.pwmLeft = GPIO.PWM(self.pin19, 50)
         self.pwmRight.start(self.m1_speed)
         self.pwmLeft.start(self.m2_speed)

     #  funkcja odpowiadajaca za jazde pojazdu
     def teslaRun(self):
         run = True
         while run:
             response  = self.connection.getData()
             pwmStringList =  response.split('_')
             if (pwmStringList[0] == 'q'):
                 GPIO.cleanup()
                 self.camera.stop_record()
                 self.connection.close()
                 break;
             else:
                 pwmLeft = pwmStringList[0]
                 pwmRight = pwmStringList[1]
                 self.forward(int(pwmLeft),int(pwmRight))
                 time.sleep(.01)

def main():

    tesla = Tesla()
    tesla.teslaRun()
    print('KONIEC PROGRAMU')
    # rotation 45
    # tesla.forward_b(0,40)
    # time.sleep(3)



if __name__ == "__main__":
    main()