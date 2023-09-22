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
--CTR_phoneme_GK

vertexOffsetArray=#(0x4a53ec,0x4a5f20,0x4a75a8,0x4a9a40)
vertexCountArray=#(0x1de,0x3c1,0x619,0xc7)

morphPosScale = [0.00010337309504393488, -0.019466280937194824]
morphNrmScale = [0.007843137718737125, -1.0]

clearlistener()

for x=1 to vertexOffsetArray.count do (
	fseek f vertexOffsetArray[x] #seek_set
	for y=1 to vertexCountArray[x] do (
		vx = morphPosScale[1] * (readbyte f #unsigned) + morphPosScale[2]
		vy = morphPosScale[1] * (readbyte f #unsigned) + morphPosScale[2]
		vz = morphPosScale[1] * (readbyte f #unsigned) + morphPosScale[2]
		
		nx = morphNrmScale[1] * (readbyte f #unsigned) + morphNrmScale[2]
		ny = morphNrmScale[1] * (readbyte f #unsigned) + morphNrmScale[2]
		nz = morphNrmScale[1] * (readbyte f #unsigned) + morphNrmScale[2]
		
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
	[ 554 ,  2 ],
[ 1029 ,  7 ],
[ 1145 ,  32 ],
[ 1177 ,  14 ],
[ 1193 ,  11 ],
[ 1256 ,  5 ],
[ 1361 ,  8 ],
[ 1383 ,  32 ],
[ 1415 ,  5 ],
[ 1435 ,  2 ],
[ 1875 ,  2 ],
[ 1891 ,  14 ],
[ 2216 ,  32 ],
[ 2248 ,  32 ],
[ 2280 ,  32 ],
[ 2312 ,  32 ],
[ 2344 ,  32 ],
[ 2376 ,  32 ],
[ 2408 ,  32 ],
[ 2440 ,  32 ],
[ 2472 ,  32 ],
[ 2504 ,  32 ],
[ 2536 ,  24 ],
[ 2560 ,  32 ],
[ 2592 ,  32 ],
[ 2624 ,  32 ],
[ 2656 ,  32 ],
[ 2688 ,  32 ],
[ 2720 ,  32 ],
[ 2752 ,  32 ],
[ 2784 ,  32 ],
[ 2816 ,  32 ],
[ 2848 ,  32 ],
[ 2880 ,  32 ],
[ 2912 ,  32 ],
[ 2944 ,  32 ],
[ 2976 ,  2 ],
[ 2987 ,  1 ],
[ 3004 ,  10 ],
[ 3063 ,  8 ],
[ 3080 ,  8 ],
[ 3093 ,  32 ],
[ 3125 ,  32 ],
[ 3157 ,  32 ],
[ 3189 ,  32 ],
[ 3221 ,  23 ],
[ 3251 ,  32 ],
[ 3283 ,  9 ],
[ 3301 ,  3 ],
[ 3336 ,  3 ],
[ 3379 ,  1 ],
[ 3381 ,  3 ],
[ 3744 ,  1 ],
[ 3797 ,  1 ],
[ 3799 ,  8 ],
[ 3811 ,  1 ],
[ 3813 ,  12 ],
[ 3860 ,  2 ],
[ 3897 ,  4 ],
[ 4121 ,  23 ],
[ 4357 ,  1 ],
[ 4359 ,  1 ],
[ 4414 ,  7 ],
[ 4542 ,  24 ],
[ 4582 ,  19 ],
[ 4621 ,  32 ],
[ 4653 ,  7 ],
[ 4775 ,  32 ],
[ 4807 ,  26 ],
[ 4844 ,  32 ],
[ 4876 ,  31 ],
[ 5070 ,  32 ],
[ 5102 ,  18 ],
[ 5120 ,  18 ],
[ 5306 ,  7 ],
[ 5314 ,  1 ],
[ 5374 ,  10 ],
[ 5444 ,  6 ],
[ 5451 ,  1 ],
[ 5644 ,  11 ],
[ 5666 ,  17 ],
[ 5703 ,  1 ],
[ 5705 ,  4 ],
[ 5714 ,  32 ],
[ 5746 ,  32 ],
[ 5778 ,  32 ],
[ 5810 ,  32 ],
[ 5842 ,  12 ],
[ 5857 ,  3 ],
[ 5887 ,  3 ],
[ 5914 ,  9 ],
[ 5924 ,  27 ],
[ 5989 ,  16 ],
[ 6054 ,  4 ],
[ 6059 ,  30 ],
[ 6093 ,  7 ],
[ 6101 ,  4 ],
[ 6126 ,  4 ],
[ 6201 ,  32 ],
[ 6233 ,  5 ],
[ 6331 ,  32 ],
[ 6363 ,  32 ],
[ 6395 ,  32 ],
[ 6427 ,  32 ],
[ 6459 ,  32 ],
[ 6491 ,  32 ],
[ 6523 ,  25 ],
[ 6576 ,  3 ],
[ 6593 ,  7 ],
[ 6601 ,  21 ],
[ 6623 ,  32 ],
[ 6655 ,  6 ],
[ 6668 ,  32 ],
[ 6700 ,  32 ],
[ 6732 ,  32 ],
[ 6764 ,  32 ],
[ 6796 ,  32 ],
[ 6828 ,  32 ],
[ 6860 ,  32 ],
[ 6892 ,  7 ],
[ 6905 ,  32 ],
[ 6937 ,  32 ],
[ 6969 ,  32 ],
[ 7001 ,  32 ],
[ 7033 ,  32 ],
[ 7065 ,  32 ],
[ 7097 ,  32 ],
[ 7129 ,  32 ],
[ 7161 ,  32 ],
[ 7193 ,  32 ],
[ 7225 ,  32 ],
[ 7257 ,  32 ],
[ 7289 ,  32 ],
[ 7321 ,  32 ],
[ 7353 ,  32 ],
[ 7385 ,  32 ],
[ 7417 ,  32 ],
[ 7449 ,  32 ],
[ 7481 ,  32 ],
[ 7513 ,  32 ],
[ 7545 ,  32 ],
[ 7577 ,  12 ],
[ 7695 ,  1 ],
[ 7703 ,  29 ],
[ 7733 ,  2 ],
[ 7736 ,  32 ],
[ 7768 ,  31 ],
[ 8171 ,  8 ],
[ 8181 ,  13 ],
[ 8206 ,  6 ],
[ 8346 ,  2 ],
[ 8355 ,  2 ],
[ 8382 ,  2 ],
[ 8511 ,  21 ],
[ 8601 ,  6 ],
[ 8726 ,  11 ],
[ 8739 ,  3 ],
[ 9337 ,  30 ]
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

