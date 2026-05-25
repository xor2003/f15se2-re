;	Static Name Aliases
;
	TITLE   3DPLANES.C
	.286p
	.287
INCLUDELIB	MLIBCA
$3DPLANES_TEXT	SEGMENT  WORD PUBLIC 'CODE'
$3DPLANES_TEXT	ENDS
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
PUBLIC  _LIGHTS
PUBLIC  _PLANEDETAIL
PUBLIC  _WingRot
PUBLIC  _HookDown
PUBLIC  _HookRot
PUBLIC  _slposx
PUBLIC  _slposy
PUBLIC  _pflashtbl
EXTRN	_Stack3DObject:FAR
EXTRN	_abs:FAR
EXTRN	_labs:FAR
EXTRN	_ViewX:DWORD
EXTRN	_ViewY:DWORD
EXTRN	_ViewZ:WORD
_BSS      SEGMENT
COMM NEAR	_PlaneAnimVals:	 2:	 32
COMM NEAR	_ntmp:	 1:	 10
_BSS      ENDS
_DATA      SEGMENT
_LIGHTS	DW	00H
_PLANEDETAIL	DW	02H
_WingRot	DW	02220H
_HookDown	DW	00H
_HookRot	DW	00H
_slposx	DW	00H
_slposy	DW	00H
_pflashtbl	DW	0fbfbH
	DW	09292H
	DW	09393H
	DW	09292H
_DATA      ENDS
$3DPLANES_TEXT      SEGMENT
	ASSUME	CS: $3DPLANES_TEXT
; Line 1
; Line 11
; Line 12
; Line 13
; Line 19
; Line 14
; Line 15
; Line 16
; Line 17
; Line 18
; Line 19
; Line 20
; Line 21
; Line 22
; Line 86
	PUBLIC	_Do3dObject
_Do3dObject	PROC FAR
	enter	10,0
;	dz = -10
;	t1 = -6
;	t2 = -10
;	register cx = SCL
;	Obj = 6
;	OX = 8
;	OY = 12
;	OZ = 16
;	ID = 18
;	TYPE = 20
;	dx = -4
;	dy = -8
; Line 95
	mov	ax,WORD PTR [bp+8]	;OX
	mov	dx,WORD PTR [bp+10]
	sub	ax,WORD PTR _ViewX
	sbb	dx,WORD PTR _ViewX+2
	mov	WORD PTR [bp-4],ax	;dx
	mov	WORD PTR [bp-2],dx
; Line 96
	mov	ax,WORD PTR _ViewY
	mov	dx,WORD PTR _ViewY+2
	add	ax,WORD PTR [bp+12]	;OY
	adc	dx,WORD PTR [bp+14]
	sub	ax,0
	sbb	dx,16
	mov	WORD PTR [bp-8],ax	;dy
	mov	WORD PTR [bp-6],dx	;t1
; Line 97
	mov	ax,WORD PTR [bp+16]	;OZ
	sub	ax,WORD PTR _ViewZ
	mov	WORD PTR [bp-10],ax	;dz
; Line 99
	push	ax
	call	FAR PTR _abs
	pop	bx
	cmp	ax,16382
	jle	$I1284
$L20002:
	mov	ax,1
	leave	
	ret	
; Line 102
$I1284:
; Line 103
	push	WORD PTR [bp-6]	;t1
	push	WORD PTR [bp-8]	;dy
	call	FAR PTR _labs
	pop	bx
	pop	bx
	or	dx,dx
	jl	$I1285
	jg	$L20002
	cmp	ax,16383
	ja	$L20002
; Line 104
$I1285:
; Line 105
	push	WORD PTR [bp-2]
	push	WORD PTR [bp-4]	;dx
	call	FAR PTR _labs
	pop	bx
	pop	bx
	or	dx,dx
	jl	$I1286
	jg	$L20002
	cmp	ax,16383
	ja	$L20002
; Line 108
$I1286:
	mov	ax,WORD PTR [bp+20]	;TYPE
; Line 134
	cmp	ax,90
	je	$SC1297
	ja	$SC1297
	sub	al,30
	je	$SC1296
	sub	al,10
	je	$SC1296
	sub	al,10
	je	$SC1294
	sub	al,5
	jl	$SC1297
	dec	al
	jle	$SC1294
	sub	al,4
	je	$SC1296
	sub	al,10
; Line 131
	jmp	SHORT $SC1297
; Line 109
$SC1296:
; Line 126
	mov	cx,40
; Line 127
	jmp	SHORT $SB1288
; Line 121
$SC1294:
; Line 119
	mov	cx,30
; Line 120
	jmp	SHORT $SB1288
$SC1297:
; Line 129
	mov	cx,4
; Line 134
$SB1288:
; Line 135
	push	WORD PTR [bp+20]	;TYPE
	push	cx
	push	WORD PTR [bp+18]	;ID
	push	WORD PTR [bp-8]	;dy
	push	WORD PTR [bp-10]	;dz
	push	WORD PTR [bp-4]	;dx
	push	WORD PTR [bp+6]	;Obj
	call	FAR PTR _Stack3DObject
; Line 137
	leave	
	ret	

_Do3dObject	ENDP
$3DPLANES_TEXT	ENDS
END
