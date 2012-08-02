############################################################################
# This file is part of LImA, a Library for Image Acquisition
#
# Copyright (C) : 2009-2011
# European Synchrotron Radiation Facility
# BP 220, Grenoble 38043
# FRANCE
#
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
############################################################################

import threading
import os
import time

from Lima import Core

import ctypes as ct
import numpy as np
from XPad_par import *

class Communication(threading.Thread):
    Core.DEB_CLASS(Core.DebModCameraCom, 'Communication')

    COM_NONE,COM_START,COM_STOP,COM_CONF,COM_TEST = range(5)

    # Trigger Mode
    # 0 IntTrig & IntTrigMult
    # 1 ExtGate
    # 2 ExtTrigMult
    # 3 ExtTrigSingle
    TRG_INT_MULT,TRG_GATE,TRG_EXT_MULT,TRG_EXT_SING = range(4)
    TRG_DICT = {Core.IntTrigMult:TRG_INT_MULT,\
                Core.IntTrig:TRG_INT_MULT,\
                Core.ExtGate:TRG_GATE,\
                Core.ExtTrigMult:TRG_EXT_MULT,\
                Core.ExtTrigSingle:TRG_EXT_SING}

    # Analog out Mode
    #
    OUT_BUSY, OUT_BUSY_SHUTTER, OUT_IMGREAD_ENBL, OUT_OVFTRIG, OUT_EXPOSURE,\
              OUT_TEST1, OUT_IMGTRANSF, OUT_FIFO_FULL, OUT_EXT_GATE, OUT_TEST2\
              = range(10)

    # Test modes
    #
    TST_FLAT,TST_STRIP,TST_GRADIENT = range(3)

    def __init__(self):
        threading.Thread.__init__(self)
        
        self.__cond = threading.Condition()
        self.__frameCB = None
        self.__command = self.COM_NONE
        self.__run = True
        self.__configured = False
        self.__dll=ct.cdll.LoadLibrary("libxpad.so")
        
        if self.__dll.xpci_init(0,XPAD_31) != 0:
            raise Exception,"Communication Error: Initialzation failure."

        self.__ModMask = ct.c_ushort()
        if self.__dll.xpci_modAskReady(ct.pointer(self.__ModMask)) != 0:
            raise Exception,"Communication Error: Module communication failure"

        self.__ModNb   = self.__dll.xpci_getModNb(self.__ModMask)
        self.__BuffLen = 120*566*self.__ModNb
        self.__BuffNb = 0
        self.__ImgBuff = None
        self.setNbBuffers(1)

        self.__FramesNb  = 1
        self.__FramesRdy = 0

        # Calibration files
        self.__calFile1 = ''
        self.__calFile2 = ''
        
        # Module, Chip, Row, Column
        self.__DACL = np.zeros((2,7,120,82),dtype="int")
        self.__ITHL = np.zeros((2,7),dtype="int")

        # Standard Exposure parameters (in us)
        self.__TExp_m = ct.c_ushort((1000000 >> 16) & 0xFFFF)
        self.__TExp_l = ct.c_ushort(1000000 & 0xFFFF)
        self.__TLat_m = ct.c_ushort((5000 >> 16) & 0xFFFF)
        self.__TLat_l = ct.c_ushort(5000 & 0xFFFF)
        self.__TIni_m = ct.c_ushort((0 >> 16) & 0xFFFF)
        self.__TIni_l = ct.c_ushort(0 & 0xFFFF)
        self.__TSht_m = ct.c_ushort((0 >> 16) & 0xFFFF)
        self.__TSht_l = ct.c_ushort(0 & 0xFFFF)
        self.__TOvf_m = ct.c_ushort((4000 >> 16) & 0xFFFF)
        self.__TOvf_l = ct.c_ushort(4000 & 0xFFFF)

        self.__TrigMode = self.TRG_INT_MULT
        self.__OutMode  = self.OUT_BUSY
        self.__TestMode = self.TST_GRADIENT
                
    def __del__(self):
        if self.__dll.xpci_close(0) != 1:
            raise Exception,"Communication Error: Close failure"


    @Core.DEB_MEMBER_FUNCT
    def quit(self):
        self.__cond.acquire()
        print "quit lock"
        self.__run = False
        self.__cond.notify()
        print "quit unlock"
        self.__cond.release()
        time.sleep(0.01)
        self.join()

    @Core.DEB_MEMBER_FUNCT
    def ReadConfig(self):
        self.__cond.acquire()
        print "ReadConfig lock"
        ConfBuff = (ct.c_ushort * self.__BuffLen)()
        if self.__dll.xpci_getModConfig(self.__ModMask, 7, ConfBuff) != 0:
            self.__cond.release()
            raise Exception,"Communication Error: failure getting module configuration"
        arr = np.array(ConfBuff[0:self.__BuffLen], dtype='uint16')
        print "ReadConfig unlock"
        self.__cond.release()
        time.sleep(0.01)
        return arr

    @Core.DEB_MEMBER_FUNCT
    def setNbBuffers(self, nb_buffers):
        self.__cond.acquire()
        print "setNbBuffers lock"
        self.__BuffNb = nb_buffers
        self.__ImgBuff = (ct.POINTER(ct.c_ushort) * self.__BuffNb)()
        for i in range(self.__BuffNb):
            self.__ImgBuff[i] = (ct.c_ushort * self.__BuffLen)()
        self.__FramesRdy = 0
        print "setNbBuffers unlock"
        self.__cond.release()
        time.sleep(0.01)

    @Core.DEB_MEMBER_FUNCT
    def getNbBuffers(self):
        return self.__BuffNb

    @Core.DEB_MEMBER_FUNCT
    def getBuffer(self, buffer_nb):
        self.__cond.acquire()
        print "getBuffer lock"
        if buffer_nb >= self.__BuffNb:
            return None
        arr = np.array(self.__ImgBuff[buffer_nb][0:self.__BuffLen], dtype='uint16')
        print "getBuffer unlock"
        self.__cond.release()
        time.sleep(0.01)
        return arr

    @Core.DEB_MEMBER_FUNCT
    def setCalFiles(self,file1,file2) :
        self.__calFile1 = file1
        self.__calFile2 = file2

    @Core.DEB_MEMBER_FUNCT
    def getCalFiles(self) :
        return self.__calFile1, self.__calFile2

    @Core.DEB_MEMBER_FUNCT
    def setNbFrames(self,nb_frames) :
        self.__FramesNb = nb_frames
        if self.__FramesNb > self.__BuffNb:
            self.setNbBuffers(self.__FramesNb)

    @Core.DEB_MEMBER_FUNCT
    def getNbFrames(self) :
        return self.__FramesNb

    @Core.DEB_MEMBER_FUNCT
    def getNbFramesReady(self) :
        return self.__FramesRdy

    @Core.DEB_MEMBER_FUNCT
    def setTrigMode(self,trig_mode):
        self.__TrigMode = trig_mode

    @Core.DEB_MEMBER_FUNCT
    def getTrigMode(self) :
        return self.__TrigMode
    
    @Core.DEB_MEMBER_FUNCT
    def setOutMode(self,out_mode):
        self.__OutMode = out_mode

    @Core.DEB_MEMBER_FUNCT
    def getOutMode(self) :
        return self.__OutMode
    
    @Core.DEB_MEMBER_FUNCT
    def setExpTime(self,exp_time):
        self.__TExp_m = ct.c_ushort((exp_time >> 16) & 0xFFFF)
        self.__TExp_l = ct.c_ushort(exp_time & 0xFFFF)
        
    @Core.DEB_MEMBER_FUNCT
    def getExpTime(self) :
        return (((self.__TExp_m.value << 16) | self.__TExp_l.value) & \
                0xFFFFFFFF)

    @Core.DEB_MEMBER_FUNCT
    def setLatTime(self,lat_time):
        self.__TLat_m = ct.c_ushort((lat_time >> 16) & 0xFFFF)
        self.__TLat_l = ct.c_ushort(lat_time & 0xFFFF)
        
    @Core.DEB_MEMBER_FUNCT
    def getLatTime(self) :
        return (((self.__TLat_m.value << 16) | self.__TLat_l.value) & \
                0xFFFFFFFF)

    @Core.DEB_MEMBER_FUNCT
    def setIniTime(self,ini_time):
        self.__TIni_m = ct.c_ushort((ini_time >> 16) & 0xFFFF)
        self.__TIni_l = ct.c_ushort(ini_time & 0xFFFF)
        
    @Core.DEB_MEMBER_FUNCT
    def getIniTime(self) :
        return (((self.__TIni_m.value << 16) | self.__TIni_l.value) & \
                0xFFFFFFFF)

    @Core.DEB_MEMBER_FUNCT
    def setShtTime(self,sht_time):
        self.__TSht_m = ct.c_ushort((sht_time >> 16) & 0xFFFF)
        self.__TSht_l = ct.c_ushort(sht_time & 0xFFFF)
        
    @Core.DEB_MEMBER_FUNCT
    def getShtTime(self) :
        return (((self.__TSht_m.value << 16) | self.__TSht_l.value) & \
                0xFFFFFFFF)

    @Core.DEB_MEMBER_FUNCT
    def setOvfTime(self,ovf_time):
        self.__TOvf_m = ct.c_ushort((ovf_time >> 16) & 0xFFFF)
        self.__TOvf_l = ct.c_ushort(ovf_time & 0xFFFF)
        
    @Core.DEB_MEMBER_FUNCT
    def getOvfTime(self) :
        return (((self.__TOvf_m.value << 16) | self.__TOvf_l.value) & \
                0xFFFFFFFF)        

    @Core.DEB_MEMBER_FUNCT
    def Configure(self):
        if not ( os.access(self.__calFile1,os.R_OK) and  os.access(self.__calFile2,os.R_OK)):
            raise Exception,"Communication Error: calibration files not found. (%s,%s)" % (self.__calFile1,self.__calFile2)
        self.__cond.acquire()
        print "Configure lock"
        print "Communication: Send Config command"
        self.__command = self.COM_CONF
        self.__cond.notify()        
        print "Configure unlock"
        self.__cond.release()
        time.sleep(0.01)

    @Core.DEB_MEMBER_FUNCT
    def startAcquisition(self):
        self.__cond.acquire()
        print "startAcquisition lock"
        print "Communication: Send Start command"
        self.__command = self.COM_START
        self.__cond.notify()
        print "startAcquisition unlock"
        self.__cond.release()
        time.sleep(0.01)

    @Core.DEB_MEMBER_FUNCT
    def Test(self):
        if self.__command != self.COM_NONE:
            print "Communication Warning: System must be idle before testing\n"
            return
        self.__cond.acquire()
        print "Test lock"
        print "Communication: Send Test command"
        self.__command = self.COM_TEST
        self.__cond.notify()
        print "Test unlock"
        self.__cond.release()
        time.sleep(0.01)

    @Core.DEB_MEMBER_FUNCT
    def getCurrentCommand(self) :
        return self.__command

    @Core.DEB_MEMBER_FUNCT
    def isRunning(self):
        return self.__run

    def isConfigured(self):
        return self.__configured

    @Core.DEB_MEMBER_FUNCT
    def registerFrameCallback(self,frame_cb) :
        print "Communication: FrameCB registered"
        self.__frameCB = frame_cb
        
    @Core.DEB_MEMBER_FUNCT
    def unregisterFrameCallback(self,frame_cb) :
        print "Communication: FrameCB unregistered"
        self.__frameCB = None


    @Core.DEB_MEMBER_FUNCT
    def run(self):
        self.__cond.acquire()
        print "run lock"
        while self.__run :

            ### CONFIG COMMAND ###
            
            if self.__command == self.COM_CONF : 
                print "Communication: Config Command"

                # Read Configuration file
                for i,filename,mask in \
                        map(None, range(2), [self.__calFile1,self.__calFile2], [0x1,0x2]):
                    try:
                        CFile = open(filename)
                    except IOError:
                        raise 
                                           
                    for line in CFile:
                        if line.strip() == 'ITHL':
                            ithl = CFile.next().strip().split(' ')
                            self.__ITHL[i][:] = map(int, ithl)
                        if line.strip() == 'DACL':
                            for k in range(120):
                                for j in range(7):
                                    dacl = CFile.next().strip().split(' ')
                                    self.__DACL[i][j][k][:] = map(int,dacl)
                
                    # Save DACL values for each module
                    # Has to be in reverse order to avoid 
                    # overwriting of following pixels
                    for k in range(119,-1,-1):
                        for j in range(7):
                            calbuff = (ct.c_uint*len(self.__DACL[i][j][k][2:82]))( \
                                *(self.__DACL[i][j][k][2:82]*8+1))
                            if self.__dll.xpci_modSaveConfigL( \
                                mask, 0, j, k, calbuff) !=0 :
                                #self.__cond.release()
                                raise Exception,"Communication Error: Configuration saving failure (%#.2X, %d, %d, %d)" % (mask, i, j, k)
                
                    # Load DACL Values
                    if self.__dll.xpci_modDetLoadConfig(mask,0,0) != 0:
                        #self.__cond.release()
                        raise Exception,"Communication Error: Configuration loading failure"
                
                # Load register values
                retbuff = (ct.c_uint * (16*self.__ModNb))()
                if self.__dll.xpci_modLoadConfigG(self.__ModMask, 0x7F, ITUNE_V32  \
                                                   ,145, retbuff) != 0:
                    #self.__cond.release()
                    raise Exception,"Communication Error: Configuration loading failure (%#.2X, %#.2X)" % (self.__ModMask, 0x7F)
                    
                if self.__dll.xpci_modLoadConfigG(self.__ModMask, 0x7F, AMP_TP_V32 \
                                                   ,  0, retbuff) != 0:
                    #self.__cond.release()
                    raise Exception,"Communication Error: Configuration loading failure (%#.2X, %#.2X)" % (self.__ModMask, 0x7F)
                if self.__dll.xpci_modLoadConfigG(self.__ModMask, 0x7F, IMFP_V32   \
                                                   , 52, retbuff) != 0:
                    #self.__cond.release()
                    raise Exception,"Communication Error: Configuration loading failure (%#.2X, %#.2X)" % (self.__ModMask, 0x7F)
                if self.__dll.xpci_modLoadConfigG(self.__ModMask, 0x7F, IOTA_V32   \
                                                   , 40, retbuff) != 0:
                    #self.__cond.release()
                    raise Exception,"Communication Error: Configuration loading failure (%#.2X, %#.2X)" % (self.__ModMask, 0x7F)
                if self.__dll.xpci_modLoadConfigG(self.__ModMask, 0x7F, IPRE_V32   \
                                                   , 60, retbuff) != 0:
                    #self.__cond.release()
                    raise Exception,"Communication Error: Configuration loading failure (%#.2X, %#.2X)" % (self.__ModMask, 0x7F)
                if self.__dll.xpci_modLoadConfigG(self.__ModMask, 0x7F, IBUFFER_V32\
                                                   ,  0, retbuff) != 0:
                    #self.__cond.release()
                    raise Exception,"Communication Error: Configuration loading failure (%#.2X, %#.2X)" % (self.__ModMask, 0x7F)
                
                for i in range(2):
                    mmask = 0x01 << i
                    for j in range(7):
                        cmask = 0x01 << j
                        if self.__dll.xpci_modLoadConfigG(mmask, cmask, ITHL_V32   \
                                                          ,int(self.__ITHL[i][j]), retbuff) != 0:
                            #self.__cond.release()
                            raise Exception,"Communication Error: Configuration loading failure (%#.2X, %#.2X)" % (mmask, cmask)

                self.__configured = True
                self.__command = self.COM_NONE

            ### START  COMMAND ###

            if self.__command == self.COM_START : 
                print "Communication: Start Command"
                if self.__dll.xpci_sendExposureParameters( \
                    self.__ModMask,\
                    self.__TExp_m,\
                    self.__TExp_l,\
                    self.__TLat_m,\
                    self.__TLat_l,\
                    self.__TIni_m,\
                    self.__TIni_l,\
                    self.__TSht_m,\
                    self.__TSht_l,\
                    self.__TOvf_m,\
                    self.__TOvf_l,\
                    self.__TrigMode,\
                    0,0,self.__FramesNb,\
                    self.__OutMode,\
                    B2,0,0) != 0:
                    #self.__cond.release()
                    raise Exception, "Communication Error: failure sending exposure parameters"
                #self.__cond.release()
                #print "run unlock"
                if self.__dll.xpci_getImgSeq_imxpad( \
                    B2, self.__ModMask, 7, \
                    self.__FramesNb, \
                    self.__ImgBuff, 0) != 0:                        
                    #self.__cond.acquire()
                    #print "run lock"
                    #self.__cond.release()
                    raise Exception, "Communication Error: failure getting images"
                self.__FramesRdy = self.__FramesNb
                if self.__frameCB:
                    for i in range(self.__FramesRdy):
                        arr = np.array(self.__ImgBuff[i][0:self.__BuffLen], dtype='uint16')
                        arr.resize(240,566)
                        data = np.array(arr[:,5:565])
                        FrameInfo = Core.HwFrameInfoType(i,\
                                                    data,Core.Timestamp(),0,\
                                                    Core.HwFrameInfoType.Transfer)
                        self.__frameCB.newFrameReady(FrameInfo)
                        print "Frame",i,"ready"
                    
                self.__command = self.COM_NONE

            ### TEST   COMMAND ###

            if self.__command == self.COM_TEST : 
                print "Communication: Test Command"
                #self.__cond.release()
                #print "run unlock"
                if self.__dll.xpci_modLoadAutoTest(self.__ModMask, \
                                                   0x4F6B, \
                                                   self.__TestMode ):
                    #self.__cond.acquire()
                    #print "run lock"
                    #self.__cond.release()
                    raise Exception, "Communication Error: failure loading autotest\n"
                self.setNbBuffers(1)
                #self.__cond.acquire()
                print "run lock"
                if self.__dll.xpci_readOneImage( \
                    B2, self.__ModMask, 7, \
                    self.__ImgBuff) !=0:
                    #self.__cond.release()
                    raise Exception, "Communication Error: failure loading autotest\n"
                self.__command = self.COM_NONE

            ###  NO    COMMAND ###

            # By default wait for a command
            else :
                print "Communication: No Command"
                while  self.__run == True and self.__command == self.COM_NONE:
                    print "Run sleep"
                    self.__cond.wait()
                    print "Run wake up"
        self.__cond.release()
        print "run unlock"
        time.sleep(0.01)
        
def main():
    """
    Usage: 
         pyXPad [opt] output

    Argument:
        output: Base name for the output file. Image number and extension will
            be append.
            Ex:
                #python pyXPad data/Test
                #ls data/Test*
                data/Test_0000.edf

    Options:
        -c: Load calibration files. Calibration file names are defined in
            pyXPad_conf.py
        -n: Number of images to be taken.
        -e: Exposure time in us.
        -l: Latency time in us (minimum 5000 us).
        -o: Overflow counter pull period (minimum 4000 us).
        -t: Trigger mode.
            0: Internal trigger
            1: External gate
            2: External trigger for sequence
            3: External trigger for singles
        -a: Analog output mode.
            0: Bussy
            1: Bussy - Shutter time
            2: Image read enabled
            3: Overflow counter pull
            4: Exposure
            5: Reserved
            6: Image transfer
            7: FIFO full
            8: External Gate
            9: Reserved

    Press "q" to exit 

    """

    import getopt, sys
    import pydoc
    import time
    from EdfFile import EdfFile as EDF

    try:
        opts, args = getopt.getopt(sys.argv[1:], "cn:t:a:e:l:o:")
    except getopt.GetoptError, err:
        # print help information and exit:
        pydoc.help(main)
        sys.exit(2)

    print args
        
    if len(args) == 0:
        pydoc.help(main)        
        sys.exit()

    Comm = Communication()
    filename = args[0]

    DoConfigure = False

    for o, a in opts:
        if o in ("-c"):
            DoConfigure = True
        elif o in ("-n"):
            Comm.setNbFrames(int(a))
        elif o in ("-t"):
            Comm.setTrigMode(int(a))
        elif o in ("-a"):
            Comm.setOutMode(int(a))
        elif o in ("-e"):
            Comm.setExpTime(int(a))
        elif o in ("-l"):
            Comm.setLatTime(int(a))
        elif o in ("-o"):
            Comm.setOvfTime(int(a))
        else:
            assert False, "unhandled option"

    print
    print "Settings:"
    print "==================="
    print "Load Configuration:",DoConfigure
    print "Output filename:   ","%s_XXXX%s" % (filename,".edf")
    print "Number of Frames:  ",Comm.getNbFrames()            
    print "Trigger Mode:      ",Comm.getTrigMode()
    print "Output signal:     ",Comm.getOutMode()
    print "Exposure time:     ",Comm.getExpTime()
    print "Latency type:      ",Comm.getLatTime()
    print "Overflow pull:     ",Comm.getOvfTime()
    print

    Comm.start()
    if DoConfigure:
        Comm.Configure()
        if not Comm.isAlive():
            raise SystemExit
        

    Comm.startAcquisition()
    if not Comm.isAlive():
        raise SystemExit

    while Comm.getCurrentCommand() != Comm.COM_NONE:        
        time.sleep(0.2)

    for i in range(Comm.getNbFramesReady()):
        if not Comm.isAlive():
            raise SystemExit       
        arr = Comm.getBuffer(i)
        arr.resize(240,566)
        f = EDF("%s_%.4d%s" % (filename,i,".edf"))
        f.WriteImage({},arr[:,5:565])
        del f

    Comm.quit()        
    del Comm

if __name__ == "__main__":
    main()

