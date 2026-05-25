;	Static Name Aliases
;
;	$S669_Dx	EQU	Dx
;	$S670_Dy	EQU	Dy
;	$S671_Dz	EQU	Dz
	TITLE   src\3DOBJECT.C
	.286p
	.287
INCLUDELIB	MLIBCA
$3DOBJECT_TEXT	SEGMENT  WORD PUBLIC 'CODE'
$3DOBJECT_TEXT	ENDS
_DATA	SEGMENT  WORD PUBLIC 'DATA'
_DATA	ENDS
CONST	SEGMENT  WORD PUBLIC 'CONST'
CONST	ENDS
_BSS	SEGMENT  WORD PUBLIC 'BSS'
_BSS	ENDS
$$SYMBOLS	SEGMENT  BYTE PUBLIC 'DEBSYM'
$$SYMBOLS	ENDS
$$TYPES	SEGMENT  BYTE PUBLIC 'DEBTYP'
$$TYPES	ENDS
DGROUP	GROUP	CONST, _BSS, _DATA
	ASSUME DS: DGROUP, SS: DGROUP
PUBLIC  _Object
PUBLIC  _OX
PUBLIC  _OY
PUBLIC  _OZ
PUBLIC  _SecondMatrix
PUBLIC  _Dist2Obj
PUBLIC  _Class
PUBLIC  _VX
PUBLIC  _VY
PUBLIC  _VZ
PUBLIC  _SinHead
PUBLIC  _CosHead
PUBLIC  _SinPitch
PUBLIC  _CosPitch
PUBLIC  _SinRoll
PUBLIC  _CosRoll
PUBLIC  _V
PUBLIC  _O
PUBLIC  _C
EXTRN	_SetOvrlyRp:FAR
EXTRN	_MakeRotationMatrix:FAR
EXTRN	_MakeMatHPR:FAR
EXTRN	_NSetViewMat:FAR
EXTRN	_NGXMID:WORD
EXTRN	_NGYMID:WORD
EXTRN	_GRPAGE:WORD
EXTRN	_GRPAGE0:BYTE
_BSS      SEGMENT
COMM NEAR	_ntmp:	 1:	 10
_BSS      ENDS
EXTRN	_NPDEST:DWORD
_BSS      SEGMENT
COMM NEAR	_XEB:	BYTE:	 4
COMM NEAR	_YEB:	BYTE:	 4
COMM NEAR	_ZEB:	BYTE:	 4
_BSS      ENDS
EXTRN	_View:WORD
_BSS      SEGMENT
COMM NEAR	_HCent:	BYTE:	 2
COMM NEAR	_VCent:	BYTE:	 2
COMM NEAR	_AnimVals:	 2:	 32
COMM NEAR	_HitMe:	BYTE:	 2
COMM NEAR	_CRASHED:	BYTE:	 2
_BSS      ENDS
EXTRN	_GXLO:WORD
EXTRN	_GYLO:WORD
EXTRN	_GXHI:WORD
EXTRN	_GYHI:WORD
EXTRN	_GXMID:WORD
EXTRN	_GYMID:WORD
EXTRN	_NGXLO:WORD
EXTRN	_NGYLO:WORD
EXTRN	_NGXHI:WORD
EXTRN	_NGYHI:WORD
_DATA      SEGMENT
_Object	DW	00H
_OX	DW	00H
_OY	DW	00H
_OZ	DW	00H
_SecondMatrix	DW	00H
$S669_Dx	DW	00H
$S670_Dy	DW	00H
$S671_Dz	DW	00H
_Dist2Obj	DW	00H
_Class	DW	00H
_VX	DW	00H
_VY	DW	00H
_VZ	DW	00H
_SinHead	DW	00H
_CosHead	DW	00H
_SinPitch	DW	00H
_CosPitch	DW	00H
_SinRoll	DW	00H
_CosRoll	DW	00H
_V	DW	00H
 	DB	16 DUP(0)

_O	DW	00H
 	DB	16 DUP(0)

_C	DW	00H
 	DB	16 DUP(0)

_DATA      ENDS
$3DOBJECT_TEXT      SEGMENT
	ASSUME	CS: $3DOBJECT_TEXT
; Line 1
; Line 14
; Line 19
; Line 16
; Line 17
; Line 18
; Line 19
; Line 20
; Line 79
	PUBLIC	_SetDrawWindow
_SetDrawWindow	PROC FAR
	push	bp
	mov	bp,sp
	push	si
;	Rp = 6
;	LWidth = -4
;	LHeight = -2
	mov	si,WORD PTR [bp+6]	;Rp
; Line 83
	mov	ax,WORD PTR [si+6]
	inc	ax
	sar	ax,1
	mov	WORD PTR _HCent,ax
; Line 84
	mov	ax,WORD PTR [si+8]
	inc	ax
	sar	ax,1
	mov	WORD PTR _VCent,ax
; Line 86
	cmp	WORD PTR [si+4],0
	jne	$I720
; Line 88
	test	BYTE PTR _View,64
	jne	$I720
; Line 89
	mov	WORD PTR _VCent,56
; Line 94
$I720:
	push	si
	call	FAR PTR _SetOvrlyRp
	pop	bx
; Line 97
	mov	ax,WORD PTR [si+2]
	mov	WORD PTR _GXLO,ax
; Line 98
	mov	ax,WORD PTR [si+4]
	mov	WORD PTR _GYLO,ax
; Line 99
	mov	ax,WORD PTR [si+2]
	add	ax,WORD PTR [si+6]
	mov	WORD PTR _GXHI,ax
; Line 100
	mov	ax,WORD PTR [si+4]
	add	ax,WORD PTR [si+8]
	mov	WORD PTR _GYHI,ax
; Line 101
	mov	ax,WORD PTR [si+2]
	add	ax,WORD PTR _HCent
	mov	WORD PTR _GXMID,ax
; Line 102
	mov	ax,WORD PTR [si+4]
	add	ax,WORD PTR _VCent
	mov	WORD PTR _GYMID,ax
; Line 103
	mov	bx,WORD PTR [si]
	shl	bx,1
	mov	ax,WORD PTR _GRPAGE0[bx]
	mov	WORD PTR _GRPAGE,ax
; Line 104
	mov	ax,WORD PTR _GXLO
	mov	WORD PTR _NGXLO,ax
; Line 105
	mov	ax,WORD PTR _GXHI
	mov	WORD PTR _NGXHI,ax
; Line 106
	mov	ax,WORD PTR _GYLO
	mov	WORD PTR _NGYLO,ax
; Line 107
	mov	ax,WORD PTR _GYHI
	mov	WORD PTR _NGYHI,ax
; Line 108
	mov	ax,WORD PTR _GXMID
	mov	WORD PTR _NGXMID,ax
; Line 109
	mov	ax,WORD PTR _GYMID
	mov	WORD PTR _NGYMID,ax
; Line 111
	mov	ax,WORD PTR _GRPAGE
	mov	WORD PTR _NPDEST+2,ax
; Line 112
	mov	WORD PTR _NPDEST,0
; Line 113
	pop	si
	leave	
	ret	

_SetDrawWindow	ENDP
; Line 117
	PUBLIC	_SetViewRot
_SetViewRot	PROC FAR
	push	bp
	mov	bp,sp
	push	di
	push	si
;	LHead = 6
;	LPitch = 8
;	LRoll = 10
;	Zoom = 12
; Line 118
	mov	ax,WORD PTR [bp+10]	;LRoll
	neg	ax
	push	ax
	mov	ax,WORD PTR [bp+8]	;LPitch
	neg	ax
	push	ax
	mov	cx,WORD PTR [bp+6]	;LHead
	neg	cx
	push	cx
	push	OFFSET DGROUP:_V
	mov	si,ax
	mov	di,cx
	call	FAR PTR _MakeRotationMatrix
	add	sp,8
; Line 119
	push	OFFSET DGROUP:_O
	push	WORD PTR [bp+10]	;LRoll
	push	si
	push	di
	call	FAR PTR _MakeMatHPR
	add	sp,8
; Line 121
	push	WORD PTR [bp+12]	;Zoom
	push	OFFSET DGROUP:_O
	call	FAR PTR _NSetViewMat
	pop	bx
	pop	bx
; Line 122
	pop	si
	pop	di
	leave	
	ret	

_SetViewRot	ENDP
; Line 127
	PUBLIC	_SetViewPos
_SetViewPos	PROC FAR
	push	bp
	mov	bp,sp
;	X = 6
;	Y = 8
;	Z = 10
; Line 128
	mov	ax,WORD PTR [bp+6]	;X
	mov	WORD PTR _VX,ax
; Line 129
	mov	ax,WORD PTR [bp+8]	;Y
	mov	WORD PTR _VY,ax
; Line 130
	mov	ax,WORD PTR [bp+10]	;Z
	mov	WORD PTR _VZ,ax
; Line 131
	leave	
	ret	

_SetViewPos	ENDP
$3DOBJECT_TEXT	ENDS
END
