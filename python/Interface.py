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
import time
from Lima import Core

from DetInfoCtrlObj import DetInfoCtrlObj
from SyncCtrlObj import SyncCtrlObj
from BufferCtrlObj import BufferCtrlObj
from Communication import Communication

class Interface(Core.HwInterface) :
    Core.DEB_CLASS(Core.DebModCamera, "Interface")

    def __init__(self) :
	Core.HwInterface.__init__(self)

        self.__comm = Communication()
        self.__comm.start()
        self.__detInfo = DetInfoCtrlObj()
        self.__detInfo.init()
        self.__buffer = BufferCtrlObj(self.__comm,self.__detInfo)
        self.__syncObj = SyncCtrlObj(self.__comm,self.__detInfo)

    def __del__(self) :
        self.__comm.quit()

    def quit(self) :
        self.__comm.quit()
        
    @Core.DEB_MEMBER_FUNCT
    def getCapList(self) :
        return [Core.HwCap(x) for x in [self.__detInfo,self.__syncObj,self.__buffer]]

    @Core.DEB_MEMBER_FUNCT
    def reset(self,reset_level):
        pass
        
    @Core.DEB_MEMBER_FUNCT
    def prepareAcq(self):
        self.__syncObj.prepareAcq()
#        while self.__comm.getCurrentCommand() != Communication.COM_NONE:
#            time.sleep(0.1)

    @Core.DEB_MEMBER_FUNCT
    def loadConfig(self,file1,file2):
        self.__comm.setCalFiles(file1,file2)
        self.__comm.Configure()            

    @Core.DEB_MEMBER_FUNCT
    def setConfigId(self,Id):
        self.__comm.setConfigId(Id)

    @Core.DEB_MEMBER_FUNCT
    def getConfigId(self):
        return self.__comm.getConfigId()

    @Core.DEB_MEMBER_FUNCT
    def startAcq(self) :
        self.__comm.startAcquisition()

    @Core.DEB_MEMBER_FUNCT
    def stopAcq(self) :
        pass
        
    @Core.DEB_MEMBER_FUNCT
    def getStatus(self) :
        CommOk = self.__comm.isAlive() and self.__comm.isRunning()
        CommState = self.__comm.getCurrentCommand()
        status = Core.HwInterface.StatusType()

        if not CommOk:
            status.det = Core.DetFault
            status.acq = Core.AcqFault
            deb.Error("Detector communication is not running")
        elif CommState == Communication.COM_NONE:
            status.det = Core.DetIdle
            status.acq = Core.AcqReady
        elif not self.__comm.isConfigured() :
            status.det = Core.DetFault
            status.acq = Core.AcqConfig
        else:
            if CommState == Communication.COM_START or \
                   CommState == Communication.COM_TEST:
                status.det = Core.DetExposure
            else:
                status.det = Core.DetFault
            if self.__syncObj.getNbFrames() == self.__comm.getNbFramesReady():
                status.acq = Core.AcqReady
            else:
                status.acq = Core.AcqRunning

        status.det_mask = (Core.DetExposure|Core.DetFault)
        return status
    
    @Core.DEB_MEMBER_FUNCT
    def getNbAcquiredFrames(self) :
        return self.__comm.getNbFramesReady()
    
    @Core.DEB_MEMBER_FUNCT
    def getNbHwAcquiredFrames(self):
        return self.getNbAcquiredFrames()


