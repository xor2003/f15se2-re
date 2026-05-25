;	Static Name Aliases
;
;	$S643_JstarTimer	EQU	JstarTimer
;	$S644_JstarX	EQU	JstarX
	TITLE   AWACS.C
	.8087
INCLUDELIB	MLIBCE
AWACS_TEXT	SEGMENT  WORD PUBLIC 'CODE'
AWACS_TEXT	ENDS
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
PUBLIC  _LastCall
EXTRN	_LocationPicture:FAR
EXTRN	_Dist2D:FAR
EXTRN	_ARCTAN:FAR
EXTRN	_strcat:FAR
EXTRN	_itoa:FAR
EXTRN	_Speech:FAR
_BSS      SEGMENT
COMM NEAR	_ntmp:	 1:	 10
_BSS      ENDS
EXTRN	_Txt:BYTE
EXTRN	_Diff:WORD
EXTRN	_Gtime:WORD
EXTRN	_NPLANES:WORD
EXTRN	_ps:BYTE
EXTRN	_Px:WORD
EXTRN	_Py:WORD
_DATA      SEGMENT
_LastCall	DW	0ff10H
_DATA      ENDS
_BSS      SEGMENT
$S643_JstarTimer	DW 01H DUP (?)
$S644_JstarX	DW 01H DUP (?)
_BSS      ENDS
AWACS_TEXT      SEGMENT
	ASSUME	CS: AWACS_TEXT
; Line 1
; Line 19
; Line 2
; Line 3
; Line 4
; Line 5
; Line 6
; Line 7
; Line 8
; Line 27
	PUBLIC	_AwacsPicture
_AwacsPicture	PROC FAR
	push	bp
	mov	bp,sp
	sub	sp,52
;	psi = -42
;	Mini = -46
;	i = -28
;	dx = -40
;	dy = -44
;	dist = -14
;	angl = -12
;	MinDist = -26
;	MinAngl = -22
;	eyex = -30
;	eyey = -38
;	eyedist = -24
;	bogeyi = -52
;	cnt = -16
;	ptemp = -20
;	carrx = -2
;	carry = -6
;	carrangle = -50
;	carrrelangle = -10
;	carrdist = -36
;	do_id = -48
;	is_target = -8
;	waynum = -4
;	bogey_org_num = -34
;	whatsrc = -32
; Line 35
	sub	ax,ax
	mov	WORD PTR [bp-48],ax	;do_id
	mov	WORD PTR [bp-8],ax	;is_target
; Line 39
	mov	WORD PTR [bp-26],11250	;MinDist
; Line 40
	mov	ax,WORD PTR _Diff
	inc	ax
	mov	cx,60
	imul	cx
	mov	cx,WORD PTR _Gtime
	sub	cx,WORD PTR _LastCall
	cmp	cx,ax
	jge	$I678
; Line 41
	mov	ax,1
	push	ax
	sub	ax,ax
	push	ax
	mov	cx,11250
	push	cx
	push	ax
	push	ax
	push	ax
	call	FAR PTR _LocationPicture
	add	sp,12
; Line 42
	jmp	$I680
	nop	
$I678:
; Line 43
	mov	ax,WORD PTR _Gtime
	mov	WORD PTR _LastCall,ax
; Line 45
	mov	WORD PTR [bp-52],-999	;bogeyi
; Line 46
	mov	WORD PTR [bp-28],0	;i
	mov	WORD PTR [bp-42],OFFSET _ps	;psi
	jmp	SHORT $F681
	nop	
$FC682:
	inc	WORD PTR [bp-28]	;i
	add	WORD PTR [bp-42],40	;psi
$F681:
	mov	ax,WORD PTR [bp-28]	;i
	cmp	WORD PTR _NPLANES,ax
	jle	$FB683
; Line 47
	mov	bx,WORD PTR [bp-42]	;psi
	mov	cx,WORD PTR [bx+24]
	mov	dx,cx
	test	cl,2
	je	$I687
	cmp	WORD PTR [bx+26],0
	je	$I687
	test	dx,1056
	jne	$I687
; Line 48
	mov	cx,WORD PTR [bx+2]
	sub	cx,WORD PTR _Px
	mov	WORD PTR [bp-40],cx	;dx
; Line 49
	mov	dx,WORD PTR [bx+4]
	sub	dx,WORD PTR _Py
	mov	WORD PTR [bp-44],dx	;dy
; Line 51
	push	dx
	push	cx
	call	FAR PTR _Dist2D
	add	sp,4
	mov	WORD PTR [bp-14],ax	;dist
; Line 52
	mov	ax,WORD PTR [bp-44]	;dy
	neg	ax
	push	ax
	push	WORD PTR [bp-40]	;dx
	call	FAR PTR _ARCTAN
	add	sp,4
	mov	WORD PTR [bp-12],ax	;angl
; Line 54
	mov	ax,WORD PTR [bp-14]	;dist
	cmp	WORD PTR [bp-26],ax	;MinDist
	jle	$I687
; Line 55
	mov	cx,WORD PTR [bp-28]	;i
	mov	WORD PTR [bp-52],cx	;bogeyi
; Line 56
	mov	WORD PTR [bp-26],ax	;MinDist
; Line 57
	mov	ax,WORD PTR [bp-42]	;psi
	mov	WORD PTR [bp-46],ax	;Mini
; Line 58
	mov	ax,WORD PTR [bp-12]	;angl
	mov	WORD PTR [bp-22],ax	;MinAngl
; Line 59
; Line 60
$I687:
; Line 61
	jmp	SHORT $FC682
	nop	
$FB683:
; Line 62
	sub	ax,ax
	push	ax
	push	WORD PTR [bp-52]	;bogeyi
	push	WORD PTR [bp-26]	;MinDist
	push	WORD PTR [bp-22]	;MinAngl
	push	ax
	push	ax
	call	FAR PTR _LocationPicture
	add	sp,12
; Line 63
$I680:
; Line 64
	sub	ax,ax
	mov	sp,bp
	pop	bp
	ret	
; Line 65
	mov	sp,bp
	pop	bp
	ret	

_AwacsPicture	ENDP
; Line 70
	PUBLIC	_NSpeech
_NSpeech	PROC FAR
	push	bp
	mov	bp,sp
	sub	sp,12
	push	si
;	s = -10
;	i = -12
;	isawac = 8
;	num = 6
; Line 74
	mov	ax,10
	push	ax
	lea	ax,WORD PTR [bp-10]	;s
	push	ax
	push	WORD PTR [bp+6]	;num
	call	FAR PTR _itoa
	add	sp,6
; Line 75
	lea	ax,WORD PTR [bp-10]	;s
	push	ax
	mov	ax,OFFSET _Txt
	push	ax
	call	FAR PTR _strcat
	add	sp,4
; Line 77
	mov	WORD PTR [bp-12],0	;i
	jmp	SHORT $F695
	nop	
$FC696:
	inc	WORD PTR [bp-12]	;i
$F695:
	mov	si,WORD PTR [bp-12]	;i
	cmp	BYTE PTR [bp-10][si],0
	je	$FB697
; Line 78
	cmp	WORD PTR [bp+8],0	;isawac
	je	$I698
; Line 79
	mov	al,BYTE PTR [bp-10][si]
	cbw	
	inc	ax
	push	ax
	call	FAR PTR _Speech
	add	sp,2
; Line 80
	jmp	SHORT $I700
$I698:
; Line 81
	mov	al,BYTE PTR [bp-10][si]
	cbw	
	sub	ax,24
	push	ax
	call	FAR PTR _Speech
	add	sp,2
$I700:
; Line 82
	jmp	SHORT $FC696
$FB697:
; Line 83
	pop	si
	mov	sp,bp
	pop	bp
	ret	
	nop	

_NSpeech	ENDP
AWACS_TEXT	ENDS
END
