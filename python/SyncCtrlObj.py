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
import weakref

from Lima import Core

class SyncCtrlObj(Core.HwSyncCtrlObj) :
    Core.DEB_CLASS(Core.DebModCamera, "SyncCtrlObj")

    def __init__(self,comm_object,det_info) :
        Core.HwSyncCtrlObj.__init__(self)
        self.__comm = weakref.ref(comm_object)
        self.__det_info = weakref.ref(det_info)
        
        #Variables and default values
        self.__exposure  = None
        self.getExpTime()
        self.__latency   = None
        self.getLatTime()
        self.__trigMode  = None
        self.getTrigMode()

    @Core.DEB_MEMBER_FUNCT
    def checkTrigMode(self,trig_mode) :
        com = self.__comm()
        return com.TRG_DICT.has_key(trig_mode)
        
    @Core.DEB_MEMBER_FUNCT
    def setTrigMode(self,trig_mode):
        com = self.__comm()
        if com.TRG_DICT.has_key(trig_mode):
            self.__trigMode = trig_mode
            com.setTrigMode(com.TRG_DICT[self.__trigMode])
        else:
            raise Core.Exceptions(Core.Hardware,Core.NotSupported)

    @Core.DEB_MEMBER_FUNCT
    def getTrigMode(self) :
        com = self.__comm()
        if self.__trigMode is None:
            trg = com.getTrigMode()
            for t in com.TRG_DICT:
                if com.TRG_DICT[t] == trg:
                    self.__trigMode = t
                    break
            if self.__trigMode is None:
                raise Core.Exceptions(Core.Hardware,Core.InvalidValue)
        return self.__trigMode
    
    @Core.DEB_MEMBER_FUNCT
    def setExpTime(self,exp_time):
        self.__exposure = exp_time
        self.__comm().setExpTime(int(self.__exposure*1000000))
        
    @Core.DEB_MEMBER_FUNCT
    def getExpTime(self) :
        if self.__exposure is None:
            self.__exposure = self.__comm().getExpTime()/1000000
        return self.__exposure

    @Core.DEB_MEMBER_FUNCT
    def setLatTime(self,lat_time):
        self.__latency = lat_time
        self.__comm().setLatTime(int(self.__latency*1000000))

    @Core.DEB_MEMBER_FUNCT
    def getLatTime(self) :
        if self.__latency is None:
            self.__latency = self.__comm().getLatTime()/1000000
        return self.__latency

    @Core.DEB_MEMBER_FUNCT
    def setNbFrames(self,nb_frames) :
        self.__comm().setNbFrames(nb_frames)

    @Core.DEB_MEMBER_FUNCT
    def getNbFrames(self) :
        return self.__comm().getNbFrames()

    @Core.DEB_MEMBER_FUNCT
    def setNbHwFrames(self,nb_frames) :
        self.setNbFrames(nb_frames)

    @Core.DEB_MEMBER_FUNCT
    def getNbHwFrames(self) :
        return self.getNbFrames()

    @Core.DEB_MEMBER_FUNCT
    def getValidRanges(self) :
        det_info = self.__det_info()
        return Core.HwSyncCtrlObj.ValidRangesType(det_info.get_min_exposition_time(),
                                                  det_info.get_max_exposition_time(),
                                                  det_info.get_min_latency(),
                                                  det_info.get_max_latency())

    def prepareAcq(self) :
        pass



