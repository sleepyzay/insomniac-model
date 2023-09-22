Vert_Array=#()
UV_Array=#()
Face_Array=#()
delete $*

fname = @"D:\scripts\blender\ra model\hero_ratchet\hero_ratchet.model"
f = fopen fname "rb"   --open file in read only format

fseek f 0xe67ad0 #seek_set
for x=1 to 0x48c6 do (
	vx = readshort f
	vy = readshort f
	vz = readshort f
	vw =readshort f
	normals = readlong f
	tu = readshort f / 4096.0
	tv = readshort f / 4096.0
	
	append Vert_Array([vx,vy,vz] / 4096.0)
	append UV_Array([tu,1-tv,0])
)

fseek f 0xac7872 #seek_set
for x=1 to 0x1a490 / 3 do (
	fa = readshort f #unsigned + 1
	fb = readshort f #unsigned + 1
	fc = readshort f #unsigned + 1
	
	append Face_Array[fa,fb,fc]
)

msh = mesh vertices:Vert_array faces:Face_Array
msh.wirecolor = white
select msh

MorphVertArray = #()
--CTR_phoneme_S

offsetArray=#(0x74e530,0x74efdc,0x74f540,0x74f864)
countArray=#(0x1c7,0xe6,0x86,0x1)

q = [0.0001707268093014136, -0.03521227836608887, 0.007843137718737125, -1.0]


morphPosMax = q[1]
morphPosMin = q[2]
morphNrmMax = q[3]
morphNrmMin = q[4]

min = 999
max = -999
clearlistener()

-- v1 = 0
-- v2 = 0
-- v3 = 0

for x=1 to offsetArray.count do (
	fseek f offsetArray[x] #seek_set
	for y=1 to countArray[x] do (
-- 		vx = readbyte f #unsigned
-- 		vy = readbyte f #unsigned
-- 		vz = readbyte f #unsigned
-- 		
-- 		if v1 < vx do v1 = vx
-- 		if v2 < vy do v2 = vy
-- 		if v3 < vz do v3 = vz
-- 		
		vx = morphPosMin + ((readbyte f #unsigned) * (morphPosMax - morphPosMin) / (208.0))
		vy = morphPosMin + ((readbyte f #unsigned) * (morphPosMax - morphPosMin) / (208.0))
		vz = morphPosMin + ((readbyte f #unsigned) * (morphPosMax - morphPosMin) / (208.0))
		
		nx = morphNrmMin + ((readbyte f #unsigned) * (morphNrmMax - morphNrmMin) / (255.0))
		ny = morphNrmMin + ((readbyte f #unsigned) * (morphNrmMax - morphNrmMin) / (255.0))
		nz = morphNrmMin + ((readbyte f #unsigned) * (morphNrmMax - morphNrmMin) / (255.0))
		
		append MorphVertArray([vx,vy,vz])
		if y==1 do print [vx,vy,vz]
	)
)
-- print v1
-- print v2
-- print v3
-- print(150 / 4096.0)
-- print (min)
-- print (max)

-- print(bit.intashex(ftell f as integer))
-- print(bit.intashex(MorphVertArray.count))


vertexSelectionArray = #(
	[ 178 ,  7 ],
	[ 186 ,  1 ],
	[ 188 ,  4 ],
	[ 199 ,  1 ],
	[ 201 ,  8 ],
	[ 210 ,  1 ],
	[ 600 ,  5 ],
	[ 625 ,  5 ],
	[ 657 ,  2 ],
	[ 661 ,  3 ],
	[ 723 ,  12 ],
	[ 806 ,  32 ],
	[ 838 ,  16 ],
	[ 855 ,  1 ],
	[ 857 ,  1 ],
	[ 867 ,  19 ],
	[ 1051 ,  24 ],
	[ 1086 ,  32 ],
	[ 1118 ,  10 ],
	[ 1140 ,  5 ],
	[ 1221 ,  8 ],
	[ 1291 ,  3 ],
	[ 1941 ,  17 ],
	[ 1963 ,  32 ],
	[ 1995 ,  32 ],
	[ 2027 ,  32 ],
	[ 2059 ,  32 ],
	[ 2091 ,  32 ],
	[ 2123 ,  32 ],
	[ 2155 ,  32 ],
	[ 2187 ,  3 ],
	[ 2192 ,  11 ],
	[ 3502 ,  5 ],
	[ 3509 ,  1 ],
	[ 3523 ,  17 ],
	[ 3544 ,  32 ],
	[ 3576 ,  11 ],
	[ 3590 ,  9 ],
	[ 3600 ,  1 ],
	[ 3616 ,  26 ],
	[ 3643 ,  32 ],
	[ 3675 ,  32 ],
	[ 3707 ,  22 ],
	[ 3750 ,  32 ],
	[ 3782 ,  9 ],
	[ 4839 ,  1 ],
	[ 5427 ,  2 ],
	[ 5465 ,  2 ],
	[ 5471 ,  1 ],
	[ 5498 ,  4 ],
	[ 5506 ,  1 ],
	[ 5631 ,  1 ],
	[ 6281 ,  32 ],
	[ 6313 ,  18 ],
	[ 7589 ,  16 ],
	[ 7614 ,  28 ],
	[ 7649 ,  25 ],
	[ 7675 ,  4 ],
	[ 7697 ,  1 ]
)

actionMan.executeAction 0 "40839"  -- MAX Script: MAXScript Editor
-- clearlistener()

-- msh = selection[1]
vertexIndex = 0
vertsToSelect = #()
for x=1 to vertexSelectionArray.count  do (	--vertSelectionArray.count 
	vertexIndex = vertexSelectionArray[x][1]
    vertexRange = vertexSelectionArray[x][2]
    vertexEndIndex = (vertexIndex - 1) + vertexRange
	
-- 	format "start: %    range: %   end: %\n" vertexIndex vertexRange vertexEndIndex
	
	for y=vertexIndex to vertexEndIndex do (
		append vertsToSelect (y + 1 as integer)
	)
)

for x=1 to vertsToSelect.count do (
	vertPos = meshOp.getVert msh vertsToSelect[x]
	newVertPos = (vertPos +  MorphVertArray[x] )
	meshop.setvert msh vertsToSelect[x] newVertPos
)
redrawViews()

