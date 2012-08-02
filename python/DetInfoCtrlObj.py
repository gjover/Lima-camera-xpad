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
import os
from Lima import Core

class DetInfoCtrlObj(Core.HwDetInfoCtrlObj) :
    Core.DEB_CLASS(Core.DebModCamera, "DetInfoCtrlObj")
    
    def __init__(self) :
        Core.HwDetInfoCtrlObj.__init__(self)

        #Variables
        self.__name = 'imXPad,S140'
        self.__width  = 560
        self.__height = 240
        self.__ImgType = Core.Bpp16

    def init(self) :
        pass
        
    @Core.DEB_MEMBER_FUNCT
    def getMaxImageSize(self) :
        return Core.Size(self.__width,self.__height)

    @Core.DEB_MEMBER_FUNCT
    def getDetectorImageSize(self) :
        return self.getMaxImageSize()
    
    @Core.DEB_MEMBER_FUNCT
    def getDefImageType(self) :
        return Core.Bpp16

    @Core.DEB_MEMBER_FUNCT
    def getCurrImageType(self) :
        return self.__ImgType

    @Core.DEB_MEMBER_FUNCT
    def setCurrImageType(self,ImgType) :
        if ImgType == Core.Bpp16 or ImgType == Core.Bpp32:
            self.__ImgType = ImgType
        else :
            raise Core.Exception(Core.Hardware,Core.NotSupported)
     
    @Core.DEB_MEMBER_FUNCT
    def getPixelSize(self) :
        return 130e-6

    @Core.DEB_MEMBER_FUNCT
    def getDetectorType(self) :
        return 'imXPad'

    @Core.DEB_MEMBER_FUNCT
    def getDetectorModel(self):
	if self.__name :
           return self.__name.split(',')[0].split()[-1]
	else:
	   return "imXPad unknown"


    ##@brief image size won't change so no callback
    #@Core.DEB_MEMBER_FUNCT
    def registerMaxImageSizeCallback(self,cb) :
        pass

    ##@brief image size won't change so no callback
    #@Core.DEB_MEMBER_FUNCT
    def unregisterMaxImageSizeCallback(self,cb) :
        pass

    @Core.DEB_MEMBER_FUNCT
    def get_min_exposition_time(self):
        return 4e-6
    
    ##@todo don't know realy what is the maximum exposure time
    #for now set to a high value 1 hour
    @Core.DEB_MEMBER_FUNCT
    def get_max_exposition_time(self) :
        return 3600

    #@Core.DEB_MEMBER_FUNCT
    def get_min_latency(self) :
	return 0.005

    ##@todo don't know
    #@see get_max_exposition_time
    @Core.DEB_MEMBER_FUNCT
    def get_max_latency(self):
        return 2**31
    
