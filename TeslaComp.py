# -*- coding: utf-8 -*-
import random
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QTimer
from PyQt4.QtCore import pyqtSlot
import sys
# import socket programming library
import socket
import cv2
import time
import numpy as np
import os

# import thread module
from _thread import *
import threading

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


''' 
    Klasa WorkThread odpowiada za polaczenie z raspberry pi
    jest realizowana na watku, wywolywanym w konstruktorze
    glownego menu.
'''
class WorkThread(QtCore.QThread):
    def __init__(self):
        super(WorkThread, self).__init__()
        self.camera = cv2.VideoCapture('http://192.168.0.201:8080/')
        # self.camera = cv2.VideoCapture(0)
        self.running = True

    def run(self):
        while self.running:
            b, self.image = self.camera.read()
            self.image = cv2.cvtColor(self.image,cv2.COLOR_BGR2RGB)
            self.emit(QtCore.SIGNAL('update_Camera'), self.image)

    def stop(self):
        self.running = False


'''
    Glowna klasa aplikacji
'''
class GUIApp(QtGui.QMainWindow):

    strProsto = _translate("MainWindow", "PROSTO", None)
    strLewo = _translate("MainWindow", "LEWO", None)
    strPrawo = _translate("MainWindow", "PRAWO", None)
    strStop = _translate("MainWindow", "STOP", None)
    strPrzod = _translate("MainWindow", "PRZOD", None)
    strWsteczny = _translate("MainWindow", "WSTECZNY", None)

    def __init__(self, parent=None):
        super(GUIApp, self).__init__(parent)
        self.setupUi(self)

        self.workThread = WorkThread()
        self.connect(self.workThread, QtCore.SIGNAL('update_Camera'), self.draw)
        self.workThread.start()
        # Ważne
        self.processThread = threading.Thread(target=self.showVal)
        self.processThread.start()

        self.reverse =  False
        self.lastSpeed = 0

        self.line = False
        self.normal =  True

        self.position = None

        self.pwmValue = 0
        self.pwmLeft = 0
        self.pwmRigt = 0

    def showVal(self):
        t = threading.currentThread()
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind(('', 12016))

        messageFromClient, address = server_socket.recvfrom(1024)
        messegeDecode = messageFromClient.decode()

        sendStr = '0_0'
        if (messegeDecode):
            while getattr(t, "do_run", True):
                if (self.pwmRigt is not 'q'):
                    self.pwmLeft = self.pwmValidation(self.pwmLeft)
                    self.pwmRigt = self.pwmValidation(self.pwmRigt)
                    self.label_4.setText(_translate("MainWindow", "PWM LEFT: " + str(self.pwmLeft), None))
                    self.label_7.setText(_translate("MainWindow", "PWM RIGHT: "+ str(self.pwmRigt), None))
                sendStr = str(self.pwmLeft) + '_' + str(self.pwmRigt)

                server_socket.sendto(sendStr.encode(), address)
                time.sleep(.01)

        server_socket.close()
# funkcja odpowiada za renderowanie okienka
# inicjacja wszytkich przyciskow
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(1045, 810)
        MainWindow.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setMinimumSize(QtCore.QSize(1024, 768))
        self.centralwidget.setMaximumSize(QtCore.QSize(1024, 768))
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayoutWidget = QtGui.QWidget(self.centralwidget)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(60, 10, 921, 482))
        self.gridLayoutWidget.setObjectName(_fromUtf8("gridLayoutWidget"))
        self.gridLayout = QtGui.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_3 = QtGui.QLabel(self.gridLayoutWidget)
        self.label_3.setMinimumSize(QtCore.QSize(640, 480))
        self.label_3.setMaximumSize(QtCore.QSize(640, 480))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 0, 0, 1, 1)
        self.frame = QtGui.QFrame(self.centralwidget)
        self.frame.setGeometry(QtCore.QRect(40, 560, 931, 191))
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.pushButton_4 = QtGui.QPushButton(self.frame)
        self.pushButton_4.setGeometry(QtCore.QRect(10, 20, 201, 51))
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_4.setFont(font)
        self.pushButton_4.setFocusPolicy(QtCore.Qt.NoFocus)
        self.pushButton_4.setObjectName(_fromUtf8("pushButton_4"))
        self.pushButton = QtGui.QPushButton(self.frame)
        self.pushButton.setGeometry(QtCore.QRect(10, 130, 201, 51))
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton.setFont(font)
        self.pushButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.pushButton_5 = QtGui.QPushButton(self.frame)
        self.pushButton_5.setGeometry(QtCore.QRect(270, 20, 201, 51))
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_5.setFont(font)
        self.pushButton_5.setFocusPolicy(QtCore.Qt.NoFocus)
        self.pushButton_5.setObjectName(_fromUtf8("pushButton_5"))
        self.pushButton_6 = QtGui.QPushButton(self.frame)
        self.pushButton_6.setGeometry(QtCore.QRect(270, 130, 201, 51))
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_6.setFont(font)
        self.pushButton_6.setFocusPolicy(QtCore.Qt.NoFocus)
        self.pushButton_6.setObjectName(_fromUtf8("pushButton_6"))
        self.pushButton_7 = QtGui.QPushButton(self.frame)
        self.pushButton_7.setGeometry(QtCore.QRect(710, 10, 201, 51))
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_7.setFont(font)
        self.pushButton_7.setFocusPolicy(QtCore.Qt.NoFocus)
        self.pushButton_7.setObjectName(_fromUtf8("pushButton_7"))
        self.pushButton_8 = QtGui.QPushButton(self.frame)
        self.pushButton_8.setGeometry(QtCore.QRect(710, 130, 201, 51))
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_8.setFont(font)
        self.pushButton_8.setFocusPolicy(QtCore.Qt.NoFocus)
        self.pushButton_8.setObjectName(_fromUtf8("pushButton_8"))
        self.pushButton_9 = QtGui.QPushButton(self.frame)
        self.pushButton_9.setGeometry(QtCore.QRect(710, 70, 201, 51))
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_9.setFont(font)
        self.pushButton_9.setFocusPolicy(QtCore.Qt.NoFocus)
        self.pushButton_9.setObjectName(_fromUtf8("pushButton_9"))
        self.label_4 = QtGui.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(200, 520, 171, 31))
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.label_7 = QtGui.QLabel(self.centralwidget)
        self.label_7.setGeometry(QtCore.QRect(660, 520, 171, 31))
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        self.label_7.setFont(font)
        self.label_7.setAlignment(QtCore.Qt.AlignCenter)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1045, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
# podpisanie wszytkich button-ow,
# przyczepianie etykiet
    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.label_3.setText(_translate("MainWindow", "Kamera", None))

        self.pushButton_4.setText(_translate("MainWindow", "START", None))
        self.pushButton.setText(_translate("MainWindow", "STOP", None))

        self.pushButton_5.setText(_translate("MainWindow", "LINE", None))
        self.pushButton_6.setText(_translate("MainWindow", "NORMAL", None))
        self.pushButton_7.setText(_translate("MainWindow", "NORMAL", None))
        self.pushButton_8.setText(_translate("MainWindow", "DRY", None))
        self.pushButton_9.setText(_translate("MainWindow", "SLIPPERY", None))


        self.label_4.setText(_translate("MainWindow", "PWM LEFT: ", None))
        self.label_7.setText(_translate("MainWindow", "PWM RIGHT: ", None))

        self.pushButton.clicked.connect(self.stop)
        self.pushButton_5.clicked.connect(self.showLine)
        self.pushButton_6.clicked.connect(self.showCamera)
        self.pushButton_4.clicked.connect(self.save)

    # zatrzymanie pojazdu
    # uruchamia się po naciśnięciu przycisku
    def stop(self):
        print("stop")
    # funkcja odpowiada za wyswietlenie obrazu wykrycia lini
    def showLine(self):
        self.normal = False
    # pokazuje widok z kamery
    def showCamera(self):
        self.normal = True
    # zamkniecie okienka
    def closeEvent(self, event):
        self.workThread.stop()
        event.accept()
    # funkcja odpowiada za rysowania lini
    def drawLines(self, img,lines):
        listX = []
        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                listX.append(x1)
        position = min(listX)+max(listX)/2
        height, width, channel = img.shape
        bpl = 3 * width
        self.qImg = QtGui.QImage(img, width, height, bpl, QtGui.QImage.Format_RGB888)

        return None

    # funkcja odpowiada za wyswietlanie widoku z kamery
    def draw(self, img):
        threshold = 80
        minLineLength = 40
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        blurred2 = cv2.GaussianBlur(gray, (9, 9), 0)
        edged2 = cv2.Canny(blurred2, 25, 50)
        lines = cv2.HoughLinesP(edged2, 1, np.pi / 180, threshold, 0, minLineLength, 100);
        self.position = None
        if self.normal:
            try:
                self.position = self.drawLines(img, lines)
            except:
                height, width, channel = img.shape
                bpl = 3 * width
                self.qImg = QtGui.QImage(img, width, height, bpl, QtGui.QImage.Format_RGB888)
        else:
            gray = cv2.cvtColor(edged2, cv2.COLOR_GRAY2RGB)
            height, width, chanel = gray.shape
            bpl = 3 * width
            self.qImg = QtGui.QImage(gray, width, height, bpl, QtGui.QImage.Format_RGB888)

        pix = QtGui.QPixmap(self.qImg)
        self.label_3.setPixmap(pix)
        self.label_3.show()

    def keyPressEvent(self, event):

        if event.key() == QtCore.Qt.Key_1:
            self.pwmLeft += 2
            event.accept()

        if event.key() == QtCore.Qt.Key_2:
            self.pwmLeft -= 2
            event.accept()

        # -----------------------------------------------
        if event.key() == QtCore.Qt.Key_0:
            self.pwmRigt += 2
            event.accept()

        if event.key() == QtCore.Qt.Key_9:
            self.pwmRigt -= 2
            event.accept()

        if event.key() == QtCore.Qt.Key_Escape:
            self.pwmRigt = 'q'
            self.pwmLeft = 'q'
            event.accept()

        if event.key() == QtCore.Qt.Key_Space:
            self.pwmRigt = 0
            self.pwmLeft = 0
            event.accept()

    def pwmValidation(self, pwm):
        pwm = 100 if pwm>= 100 else pwm
        pwm = 0 if pwm<= 0 else pwm
        return pwm

    def testFunction(self):
        sendStr = str(self.pwmLeft)+"_"+str(self.pwmRigt)

        print(sendStr)


    def closeEvent(self, event):
        self.processThread.do_run = False

    def save(self):
        pass

def main():
    app = QtGui.QApplication(sys.argv)  # A new instance of QApplication
    form = GUIApp()                 # We set the form to be our ExampleApp (design)
    form.show()                         # Show the form
    app.exec_()                         # and execute the app


if __name__ == '__main__':              # if we're running file directly and not importing it
    main()                              # run the main function

# lower = np.array([0, 0, 0])
# upper = np.array([30, 30, 30])
# img2 = cv2.inRange(img, lower, upper)
# connected
# blurred = cv2.GaussianBlur(img2, (5, 5), 0)
# edged = cv2.Canny(blurred, 90, 170)
# cv2.imshow("color detection", img2)
# cv2.imshow("connected method", edged)
# self.drawLines(img, lines)
# cv2.imshow("edged detection", gray)