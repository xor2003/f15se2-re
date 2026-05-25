//***************************************************************************
// File: 3DPLANES.C
//
// Author: Mike McDonald
//
// Initial code by Sid Meier/Andy Hollis
//
// Description:  Process 3D planes and other single 3D objects
//
//***************************************************************************
#include <dos.h>
#include <stdlib.h>
#include "Library.h"
#include "world.h"
#include "sdata.h"
#include "cockpit.h"
#include "F15defs.h"
#include "sounds.h"
#include "armt.h"
#include "planeai.h"
#include "proto.h"
#include "3dobjdef.h"

extern  RPS     *Rp3D;
extern 	RPS		*RpCRT;

extern  UBYTE   PlaneFlags[];
extern  SWORD   AnimVals[];
extern  int     O[3][3];

extern  int     OurHead,OurRoll,OurPitch;
extern  UWORD   Alt;
extern  long    ViewX,ViewY;
extern  int     ViewZ;
extern  long    PxLng,PyLng;
extern  int     View;
extern  int     sx,sy,sz;
extern  COORD   chuteX,chuteY;
extern  int     chuteZ,chuteDZ;
extern  int     MinAlt;
extern  int     THRUST;
extern  int     Gees;
extern	int		Knots;
extern  int     detected;
extern  int     Firing;
extern	UWORD	*PalPtr3D;
extern  int     LightsOn;
extern	int		DESIGNATED;

extern   int   NOTEXTURE;

extern	int		DeckPlaneScale;
extern 	int		PlaneScale;
extern  UBYTE   mS1n,mS2n;
extern int whichourcarr;
extern int Fticks;

Shift3X3(int *M, int SHFT);


#define	DEG		182

int PlaneAnimVals[32];
int LIGHTS = 0;
int	PLANEDETAIL=2;
int WingRot=(48*DEG);
extern int WingsReady;
extern int PreparePlaneWings;
int HookDown=0;
int HookRot=0;
int slposx=0;
int slposy=0;

extern	int	GFLSH;
int	pflashtbl[4]={251*256+251,146*256+146,147*256+147,146*256+146};

extern struct MissileData far *GetMissilePtr(int MissileNo);
extern struct PlaneData far *GetPlanePtr(int PlaneNo);

extern long labs(long X);

//int Do3dObject(int Obj, long OX, long OY, UWORD OZ, int ID,int TYPE);

//***************************************************************************
int Do3dObject(int Obj, long OX, long OY, UWORD OZ, int ID,int TYPE)
{
    long dx,dy;
    int dz;
	long t1;
	long t2;

	int	SCL;


    dx = OX - ViewX;
    dy = ViewY - (0x100000L-OY);
    dz = OZ - ViewZ;

	if (abs(dz) > 0x3ffe) return (1);


	t1 = labs(dy);
	if (t1>0x3fff) return(1);
	t1 = labs(dx);
	if (t1>0x3fff) return(1);


	switch(TYPE) {
		case PLANES_OBJ:
			SCL=40;
			break;
		case SHADOW_OBJ:
			SCL=40;
			break;
		case MISSILE_OBJ:
			SCL=4;
			break;
		case CHUTE_OBJ:
			SCL=30;
		break;
		case CHAFF_OBJ:
		case FLARE_OBJ:
			SCL=30;
		break;
		case COOLF14_OBJ:
			SCL=40;
			break;
		case REG_BOAT_OBJ:
			SCL=4;
			break;
		default:
			SCL=4;
			break;
		}
	Stack3DObject(Obj, (int) dx, dz, (int) dy, ID, SCL,TYPE);

}
