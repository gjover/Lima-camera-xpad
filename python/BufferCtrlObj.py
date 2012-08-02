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

class BufferCtrlObj(Core.HwBufferCtrlObj):
	Core.DEB_CLASS(Core.DebModCamera,"BufferCtrlObj")

        def __init__(self,comm_object,det_info) :
            Core.HwBufferCtrlObj.__init__(self)
            self.__comm = weakref.ref(comm_object)
            self.__det_info = weakref.ref(det_info)

        def __del__(self) :
            pass

        @Core.DEB_MEMBER_FUNCT
	def setFrameDim(self,frame_dim) :
            pass
            
        @Core.DEB_MEMBER_FUNCT
        def getFrameDim(self) :
            det_info = self.__det_info()
            return Core.FrameDim(det_info.getDetectorImageSize(),
                                 det_info.getDefImageType())
        
        @Core.DEB_MEMBER_FUNCT
        def setNbBuffers(self,nb_buffers) :            
            self.__comm().setNbBuffers(nb_buffers)
            
        @Core.DEB_MEMBER_FUNCT
        def getNbBuffers(self) :
            return self.__comm().getNbBuffers()

        @Core.DEB_MEMBER_FUNCT
        def setNbConcatFrames(self,nb_concat_frames) :
            if nb_concat_frames != 1:
                raise Core.Exception(Core.Hardware,Core.NotSupported)

        @Core.DEB_MEMBER_FUNCT
        def getNbConcatFrames(self) :
            return 1
            
        @Core.DEB_MEMBER_FUNCT
        def getMaxNbBuffers(self) :
            return 10000 # Just a gess. TODO: Set the right value

        @Core.DEB_MEMBER_FUNCT
        def getBufferPtr(self,buffer_nb,concat_frame_nb = 0) :
            pass
        
        @Core.DEB_MEMBER_FUNCT
        def getFramePtr(self,acq_frame_nb) :
            pass

        @Core.DEB_MEMBER_FUNCT
        def getStartTimestamp(self,start_ts) :
            pass
        
        @Core.DEB_MEMBER_FUNCT
        def getFrameInfo(self,acq_frame_nb) :
            arr = self.__comm().getBuffer(acq_frame_nb)
            arr.resize(240,566)
            data = arr[:,5:565]
            FrameInfo = Core.HwFrameInfoType(acq_frame_nb,\
                                             data,Core.Timestamp(),0,\
                                             Core.HwFrameInfoType.Transfer)
            return FrameInfo

        @Core.DEB_MEMBER_FUNCT
        def registerFrameCallback(self,frame_cb) :
            self.__comm().registerFrameCallback(frame_cb)
            
        @Core.DEB_MEMBER_FUNCT
	def unregisterFrameCallback(self,frame_cb) :
            self.__comm().unregisterFrameCallback(frame_cb)


