# Type of System
XPAD_31       = 0
XPAD_32       = 1

# Gate Mode
INTERN_GATE   = 0x0
EXTERN_GATE   = 0x1
TRIGGER_IN    = 0xA

# Internal Gate Unit
MICROSEC_GATE = 0x1
MILLISEC_GATE = 0x2
SECONDS_GATE  = 0x3

IMG, CONFIG = range(2)
B2,  B4     = range(2)

# Chip Registers Code XPAD31
CMOS_DSBL_V31  = 0x01
AMP_TP_V31     = 0x32
ITHH_V31       = 0x33
VADJ_V31       = 0x35
VREF_V31       = 0x36
IMFP_V31       = 0x37
IOTA_V31       = 0x38
IPRE_V31       = 0x3B
ITHL_V31       = 0x3C
ITUNE_V31      = 0x41
IBUFFER_V31    = 0x42 

# Chip Registers Code XPAD32
CMOS_DSBL_V32  = 0x01
AMP_TP_V32     = 0x1F
ITHH_V32       = 0x33
VADJ_V32       = 0x35
VREF_V32       = 0x36
IMFP_V32       = 0x3b
IOTA_V32       = 0x3c
IPRE_V32       = 0x3d
ITHL_V32       = 0x3e
ITUNE_V32      = 0x3f
IBUFFER_V32    = 0x40
