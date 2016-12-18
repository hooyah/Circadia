"""
    Circadia Theme Editor - socket client

    communicates with a remote server over sockets

    Author: fhu

"""


import threading
import socket
import json
import pygame


#
# todo: implement remote sound. sound is currently played back locally
#

class CircadiaSocketClient:

    def __init__(self):

        self.addr = "0.0.0.0"
        self.port = 0
        self.worker = None
        self.starttime = 0
        self.success = 0

        self.canvasW = 16
        self.canvasH = 18

        self.sounds = dict()
        pygame.mixer.pre_init(frequency=41000)
        pygame.init()


    def __del__(self):

        self.disconnect()


    def connect(self, addr, port):
        """
        connect to the lamp, non blocking
        :param addr: ip address, string
        :param port: port, int
        :return:
        """

        if self.isBusy():
            return false

        self.addr = addr
        self.port = port
        self.success = 0

        # send a greeting
        self.__sendMsg("hello")


    def disconnect(self):

        if self.isConnected():
            self.__sendMsg('reset')


    def isConnected(self):
        """
        find out if the lamp is talking
        :return: lamp is connected, bool
        """
        if not self.isBusy():
            return self.success > 0
        else:
            return False


    def isBusy(self):
        """
        find out if a transmission is in progress
        :return:
        """
        if not self.worker:
            return False

        if self.worker[0].isAlive():
            return True

        if self.worker[2] == "ok":
            self.success += 1
        elif self.worker[2][:3] == "cfg":
            tok = self.worker[2].split(':')
            self.canvasW = int(tok[1])
            self.canvasH = int(tok[2])
            self.success += 1
            print 'received dim', self.canvasW, self.canvasH
        else:
            self.success = 0
            print self.worker[2]
        self.worker = None


    def startSoundLoop(self, hash, filename, volume):
        print 'starting', filename, 'on', hash
        # (filename, soundobject)
        if hash in self.sounds:
            soundRecord = self.sounds[hash]
            playing = soundRecord[1].get_num_channels() > 0
            if soundRecord[0] != filename:
                if playing:
                    soundRecord[1].fadeout(800)
                soundRecord[0] = filename
                soundRecord[1] = pygame.mixer.Sound(filename)
                soundRecord[1].play(loops=-1)
                soundRecord[1].set_volume(volume)
            else:
                soundRecord[1].play(loops=-1)
                soundRecord[1].set_volume(volume)

        else:
            self.sounds[hash] = [0, 0, 0]
            soundRecord = self.sounds[hash]
            soundRecord[0] = filename
            soundRecord[1] = pygame.mixer.Sound(filename)
            soundRecord[1].play(loops=-1)
            soundRecord[1].set_volume(volume)


    def stopSoundLoop(self, hash):
        print 'stopping', hash
        if hash in self.sounds:
            self.sounds[hash][1].fadeout(800)

    def setSoundVolume(self, hash, volume):
        if hash in self.sounds:
            self.sounds[hash][1].set_volume(volume)


    def sendGradient(self, grad):
        """
        :param grad: list of 18 colors [ [r0,g0,b0], [r1,g1,b1], ...]
        :return: busy state
        """

        buff = json.dumps(grad)
        return self.__sendMsg('grad:'+buff)

    def sendCanvas(self, canvas):
        """
        :param canvas: list of 18*16 colors [ r0,g0,b0, r1,g1,b1, ...]
        :return: busy state
        """

        buff = json.dumps(canvas)
        return self.__sendMsg('cnv:'+buff)


    def __sendMsg(self, msg):
        if self.isBusy():
            return False
        job = ['thread', msg, None]
        t = threading.Thread(target=self.__dispatch, args=(self.addr, self.port, job))
        job[0] = t
        t.start()
        self.worker = job
        return True


    @staticmethod
    def __dispatch(addr, port, msg):
        """
        worker
        :param addr:
        :param port:
        :param msg: list (thread obj, message, return value)
        :return:
        """
        print 'opening socket'
        clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientsocket.settimeout(2)
        try:
            clientsocket.connect((addr, port))
        except:
            msg[2] = "couldn't connect to socket"
            return

        print 'sending'
        n = clientsocket.sendall(msg[1])
        clientsocket.shutdown(socket.SHUT_WR)
        print 'sent', n
        buffer = ""
        while(1):
            buf = clientsocket.recv(1024)
            if len(buf) > 0:
                buffer += buf
            else:
                print 'received %d bytes'%len(buffer)
                msg[2] = buffer
                break
        clientsocket.close()
        print 'done'






__author__ = 'fhu'
