	SECTION copperlist,DATA,CHIP

	XDEF	_CopperList
	XDEF	_CopFETCHMODE
	XDEF	_CopBPLCON0
	XDEF	_CopBPLCON1
	XDEF	_CopBPLCON3
	XDEF	_CopBPLMODA
	XDEF	_CopBPLMODB
	XDEF	_CopDIWSTART
	XDEF	_CopDIWSTOP
	XDEF	_CopDDFSTART
	XDEF	_CopDDFSTOP
	XDEF	_CopPLANE1H
	XDEF	_CopPLANE1L
	XDEF	_CopPLANE2H
	XDEF	_CopPLANE2L
	XDEF	_CopPLANE3H
	XDEF	_CopPLANE3L
	XDEF	_CopPLANE4H
	XDEF	_CopPLANE4L
	XDEF	_CopPLANE5H
	XDEF	_CopPLANE5L
	XDEF	_CopPLANE6H
	XDEF	_CopPLANE6L
	XDEF	_CopPLANE7H
	XDEF	_CopPLANE7L
	XDEF	_CopPLANE8H
	XDEF	_CopPLANE8L

_CopperList:
	dc.w	$180,0

_CopFETCHMODE:
	dc.w	$1FC,0

_CopBPLCON0:
	dc.w	$100,0

_CopBPLCON1:
	dc.w	$102,0

_CopBPLCON3:
	dc.w	$106,0

_CopBPLMODA:
	dc.w	$108,0
	
_CopBPLMODB:
	dc.w	$10A,0
	
_CopDIWSTART:
	dc.w	$8e,0
	
_CopDIWSTOP:
	dc.w	$90,0
	
_CopDDFSTART:
	dc.w	$92,0
	
_CopDDFSTOP:
	dc.w	$94,0

_CopPLANE1H:
	dc.w	$e0,0

_CopPLANE1L:
	dc.w	$e2,0

_CopPLANE2H:
	dc.w	$e4,0

_CopPLANE2L:
	dc.w	$e6,0

_CopPLANE3H:
	dc.w	$e8,0

_CopPLANE3L:
	dc.w	$ea,0

_CopPLANE4H:
	dc.w	$ec,0

_CopPLANE4L:
	dc.w	$ee,0

_CopPLANE5H:
	dc.w	$f0,0

_CopPLANE5L:
	dc.w	$f2,0

_CopPLANE6H:
	dc.w	$f4,0

_CopPLANE6L:
	dc.w	$f6,0

_CopPLANE7H:
	dc.w	$f8,0

_CopPLANE7L:
	dc.w	$fa,0

_CopPLANE8H:
	dc.w	$fc,0

_CopPLANE8L:
	dc.w	$fe,0

	dc.w	-1,-2

	END

