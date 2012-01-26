//###########################################################################
// This file is part of LImA, a Library for Image Acquisition
//
// Copyright (C) : 2009-2011
// European Synchrotron Radiation Facility
// BP 220, Grenoble 38043
// FRANCE
//
// This is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 3 of the License, or
// (at your option) any later version.
//
// This software is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, see <http://www.gnu.org/licenses/>.
//###########################################################################
#ifndef XPADINTERFACE_H
#define XPADINTERFACE_H

#include "HwInterface.h"
#include "XpadCamera.h"

using namespace lima;
using namespace lima::Xpad;
using namespace std;

namespace lima
{
namespace Xpad
{
/*******************************************************************
 * \class DetInfoCtrlObj
 * \brief Control object providing Xpad detector info interface
 *******************************************************************/
class DetInfoCtrlObj : public HwDetInfoCtrlObj
{
	DEB_CLASS_NAMESPC(DebModCamera, "DetInfoCtrlObj", "Xpad");

 public:
	DetInfoCtrlObj(Camera& cam);
	virtual ~DetInfoCtrlObj();

	virtual void getMaxImageSize(Size& max_image_size);
	virtual void getDetectorImageSize(Size& det_image_size);

	virtual void getDefImageType(ImageType& def_image_type);
	virtual void getCurrImageType(ImageType& curr_image_type);
	virtual void setCurrImageType(ImageType  curr_image_type);

	virtual void getPixelSize(double& pixel_size);
	virtual void getDetectorType(std::string& det_type);
	virtual void getDetectorModel(std::string& det_model);

	virtual void registerMaxImageSizeCallback(HwMaxImageSizeCallback& cb);
	virtual void unregisterMaxImageSizeCallback(HwMaxImageSizeCallback& cb);

 private:
	Camera& m_cam;
};


/*******************************************************************
 * \class BufferCtrlObj
 * \brief Control object providing Xpad buffering interface
 *******************************************************************/
class BufferCtrlObj : public HwBufferCtrlObj
{
	DEB_CLASS_NAMESPC(DebModCamera, "BufferCtrlObj", "Xpad");

 public:
	BufferCtrlObj(Camera& simu);
	virtual ~BufferCtrlObj();

	virtual void setFrameDim(const FrameDim& frame_dim);
	virtual void getFrameDim(      FrameDim& frame_dim);

	virtual void setNbBuffers(int  nb_buffers);
	virtual void getNbBuffers(int& nb_buffers);

	virtual void setNbConcatFrames(int  nb_concat_frames);
	virtual void getNbConcatFrames(int& nb_concat_frames);

	virtual void getMaxNbBuffers(int& max_nb_buffers);

	virtual void *getBufferPtr(int buffer_nb, int concat_frame_nb = 0);
	virtual void *getFramePtr(int acq_frame_nb);

	virtual void getStartTimestamp(Timestamp& start_ts);
	virtual void getFrameInfo(int acq_frame_nb, HwFrameInfoType& info);

	virtual void registerFrameCallback(HwFrameCallback& frame_cb);
	virtual void unregisterFrameCallback(HwFrameCallback& frame_cb);

 private:
	BufferCtrlMgr& m_buffer_mgr;
};

/*******************************************************************
 * \class SyncCtrlObj
 * \brief Control object providing Xpad synchronization interface
 *******************************************************************/
class SyncCtrlObj : public HwSyncCtrlObj
{
    DEB_CLASS_NAMESPC(DebModCamera, "SyncCtrlObj", "Xpad");

  public:
	SyncCtrlObj(Camera& cam);
    virtual ~SyncCtrlObj();
	
	virtual bool checkTrigMode(TrigMode trig_mode);
    virtual void setTrigMode(TrigMode  trig_mode);
    virtual void getTrigMode(TrigMode& trig_mode);

    virtual void setExpTime(double  exp_time);
    virtual void getExpTime(double& exp_time);

    virtual void setLatTime(double  lat_time){}//- Not supported by Xpad
    virtual void getLatTime(double& lat_time){}//- Not supported by Xpad

    virtual void setNbHwFrames(int  nb_frames);
    virtual void getNbHwFrames(int& nb_frames);

    virtual void getValidRanges(ValidRangesType& valid_ranges);

  private:
    Camera& m_cam;
};

/*******************************************************************
 * \class Interface
 * \brief Xpad hardware interface
 *******************************************************************/
class Interface : public HwInterface
{
	DEB_CLASS_NAMESPC(DebModCamera, "Interface", "Xpad");

 public:
	Interface(Camera& cam);
	virtual ~Interface();

	//- From HwInterface
	virtual void 	getCapList(CapList&) const;
	virtual void	reset(ResetLevel reset_level);
	virtual void 	prepareAcq();
	virtual void 	startAcq();
	virtual void 	stopAcq();
	virtual void 	getStatus(StatusType& status);
	virtual int 	getNbHwAcquiredFrames();

	//- Xpad specific
	//! Set all the config G
	void setAllConfigG(const vector<long>& allConfigG)
		{m_cam.setAllConfigG(allConfigG);}
	//! Set the F parameters
	void setFParameters(unsigned deadtime, unsigned init,
									unsigned shutter, unsigned ovf,    unsigned mode,
									unsigned n,       unsigned p,
									unsigned GP1,     unsigned GP2,    unsigned GP3,      unsigned GP4);
	//!	set the Acquisition type between 16 or 32 bit, and Fast or Slow
	void setAcquisitionType(short acq_type);
	//!	Load of flat config of value: flat_value (on each pixel)
	void loadFlatConfig(unsigned flat_value);
	//! Load all the config G with predefined values (on each chip)
	void loadAllConfigG();
	//! Load a wanted config G with a wanted value
	void loadConfigG(const vector<unsigned long>& reg_and_value);
	//! load a known value to the pixel counters
	void loadAutoTest(unsigned known_value)
		{m_cam.loadAutoTest(known_value);}
	//! Get the DACL values
	vector<uint16_t> getDacl()
		{return m_cam.getDacl();}
	//! Save and load Dacl
	void saveAndloadDacl(uint16_t* all_dacls)
		{m_cam.saveAndloadDacl(all_dacls);}
	

 private:
	Camera&				m_cam;
	CapList 			m_cap_list;
	DetInfoCtrlObj	m_det_info;
	BufferCtrlObj	m_buffer;
	SyncCtrlObj		m_sync;

};
} // namespace xpad
} // namespace lima

#endif // XPADINTERFACE_H
