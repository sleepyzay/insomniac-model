import io
import sys
import math
import struct
import os
import numpy

def tell(file_object, endian = '<'):
	return file_object.tell()
def print_here(file_object, endian = '<'):
	print ("Here at:    {0:x}".format(tell(file_object)))
def print_hex(file_object, endian = '<'):
	print ("{0:x}".format(file_object))
def read_byte(file_object, endian = '<'):
	return struct.unpack(endian + 'B', file_object.read(1))[0]
def read_ushort(file_object, endian = '<'):
	return struct.unpack(endian + "H", file_object.read(2))[0]
def read_short(file_object, endian = '<'):
	return struct.unpack(endian + 'h', file_object.read(2))[0]
def read_uint(file_object, endian = '<'):
	return struct.unpack(endian + 'I', file_object.read(4))[0]
def read_int(file_object, endian = '<'):
	return struct.unpack(endian + 'i', file_object.read(4))[0]
def read_longlong(file_object, endian = '<'):
	return struct.unpack(endian + 'q', file_object.read(8))[0]
def read_ulonglong(file_object, endian = '<'):
	return struct.unpack(endian + 'Q', file_object.read(8))[0]
def read_half(file_object, endian = '<'):
	return struct.unpack(endian + 'e', file_object.read(2))[0]
def read_float(file_object, endian = '<'):
	return struct.unpack(endian + 'f', file_object.read(4))[0]
def read_vec2(file_object, endian = '<'):
	return struct.unpack(endian + 'ff', file_object.read(8))
def read_vec3(file_object, endian = '<'):
	return struct.unpack(endian + 'fff', file_object.read(12))
def read_vec4(file_object, endian = '<'):
	return struct.unpack(endian + 'ffff', file_object.read(16))
def read_string(file_object):
	chars = []
	while True:
		c = read_byte(file_object)
		if c == 0x00:
			return "".join(chars)
		c = chr(c)
		chars.append(c)
def read_fixed_string(file_object, length):
	chars = []
	for x in range(0,length):
		chars.append(file_object.read(1).decode())
	return "".join(chars)
def read_fixed_byte_string(file_object, length, var1, var2):
	chars = []
	for x in range(0,length):
		chars.append(read_byte(file_object))
	if (var1 == 1):
		file_object.seek(-length, 1)
	if (var2 == 1):
		for x in range(0,length):
			print(('{0:02x}'.format(chars[x])), end = " ")
		print("")
def reverse_string(string):
	return string[::-1]
def get_key(val, dict):
	for key, value in dict.items():
		if val == value:
			return key
	return 0
def getString(file_object, stringOffset):
	backJump = tell(file_object)
	file_object.seek(stringOffset)
	s = read_string(file_object)
	file_object.seek(backJump)
	return s
def read_udec4n_2(file_object):
	normal = read_uint(file_object)
	nx = (((normal >> 00) & 0x3FF) / 1023) * 2 - 1
	ny = (((normal >> 10) & 0x3FF) / 1023) * 2 - 1
	nz = (((normal >> 20) & 0x3FF) / 1023) * 2 - 1

	# print(nx*nx + ny*ny + nz*nz)

	# return (Vector([nx,ny,nz]).normalized())
def read_udec4n(file_object):
	normal = read_uint(file_object)
	a = (((normal >> 0) & 0x3FF) / 1023) - 0.5
	b = (((normal >> 10) & 0x3FF) / 1023) - 0.5
	c = (((normal >> 20) & 0x3FF) / 1023) - 0.5
	d = (1 - (a * a - b * b - c * c))
	e = (normal >> 30)
	#print("{0:032b}".format(normal))
	
	if e == 0:
		return Quaternion([d, a, b, c]).to_axis_angle()[0]
	if e == 1:
		return Quaternion([a, d, b, c]).to_axis_angle()[0]
	if e == 2:
		return Quaternion([a, b, d, c]).to_axis_angle()[0]
	if e == 3:
		return Quaternion([a, b, c, d]).to_axis_angle()[0]
def read_udec4n_3(file_object):
	packedQuat = read_uint(file_object)
	
	idx = packedQuat >> 30

	tx = ((((packedQuat >> 00) & 0x3ff) / 511.5) - 1.0) / 1.4142135
	ty = ((((packedQuat >> 10) & 0x3ff) / 511.5) - 1.0) / 1.4142135
	tz = ((((packedQuat >> 20) & 0x1ff) / 255.5) - 1.0) / 1.4142135
	tw = 0.0

	sum = (tx ** 2 + ty ** 2 + tx **2)

	if sum <= 1.0:
		tw = math.sqrt(1.0 - sum)

	q = [0,0,0,0]

	match idx:
		case 0:
			q = [tw,tx,ty,tz]
		case 1:
			q = [tx,tw,ty,tz]
		case 2:
			q = [tx,ty,tw,tz]
		case 3:
			q = [tx,ty,tz,tw]

	# x 0
	# y 1
	# z 2
	# w 3

	tangent = [
		1 - 2 * (q[1] * q[1] + q[2] * q[2]),
			2 * (q[0] * q[1] + q[3] * q[2]),
			2 * (q[0] * q[2] - q[3] * q[1])
	]
	bitangent = [
			2 * (q[0] * q[1] - q[3] * q[2]),
		1 - 2 * (q[0] * q[0] + q[2] * q[2]),
			2 * (q[1] * q[2] + q[3] * q[0])
	]
	normal = numpy.cross(tangent, bitangent)
	return normal

def unsigned_to_signed(number, num_bits):
	max_value = 2**(num_bits - 1) - 1

	if number <= max_value:
		return number

	return number - 2**num_bits

def read_bits_old(byte_list, num_bits):
	results = []
	result = 0
	bit_count = 0

	for byte in byte_list:
		for i in range(7, -1, -1):
			bit = (byte >> i) & 1
			result = (result << 1) | bit
			bit_count += 1

			if bit_count == num_bits:
				results.append(result)
				result = 0
				bit_count = 0

	if bit_count > 0:
		results.append(result)

	return results

def twos_complement(val, num_bits):
	if (val & (1 << (num_bits - 1))) != 0:
		val = val - (1 << num_bits)
	return val

def read_bits(byte_list, num_bits):
	results = []
	result = 0
	bit_count = 0

	for byte in byte_list:
		for i in range(7, -1, -1):
			bit = (byte >> i) & 1
			result = (result << 1) | bit
			bit_count += 1

			if bit_count == num_bits:
				result = twos_complement(result, num_bits)
				results.append(result)
				result = 0
				bit_count = 0

	if bit_count > 0:
		result = twos_complement(result, num_bits)
		results.append(result)

	return results

# Example usage
byte_list = [0b10101010, 0b11001100, 0b11110000, 0b00001111]
num_bits = 8
results = read_bits(byte_list, num_bits)
print(results)



def alignOffset(file_object, relOffset, alignment):
	if (relOffset % alignment) != 0:
		align = (alignment - (relOffset % alignment))
		file_object.seek(align, 1)
class _sectionTable():
	def __init__(self, file_object):
		self.hash = read_uint(file_object)
		self.offset = read_uint(file_object)
		self.length = read_uint(file_object)

class _ModelAnimDynamicsDef():
	def __init__(self, section, file_object):
		pass
class _ModelAnimGeomInfo():
	def __init__(self, section, file_object):
		pass
class _ModelAnimGeomParticles():
	def __init__(self, arg):
		pass		
class _ModelAnimMorphData():
	def __init__(self, section, file_object):
		self.ModelAnimMorphDataOffset = tell(file_object)
class _ModelAnimMorphIndices():
	def __init__(self, section, file_object):
		self.ModelAnimMorphIndicesOffset = tell(file_object)
class _ModelAnimMorphInfo():
	def __init__(self, section, file_object):
		class _morphInfoTable():
			def __init__(self, file_object):
				self.morphNameHash = read_uint(file_object)
				self.morphInfoOffset = read_uint(file_object)
		class _morphMirrorTable():
			def __init__(self, file_object):
				self.morphNameHash = read_uint(file_object)   #pairing data, LF_x -> RT_x and RT_x -> LF_x, CTR_x not present
				self.morphNameHash2 = read_uint(file_object)
		class _morphInfo():
			def __init__(self):
				self.morphName = None
				self.morphDataOffset = None
				self.morphDataLength = None	
				self.morphIndicesOffset = None
				self.morphIndicesLength = None
				self.morphPackingInfo = None
				self.morphPositionScale  = None
				self.morphPositionBias = None
				self.morphNormalScale  = None
				self.morphNormalBias = None
				self.morphSubsetInfoList = []
		class _morphSubsetInfo():
			def __init__(self):
				self.morphSubsetId = None
				self.morphSubsetVertexOffset = None
				self.morphSubsetIndicesOffset = None
				self.morphSubsetVertexCount = None
				self.morphDataTableList = []
		class _morphDataTable():
			def __init__(self, file_object):
				self.vertexCount = read_ushort(file_object)
				self.indicesCount = read_uint(file_object) 
		class _morphPackingInfo():
			def __init__(self, file_object):
				self.numElements = read_byte(file_object)
				self.bitsPerElement = read_byte(file_object)
				self.bitsPerElementComponent = read_byte(file_object)
				self.null = read_byte(file_object)
				 
				

		# print_here(file_object)
		ukw = read_uint(file_object)        #null / offset?
		morphBuffersLength = read_uint(file_object)     #length of data + indices
		morphCount = read_ushort(file_object)
		morphMirrorCount = read_ushort(file_object)
		morphInfoTableOffset = read_uint(file_object)
		morphMirrorInfoTableOffset = read_uint(file_object)
		ukw4 = read_uint(file_object)       #2

		file_object.seek(morphInfoTableOffset + section.offset)
		morphInfoTableList = [_morphInfoTable(file_object) for x in range(morphCount)]	#morphCount

		file_object.seek(morphMirrorInfoTableOffset + section.offset)
		morphMirrorInfoTableList = [_morphMirrorTable(file_object) for x in range(morphMirrorCount)]
		
		self.morphInfoList = [_morphInfo() for x in range(morphCount)]
		
		print("ModelMorphCount: {0:4x} \nModelMorphMirrorCount: {1:4x}".format(morphCount, morphMirrorCount))
		for x, morphInfoTable in enumerate(morphInfoTableList):
			file_object.seek(section.offset + morphInfoTable.morphInfoOffset)
			# print_here(file_object)

			morphNameHash = read_uint(file_object)
			morphNameOffset = read_uint(file_object)
			morphDataOffset = read_uint(file_object)                            #rel to ModelAnimMorphData
			morphIndicesOffset = read_uint(file_object)                         #rel to ModelAnimMorphIndices
			morphPackingInfo = _morphPackingInfo(file_object)
			
			
			morphPositionScale = read_float(file_object)										#bounding?
			morphPositionBias = read_float(file_object)
			morphNormalScale = read_float(file_object)
			morphNormalBias = read_float(file_object)

			# print(morphPosMax, morphPosMin, morphNrmMax, morphNrmMin)

			morphSubsetCount =				read_ushort(file_object)
			morphSubsetInfoLength =			read_ushort(file_object)                    						#rel to morphSubsetIdList's offset

			morphDataLength =				read_uint(file_object)                            					#rel to ModelAnimMorphData
			morphIndicesLength =			read_uint(file_object)                         						#rel to ModelAnimMorphIndices

			morphSubsetIdList =				[read_byte(file_object) for y in range(morphSubsetCount)]		;	alignOffset(file_object, tell(file_object), 0x04)
			morphSubsetVertexOffsetList =	[read_uint(file_object) for y in range(morphSubsetCount)]			#rel to ModelAnimMorphData
			morphSubsetIndicesOffsetList =	[read_uint(file_object) for y in range(morphSubsetCount)]			#rel to ModelAnimMorphIndices
			morphSubsetVertexCountList =	[read_ushort(file_object) for y in range(morphSubsetCount)]		;	alignOffset(file_object, tell(file_object), 0x04)
			morphSubsetDataTableIndexList =	[read_ushort(file_object) for y in range(morphSubsetCount)]		;	alignOffset(file_object, tell(file_object), 0x04)
			morphSubsetDataTableOffset = 	tell(file_object)

			# print("morphDataOffset: {0:8x}	morphIndicesOffset: {1:8x}".format(morphDataOffset, morphIndicesOffset))
			# print("morphDataLength: {0:8x}	morphIndicesLength: {1:8x}".format(morphDataLength, morphIndicesLength))
			# print("bit stride: {0:02d}".format(morphVertexStride))

			morphSubsetInfoList = [_morphSubsetInfo() for y in range(morphSubsetCount)]
			for y in range(morphSubsetCount):
				# print("{0:2d} {1:8x} {2:8x} {3:4x} {4:4x}".format(morphSubsetIdList[y], morphSubsetVertexOffsetList[y], morphSubsetIndicesOffsetList[y], morphSubsetVertexCountList[y], morphSubsetDataTableIndexList[y]))
				
				morphSubsetInfoList[y].morphSubsetId = morphSubsetIdList[y]
				morphSubsetInfoList[y].morphSubsetVertexOffset = morphSubsetVertexOffsetList[y]
				morphSubsetInfoList[y].morphSubsetIndicesOffset = morphSubsetIndicesOffsetList[y]
				morphSubsetInfoList[y].morphSubsetVertexCount = morphSubsetVertexCountList[y]

				vertexSum = 0
				morphSubsetDataTableIndex = 0
				file_object.seek(morphSubsetDataTableOffset + morphSubsetDataTableIndexList[y] * 0x06)
				while vertexSum < morphSubsetVertexCountList[y]:
					morphDataTable = _morphDataTable(file_object)
					# print("{0:4x} {1:4x} {2:4d} {3:4d} {4:4d}".format(morphDataTable.vertexCount, morphDataTable.indicesCount, morphSubsetIdList[y], morphSubsetDataTableIndex, y))
		
					morphSubsetInfoList[y].morphDataTableList.append(morphDataTable)

					vertexSum += morphDataTable.vertexCount
					morphSubsetDataTableIndex += 1

			self.morphInfoList[x].morphName = getString(file_object, morphNameOffset)
			self.morphInfoList[x].morphDataOffset = morphDataOffset
			self.morphInfoList[x].morphDataLength = morphDataLength
			self.morphInfoList[x].morphIndicesOffset = morphIndicesOffset
			self.morphInfoList[x].morphIndicesLength = morphIndicesLength
			self.morphInfoList[x].morphPackingInfo = morphPackingInfo
			self.morphInfoList[x].morphPositionScale  = morphPositionScale 
			self.morphInfoList[x].morphPositionBias = morphPositionBias
			self.morphInfoList[x].morphNormalScale  = morphNormalScale 
			self.morphInfoList[x].morphNormalBias = morphNormalBias
			self.morphInfoList[x].morphSubsetInfoList = morphSubsetInfoList

class _ModelAnimZivaData():
	def __init__(self, section, file_object):
		pass
class _ModelAnimZivaInfo():
	def __init__(self, section, file_object):
		pass
class _ModelBindPose():
	def __init__(self, section, file_object):
		self.ModelBindPoseOffset = tell(file_object)
		#external data needed to properly parse
		#matrixList - 0x30
		#byte align
		#matrixList - 0x40
class _ModelBuilt():
	def __init__(self, section, file_object):
		self.ukw = read_uint(file_object)	#hash?
		file_object.seek(0x18, 1)           #bound box
		file_object.seek(0x0c, 1)           #null
		self.ukw2 = read_ushort(file_object)
		self.ukw3 = read_ushort(file_object)
		self.vertexScale = read_float(file_object)
		self.ukw5 = read_float(file_object)
		file_object.seek(0x2c, 1)           #always the same, prob dosent matter
		file_object.seek(0x18, 1)           #more stuff here but don't feel like looking
class _ModelColVert():
	def __init__(self, section, file_object):
		self.ModelColVertOffset = tell(file_object)
class _ModelCollisionIndexData():
	def __init__(self, section, file_object):
		pass
class _ModelCollisionVertexData():
	def __init__(self, section, file_object):
		pass
class _ModelGPUSkin():
	def __init__(self, section, file_object):
		self.ModelGPUSkinOffset = tell(file_object)
		print("ModelGPUSkin count: {0:4x}".format(section.length // 0x08))
class _ModelIndex():
	def __init__(self, section, file_object):
		self.ModelIndexOffset = tell(file_object)
		# print("faceCount: {0:4x}".format(section.length // 0x10))
class _ModelJoint():
	def __init__(self, section, file_object):
		class _ModelJointTable():
			def __init__(self, file_object):
				self.parentID = read_ushort(file_object)
				self.childID = read_ushort(file_object)
				self.siblingID = read_ushort(file_object)
				self.ukwID = read_ushort(file_object)
				self.jointNameHash = read_uint(file_object)
				self.jointNameOffset = read_uint(file_object)
		self.ModelJointList = [_ModelJointTable(file_object) for x in range(section.length // 0x10)]           
class _ModelJointBspheres():
	def __init__(self, section, file_object):
		class _bSphereTable():
			def __init__(self, file_object):
				self.posX = read_float(file_object)
				self.posY = read_float(file_object)
				self.posZ = read_float(file_object)
				self.radius = read_float(file_object)
				self.boneOffset = read_uint(file_object)    #offset of matrix in second list of matrices in ModelJoint?

		self.bSphereCount = read_uint(file_object)			#bound sphere
		file_object.seek(0x0c, 1)                           #null
		self.bSphereList = [_bSphereTable(file_object) for x in range(self.bSphereCount)]

		print("ModelJointBspheres count: {0:4x}".format(self.bSphereCount))
class _ModelJointHierarchy():
	def __init__(self, section, file_object):
		self.ukw = read_short(file_object)      #null
		self.ModelJointCount = read_short(file_object)
		self.ModelLocatorCount = read_short(file_object)   #same as ModelMirrorIdCount
		self.ModelLeafIdCount = read_short(file_object)
		self.ukw5 = read_short(file_object)     #0xff/delimiter?

		print("ModelJoint count: {0:4x}\nModelLocator count: {1:4x}\nModelLeafId count: {2:4x}".format(self.ModelJointCount,self.ModelLocatorCount,self.ModelLeafIdCount))
class _ModelJointLookup():
	def __init__(self, section, file_object):
		class _ModelJointLookupTable():
			def __init__(self, file_object):
				self.jointNameHash = read_uint(file_object)
				self.jointIndex = read_uint(file_object) 
		self.ModelJointLookupList = [_ModelJointLookupTable(file_object) for x in range(section.length // 0x08)]
		print("ModelJoint count: {0:4x}".format(section.length // 0x08))
class _ModelLeafIds():
	def __init__(self, section, file_object):
		self.ModelLeafIdsList = [read_ushort(file_object) for x in range(section.length // 0x02)]
		print("ModelLeafIds count: {0:4x}".format(section.length // 0x02))
class _ModelLocator():
	def __init__(self, section, file_object):
		class _ModelLocatorTable():
			def __init__(self, file_object):
				self.igLocNameHash = read_uint(file_object)
				self.igLocNameOffset = read_uint(file_object)
				self.igLocParentID = read_uint(file_object)
				self.null = read_uint(file_object)

				file_object.seek(0x30, 1)   #matrix
		self.ModelLocatorList = [_ModelLocatorTable(file_object) for x in range(section.length // 0x40)]
		print("ModelLocator count: {0:4x}".format(section.length // 0x40))
class _ModelLocatorLookup():
	def __init__(self, section, file_object):
		class _ModelLocatorLookupTable():
			def __init__(self, file_object):
				self.igLocHash = read_uint(file_object)
				self.igLocParentID = read_uint(file_object)
		self.ModelLocatorLookupList = [_ModelLocatorLookupTable(file_object) for x in range(section.length // 0x08)]
class _ModelLook():
	def __init__(self, section, file_object):
		class _ModelLookTable():
			def __init__(self, file_object):
				self.subsetIndex = read_ushort(file_object)
				self.subsetCount = read_ushort(file_object)
		self.ModelLookList = [[_ModelLookTable(file_object) for y in range(0x08)] for x in range(section.length // 0x20)]
		print("ModelLook count: {0:4x}".format(len(self.ModelLookList)))
		#several groups of _ModelLookTable lists defined by ModelLookGroup
		#first group refers to all subsets for model, subsequent groups only refer to subsets for each body part
		#each index of group is for a specific lod, 0 being the highest, 5 being the lowest, range is 8 bc either padding or more possible lods
class _ModelLookBuilt():
	def __init__(self, section, file_object):
		class _ModelLookBuiltTable():
			def __init__(self, file_object):
				self.ukwListOffset = read_ulonglong(file_object)	#bspheres id's?
				self.ukwListOffset2 = read_ulonglong(file_object)
				self.ukwListOffset3 = read_ulonglong(file_object)
				self.ukwListOffset4 = read_ulonglong(file_object)
				self.ukwListOffset5 = read_ulonglong(file_object)
				self.ukwListOffset6 = read_ulonglong(file_object)	#list of bits where count of 1's equal ukwListCount5
				self.ukwListOffset7 = read_ulonglong(file_object)	#list of bits where count of 1's equal look's subset count / every 0x100 bytes is a look's lod
				self.ukwListCount = read_ushort(file_object)
				self.ukwListCount2 = read_ushort(file_object)
				self.ukwListCount3 = read_ushort(file_object)
				self.ukwListCount4 = read_ushort(file_object)
				self.ukwListCount5 = read_ushort(file_object)
				self.null = read_ushort(file_object)
				self.modelLookNameHash = read_uint(file_object)
				self.modelLookNameHash2 = read_uint(file_object)   	#same name but lowercase
				self.modelLookNameOffset = read_uint(file_object)
		self.ModelLookBuiltList = [_ModelLookBuiltTable(file_object) for x in range(len(ModelLook.ModelLookList))]

		#more data after here based on list data, skipping
class _ModelLookGroup():
	def __init__(self, section, file_object):
		class _ModelLookGroupTable():
			def __init__(self, file_object):
				self.modelLookIdOffset = read_uint(file_object)
				self.null = read_uint(file_object)          #offset?
				self.modelLookIdCount = read_uint(file_object)
				self.null2 = read_uint(file_object)         #count?
				self.modelLookGroupNameHash = read_uint(file_object)
				self.modelLookGroupNameOffset = read_uint(file_object)
				self.modelLookIdList = []

		self.modelLookGroupCount = read_byte(file_object)
		self.modelLookGroupList = [_ModelLookGroupTable(file_object) for x in range(self.modelLookGroupCount)]

		for modelLookGroup in self.modelLookGroupList:
			file_object.seek(section.offset + modelLookGroup.modelLookIdOffset + 1)
			modelLookGroup.modelLookIdList.append([read_ushort(file_object) for y in range(modelLookGroup.modelLookIdCount)])

		print("ModelLookGroup count: {0:4x}".format(len(self.modelLookGroupList)))
class _ModelMaterial():
	def __init__(self, section, file_object):
		self.ModelMaterialOffset = tell(file_object)
		print("ModelMaterial count: {0:4x}".format(section.length // 0x20)) #(section length / 2) / 8 = 0x20
class _ModelMirrorIds():
	def __init__(self, section, file_object):
		class _ModelMirrorIdsTable():
			def __init__(self, file_object):
				self.boneId = read_byte(file_object)
				self.ukw = read_byte(file_object)       #flag?
				self.boneId2 = read_byte(file_object)
				self.null = read_byte(file_object)      #flag?
		self.ModelMirrorIdsTableList = [_ModelMirrorIdsTable(file_object) for x in range(section.length // 0x04)]
		print("ModelMirrorIds count: {0:4x}".format(section.length // 0x04))
class _ModelMorphData():
	def __init__(self, section, file_object):
		pass
class _ModelMorphInfo():
	def __init__(self, section, file_object):
		pass	
class _ModelParentIds():
	def __init__(self, section, file_object):
		pass
class _ModelPhysicsData():
	def __init__(self, section, file_object):
		self.ModelPhysicsDataOffset = tell(file_object)
class _ModelRayTracingParameters():
	def __init__(self, section, file_object):
		self.rayTraceLevelHash = read_uint(file_object)   #kLow, kMed, kMedHigh, kHigh
		self.ukw2 = read_uint(file_object)				  #0x1f / flags?

		# print("{0:08x} length: {1:8x} ukw: {2:8x} ukw2: {3:8x}".format(section.hash, section.length, self.ukw, self.ukw2))
class _ModelRenderOverrides():
	def __init__(self, section, file_object):
		pass	
class _ModelSkinBatch():
	def __init__(self, section, file_object):
		class _ModelSkinBatchTable():
			def __init__(self, file_object):
				self.skinDataOffset = read_uint(file_object)
				self.skinJointRemapOffset = read_uint(file_object)
				self.skinJointRemapCount = read_ushort(file_object)
				self.ukw = read_ushort(file_object)
				self.skinVertexCount = read_ushort(file_object)
				self.skinVertexIndex = read_ushort(file_object)
		self.ModelSkinBatchList = [_ModelSkinBatchTable(file_object) for x in range(section.length // 0x10)]
		print("ModelSkinBatch count: {0:4x}".format(section.length // 0x10))
class _ModelSkinData():
	def __init__(self, section, file_object):
		self.ModelSkinDataOffset = tell(file_object)
class _ModelSkinJointRemap():
	def __init__(self, section, file_object):
		self.ModelSkinJointRemapOffset = tell(file_object)
class _ModelSplineJointBinding():
	def __init__(self, section, file_object):
		pass
class _ModelSplineJointWeights():
	def __init__(self, section, file_object):
		pass
class _ModelSplineSkinBinding():
	def __init__(self, section, file_object):
		class _table():
			def __init__(self, file_object):
				self.ukw = read_uint(file_object)   #may be 64bit int idk
				self.ukw2 = read_uint(file_object)
		self.ukwList = [_table(file_object) for x in range(section.length // 0x08)]
		print("ModelSplineSkinBinding count: {0:8x}".format(section.length // 0x08))
class _ModelSplineSubsets():
	def __init__(self, section, file_object):
		class _ModelSplineSubsetsTable():	#table is fucking large, 0x4e8 long
			def __init__(self, file_object):
				self.splineNameHash = read_uint(file_object)
				self.splineNameOffset = read_uint(file_object)
				self.splineCount = read_uint(file_object)
				self.splineIndex = read_uint(file_object)
				self.ukw = read_float(file_object)
				self.ukw2 = read_float(file_object)
				self.ukw3 = read_ushort(file_object)
				self.ukw4 = read_ushort(file_object)
				self.ukw5 = read_byte(file_object)
				self.ukw6 = read_byte(file_object)
				self.ukw7 = read_ushort(file_object)
				file_object.seek(0x10, 1)	#null
				file_object.seek(0x438, 1)	#shit ton of floats
				self.furTintTexturePathStringOffset = read_uint(file_object)
				self.ukwStringOffset2 = read_uint(file_object)
				self.ukwStringOffset3 = read_uint(file_object)
				self.ukwStringOffset4 = read_uint(file_object)
				self.furMaskTexturePathStringOffset = read_uint(file_object)
				file_object.seek(0x14, 1)	#null, may be byte aligned
				self.configPathStringOffset = read_uint(file_object)
				
				
				

				file_object.seek(0x54, 1)	#more unknown data
		self.ModelSplineSubsetsList = [_ModelSplineSubsetsTable(file_object) for x in range(section.length // 0x4e8)]
		print("ModelSplineSubsets count: {0:4x}".format(section.length // 0x4e8))
class _ModelSplines():
	def __init__(self, section, file_object):
		class _table():
			def __init__(self, file_object):
				self.ukw = read_ushort(file_object)
				self.ukw2 = read_byte(file_object)
				self.ukw3 = read_byte(file_object)
				self.ukw4 = read_uint(file_object)   #may be two shorts
				self.ukw5 = read_uint(file_object)   #may be two shorts
		self.ukwList = [_table(file_object) for x in range(section.length // 0x0c)]

		print("ModelSplines count: {0:4x}".format(section.length // 0x0c))
class _ModelStdVert():
	def __init__(self, section, file_object):
		self.ModelStdVertOffset = tell(file_object)
		print("ModelStdVert count: {0:4x}".format(section.length // 0x10))
class _ModelSubset():
	def __init__(self, section, file_object):
		class _ModelSubsetTable():
			def __init__(self, file_object):
				# read_fixed_byte_string(file_object, 0x40, 1, 1)
				float_bytes = bytearray(struct.pack('f', 0))

				self.ukwFloat = read_float(file_object)
				self.ukwFloat2 = read_float(file_object)
				self.ukwFloat3 = read_float(file_object)
				self.ukw = read_ushort(file_object)
				self.ukw2 = read_ushort(file_object)
				self.ukw3 = read_ushort(file_object)
				self.ukw4 = read_ushort(file_object)
				self.vertexIndex = read_uint(file_object)
				self.faceIndex = read_uint(file_object)
				self.faceCount = read_uint(file_object)
				self.vertexCount = read_ushort(file_object)
				self.ukw8 = read_ushort(file_object)
				self.ukw9 = read_byte(file_object)              #11
				self.modelGPUSkinFlag = read_byte(file_object)  #if subset uses ModelGPUSkin
				self.materialID = read_ushort(file_object)
				self.skinBatchIndex = read_ushort(file_object)
				self.skinBatchCount = read_byte(file_object)
				self.ukw10 = read_byte(file_object)             #related to skinBatchCount?
				self.ukw13 = read_ushort(file_object)           #count?
				self.ukw14 = read_ushort(file_object)           #offset?, increases by 0x10 every subset + 0x01 every lod
				self.ukwFloat4 = read_float(file_object)
				self.ukwFloat5 = read_float(file_object)
				self.modelGPUSkinVertexIndex = read_uint(file_object)
				self.null = read_float(file_object)    

		self.ModelSubsetList = [_ModelSubsetTable(file_object) for x in range(section.length // 0x40)]
		print("ModelSubset count: {0:4x}".format(section.length // 0x40))
		
		# j = 0
		# for x in self.ModelSubsetList:
		# 	j += x.ukw13
		# print_hex(j)
class _ModelTexVert():
	def __init__(self, section, file_object):
		self.ModelTexOffset = tell(file_object)
class _ModelTextureOverrides():
	def __init__(self, section, file_object):
		pass
class _ModelUV1Vert():
	def __init__(self, section, file_object):
		self.ModelUV1VertOffset = tell(file_object)
class _53ea4273():
	def __init__(self, section, file_object):
		pass
class _5a39fab7():
	def __init__(self, section, file_object):
		pass #couple arrays, dont feel like figuring it out
class _665da362():
	def __init__(self, section, file_object):
		pass
class _707f1b58():
	def __init__(self, section, file_object):
		class _table():
			def __init__(self, file_object):
				file_object.seek(0x40, 1)   				#matrix
				file_object.seek(0x40, 1)   				#matrix2
				self.jointNameHash = read_uint(file_object)
				self.jointIndex = read_ushort(file_object)
				self.ukw2 = read_ushort(file_object)		#id?
				self.jointParentID = read_ushort(file_object)
				self.jointListIndex = read_ushort(file_object)
				self.jointListCount = read_ushort(file_object)
				self.ukw6 = read_ushort(file_object)		#null?
				self.jointList = []
		
		self.ukwOffset = read_uint(file_object)
		self.ukwOffset2 = read_uint(file_object)
		self.ukwCount = read_ushort(file_object)
		self.ukwCount2 = read_ushort(file_object)
		self.ukw = read_uint(file_object)

		file_object.seek(section.offset + self.ukwOffset)
		self.ukwList = [_table(file_object) for x in range(self.ukwCount)]
		
		# file_object.seek(section.offset + self.ukwOffset2)
		# self.ukwList2 = [read_ushort(file_object) for x in range(self.ukwCount2)]
		for ukw in self.ukwList:
			file_object.seek(section.offset + self.ukwOffset2 + (ukw.jointListIndex * 0x02))
			ukw.jointList = [read_ushort(file_object) for x in range(ukw.jointListCount)]

		# print("707f1b58 length: {0:8x} count:{1:4x}       count2: {2:4x}".format(section.length, len(self.ukwList), len(self.ukwList2)))
class _7ca37da0():
	def __init__(self, section, file_object):
		pass		
class _855275d7():
	def __init__(self, section, file_object):
		pass
class _8a84e4d6():
	def __init__(self, section, file_object):
		pass
class _9a434b29():
	def __init__(self, section, file_object):
		class _table1():
			def __init__(self, file_object):
				self.ukw = read_uint(file_object)
				self.jointNameHash = read_uint(file_object)
				self.ukw2 = read_ushort(file_object)    #offset/index?
				self.ukw3 = read_ushort(file_object)    #offset/index?
				self.ukw4 = read_ushort(file_object)
				self.ukw5 = read_ushort(file_object)
				file_object.seek(0x60, 1)               #floats
		class _table2():
			def __init__(self, file_object):
				file_object.seek(0x28, 1)               #floats
				self.ukw = read_byte(file_object)       #index?
				self.ukw2 = read_byte(file_object)      #0/1/2
				self.ukw3 = read_byte(file_object)      #0/1
				self.ukw4 = read_byte(file_object)      #null?
		class _table3():
			def __init__(self, file_object):
				file_object.seek(0x20, 1)               #not sure if first 4 bytes is float
		
		self.sectionLength = read_uint(file_object)
		self.ukwOffset = read_uint(file_object)
		self.ukwOffset2 = read_uint(file_object)
		self.ukwOffset3 = read_uint(file_object)
		self.ukwOffset4 = read_uint(file_object)
		self.ukwCount = read_byte(file_object)
		self.ukwCount2 = read_byte(file_object)

		file_object.seek(section.offset + self.ukwOffset)
		self.ukwList = [_table1(file_object) for x in range(self.ukwCount)]

		file_object.seek(section.offset + self.ukwOffset2)
		self.ukwList2 = [_table2(file_object) for x in range(self.ukwCount2)]

		file_object.seek(section.offset + self.ukwOffset3)
		self.ukwList3 = [_table2(file_object) for x in range(self.ukwCount)]

		file_object.seek(section.offset + self.ukwOffset4)
		self.ukwList4 = [read_ushort(file_object) for x in range(self.ukwCount2)]

		# print("9a434b29                 count: {0:4x}     count2: {1:4x}".format(self.ukwCount,self.ukwCount2))
class _b25b3163():
	def __init__(self, section, file_object):
		class _table():
			def __init__(self, file_object):
				self.ukw = read_ushort(file_object)
				self.ukw2 = read_ushort(file_object)
				self.ukw3 = read_ushort(file_object)
				self.ukw4 = read_ushort(file_object)
		self.ukwList = [_table(file_object) for x in range(section.length // 0x08)]
		print("b25b3163 count: {0:8x} length: {1:8x}".format(section.length // 0x08, section.length))
class _df9fdf12():
	def __init__(self, section, file_object):
		class _table():
			def __init__(self, file_object):
				self.ukw = read_uint(file_object)     #offset/index?
				self.ukw2 = read_uint(file_object)    #0x1f/count?
				self.ukw3 = read_uint(file_object)    #length/count?
				self.ukw4 = read_uint(file_object)    #0x02/count?
		self.ukwList = [_table(file_object) for x in range(section.length // 0x10)]     #same count as look group
		# print("df9fdf12 length: {0:8x} count: {1:8x}".format(section.length, len(self.ukwList)))
class _fb7f6a48():
	def __init__(self, section, file_object):
		pass

filePath = r"D:\models\ripped\ratchet and clank rift apart\characters\hero\hero_ratchet\hero_ratchet.model"
# filePath = r"C:\Users\Xavier\Downloads\New folder\New folder\hero_ratchet_bangle_head_default.model-edit"
# filePath = r"D:\models\ripped\ratchet and clank rift apart\characters\npc\npc_helper_bot\npc_helper_bot.model"
f = open(filePath, "rb+")

_1TAD = read_fixed_string(f, 4)
fileTypeHash = read_uint(f)
fileLength = read_uint(f)
tableCount = read_uint(f)

sectionTableList = [_sectionTable(f) for x in range(tableCount)]
for section in sectionTableList:
	f.seek(section.offset)
	match section.hash:
		case 0xefd92e68: ModelPhysicsData = _ModelPhysicsData(section, f)
		case 0xdf9fdf12: _df9fdf12(section, f)
		case 0x283d0383: ModelBuilt = _ModelBuilt(section, f)
		case 0x90cdb60c: ModelJointHierarchy = _ModelJointHierarchy(section, f)
		case 0x15df9d3b: ModelJoint = _ModelJoint(section, f)
		case 0xdcc88a19: ModelBindPose = _ModelBindPose(section, f)
		case 0xc5354b60: ModelMirrorIds = _ModelMirrorIds(section, f)
		case 0xb7380e8c: ModelLeafIds = _ModelLeafIds(section, f)
		case 0x0ad3a708: ModelJointBspheres = _ModelJointBspheres(section, f)
		case 0xee31971c: ModelJointLookup = _ModelJointLookup(section, f)
		case 0x0ba45069: ModelRayTracingParameters = _ModelRayTracingParameters(section, f)
		case 0x9f614fab: ModelLocator = _ModelLocator(section, f)
		case 0x731cbc2e: ModelLocatorLookup = _ModelLocatorLookup(section, f)
		case 0x707f1b58: _707f1b58_ = _707f1b58(section, f)
		case 0x5a39fab7: _5a39fab7(section, f)
		case 0x9a434b29: _9a434b29(section, f)
		case 0x06eb7efc: ModelLook = _ModelLook(section, f)
		case 0x53ea4273: _53ea4273(section, f)
		case 0xfb7f6a48: _fb7f6a48(section, f)
		case 0x4ccea4ad: ModelLookGroup = _ModelLookGroup(section, f)
		case 0x811902d7: ModelLookBuilt = _ModelLookBuilt(section, f)
		case 0x665da362: _665da362(section, f)
		case 0x3c9dabdf: ModelSplineSubsets =_ModelSplineSubsets(section, f)
		case 0x27ca5246: ModelSplines = _ModelSplines(section, f)
		case 0xb25b3163: _b25b3163(section, f)
		case 0xbb7303d5: ModelSplineSkinBinding = _ModelSplineSkinBinding(section, f)
		case 0x14d8b13c: ModelSplineJointBinding = _ModelSplineJointBinding(section, f)
		case 0x5d5cf541: ModelSplineJointWeights = _ModelSplineJointWeights(section, f)
		case 0x78d9cbde: ModelSubset = _ModelSubset(section, f)
		case 0x3250bb80: ModelMaterial = _ModelMaterial(section, f)
		case 0xdca379a2: ModelSkinData = _ModelSkinData(section, f)
		case 0xc61b1ff5: ModelSkinBatch = _ModelSkinBatch(section, f)
		case 0x7ca37da0: _7ca37da0(section, f)
		case 0x5240c82b: ModelSkinJointRemap = _ModelSkinJointRemap(section, f)
		case 0x237d59f1: ModelMorphInfo = _ModelMorphInfo(section, f)
		case 0x45079bc5: ModelMorphData = _ModelMorphData(section, f)
		case 0xcd903318: ModelAnimGeomInfo = _ModelAnimGeomInfo(section, f)
		case 0x3f70f60d: ModelAnimGeomParticles = _ModelAnimGeomParticles(section, f)
		case 0x42349a17: ModelAnimZivaInfo = _ModelAnimZivaInfo(section, f)
		case 0x244e5823: ModelAnimZivaData = _ModelAnimZivaData(section, f)
		case 0x380a5744: ModelAnimMorphInfo = _ModelAnimMorphInfo(section, f)
		case 0x5e709570: ModelAnimMorphData = _ModelAnimMorphData(section, f)
		case 0xa600c108: ModelAnimMorphIndices = _ModelAnimMorphIndices(section, f)
		case 0x855275d7: _855275d7(section, f)
		case 0x8a84e4d6: _8a84e4d6(section, f)
		case 0xadd1cbd3: ModelAnimDynamicsDef =_ModelAnimDynamicsDef(section, f)
		case 0x5796fef6: ModelCollisionIndexData = _ModelCollisionIndexData(section, f)
		case 0xf4cb2f37: ModelCollisionVertexData = _ModelCollisionVertexData(section, f)
		case 0x0859863d: ModelIndex = _ModelIndex(section, f)
		case 0xa98be69b: ModelStdVert = _ModelStdVert(section, f)
		case 0x16f3ba18: ModelTexVert = _ModelTexVert(section, f)
		case 0x6b855eed: ModelUV1Vert = _ModelUV1Vert(section, f)
		case 0x5cba9de9: ModelColVert = _ModelColVert(section, f)
		case 0xccbaff15: ModelGPUSkin = _ModelGPUSkin(section, f)
		case _:
			print("Unknown hash: {0:08x}    offset: {1:8x}  length: {2:8x}".format(section.hash, section.offset, section.length))


# for ukw in _707f1b58_.ukwList:
# 	# print("{0:2x} {1:2x} {3:s} {4:s}".format(ukw.ukw2, ukw.ukw3, (getString(f, ModelJoint.ModelJointList[ukw.jointIndex].jointNameOffset))))
# 	print("{0:s}		{1:s}".format((getString(f, ModelJoint.ModelJointList[ukw.jointIndex].jointNameOffset)), (getString(f, ModelJoint.ModelJointList[ukw.ukw2].jointNameOffset))))
# 	for ukwList in ukw.jointList:
# 		print(getString(f, ModelJoint.ModelJointList[ukwList].jointNameOffset))
# 	print("")

# print("ModelAnimMorphDataOffset: {0:x} ModelAnimMorphIndices {1:x}".format(ModelAnimMorphData.ModelAnimMorphDataOffset, ModelAnimMorphIndices.ModelAnimMorphIndicesOffset))


# for modelSplineSubset in ModelSplineSubsets.ModelSplineSubsetsList:
# 	print(getString(f, modelSplineSubset.splineNameOffset))
# 	print(getString(f, modelSplineSubset.furTintTexturePathStringOffset))
# 	print(getString(f, modelSplineSubset.furMaskTexturePathStringOffset))
	

	

for morphInfo in ModelAnimMorphInfo.morphInfoList:
	print(morphInfo.morphName)
	print("morphDataOffset: {0:8x}	morphIndicesOffset: {1:8x}".format(morphInfo.morphDataOffset, morphInfo.morphIndicesOffset))
	print("morphDataLength: {0:8x}	morphIndicesLength: {1:8x}".format(morphInfo.morphDataLength, morphInfo.morphIndicesLength))	
	print("stride: {3:4d}	numElements: {0:4d}	bitsPerElement:	{1:4d}	bitsPerElementComponent: {2:4d}".format(morphInfo.morphPackingInfo.numElements, morphInfo.morphPackingInfo.bitsPerElement, morphInfo.morphPackingInfo.bitsPerElementComponent, (morphInfo.morphPackingInfo.bitsPerElement * morphInfo.morphPackingInfo.numElements)))
	print("positionScaleRange:	[{0}, {1}]".format(morphInfo.morphPositionScale, morphInfo.morphPositionBias))
	print("normalScaleRange:	[{0}, {1}]".format(morphInfo.morphNormalScale, morphInfo.morphNormalBias))
	for morphSubsetInfo in morphInfo.morphSubsetInfoList:
		print("{0:2d} {1:8x} {2:8x} {3:4x}".format(morphSubsetInfo.morphSubsetId, morphSubsetInfo.morphSubsetVertexOffset, morphSubsetInfo.morphSubsetIndicesOffset, morphSubsetInfo.morphSubsetVertexCount))
		
		morphSubsetVerticesList = []
		f.seek(ModelAnimMorphData.ModelAnimMorphDataOffset + morphInfo.morphDataOffset + morphSubsetInfo.morphSubsetVertexOffset)
		for morphSubsetDataTableIndex, morphDataTable in enumerate(morphSubsetInfo.morphDataTableList):
			morphVertexStride = (morphInfo.morphPackingInfo.bitsPerElement * morphInfo.morphPackingInfo.numElements)

			bytesToRead = math.ceil((morphVertexStride * morphDataTable.vertexCount) / 8)
			print("{0:8x} {1:4x} {2:4x} {3:4d}".format((tell(f)), bytesToRead, morphDataTable.vertexCount, morphSubsetDataTableIndex))
			packedVertices = bytearray(f.read(bytesToRead)) ; alignOffset(f, tell(f), 0x04)
			unpackedVertices = read_bits_old(packedVertices, morphInfo.morphPackingInfo.bitsPerElement)
			# deltaPositions = [unpackedVertices[i:i+3] for i in range(0, morphDataTable.vertexCount * 3, 3)]
			# for deltaVertex in deltaVertices:
			# 	# if morphSubsetInfo.morphSubsetId == 26: print(deltaVertex)
			# 	morphSubsetVerticesList.append(deltaVertex)


			
		morphSubsetIndicesList = []
		f.seek(ModelAnimMorphIndices.ModelAnimMorphIndicesOffset + morphInfo.morphIndicesOffset + morphSubsetInfo.morphSubsetIndicesOffset)
		for morphSubsetDataTableIndex, morphDataTable in enumerate(morphSubsetInfo.morphDataTableList):
			vertexIndex = 0xa00 * morphSubsetDataTableIndex
			# print("{0:4x} {1:4x} {2:4d}".format(vertexIndex, morphDataTable.indicesCount, morphSubsetDataTableIndex))

			for x in range(morphDataTable.indicesCount):
				vertexSkip = read_ushort(f)
				vertexRead = read_ushort(f)
				if vertexRead == 0x00: vertexRead = 0x20

				vertexIndex += vertexSkip
				vertexRange = vertexRead
				vertexEndIndex = vertexRange + vertexIndex

				for i in range(vertexIndex, vertexEndIndex):
					morphSubsetIndicesList.append(i)

				if morphSubsetInfo.morphSubsetId == 26: print("[", vertexIndex, ", ", vertexRange, "],")
				vertexIndex = vertexEndIndex
		# if morphSubsetInfo.morphSubsetId == 26: print_hex(len(morphSubsetIndicesList))


# print("bone count: ", ModelJointHierarchy.ModelJointCount)
# f.seek(ModelBindPose.ModelBindPoseOffset)
# for x in range(ModelJointHierarchy.ModelJointCount):
#   read_fixed_byte_string(f, 0x30, 1, 0)
#   boneScale = [read_float(f),read_float(f),read_float(f),read_float(f)]
#   boneRotation = [read_float(f),read_float(f),read_float(f),read_float(f)]
#   boneTranslation = [read_float(f),read_float(f),read_float(f),read_float(f)]
# alignOffset(f, tell(f) - ModelBindPose.ModelBindPoseOffset, 0x40)
# for x in range(ModelJointHierarchy.ModelJointCount):
#   f.seek(0x40, 1)

modelScale = 1.0
lookSelection = 0
lodSelection = 0

# print(len(ModelSubset.ModelSubsetList))

subsetSelectionList = [26]
subsetSelection = ModelLook.ModelLookList[lookSelection][lodSelection]
# for x in subsetSelectionList:
for x in range(len(ModelSubset.ModelSubsetList)):
# for x in range(subsetSelection.subsetIndex, (subsetSelection.subsetIndex + subsetSelection.subsetCount)):
	modelSubset = ModelSubset.ModelSubsetList[x]   
	modelName = getString(f, ModelLookBuilt.ModelLookBuiltList[lookSelection].modelLookNameOffset)

	f.seek(ModelMaterial.ModelMaterialOffset + (0x10 * modelSubset.materialID))
	materialPath = getString(f, read_ulonglong(f))
	materialName = getString(f, read_ulonglong(f))

	vertexList = []
	f.seek(ModelStdVert.ModelStdVertOffset + modelSubset.vertexIndex * 0x10)
	for x in range(modelSubset.vertexCount):
		vx = read_short(f) / 4096.0
		vy = read_short(f) / 4096.0
		vz = read_short(f) / 4096.0


		r1 = read_byte(f)
		r2 = read_byte(f)
		r3 = read_byte(f)
		r4 = read_byte(f)
		r5 = read_byte(f)
		r6 = read_byte(f)

		# if x < 50: print("{0:08b} {1:08b} {2:08b} {3:08b} {4:08b} {5:08b}".format(r1,r2,r3,r4,r5,r6))
		
		tu = read_short(f) / 1024.0    #sometimes 16384.0
		tv = read_short(f) / 1024.0


		# if x < 300: print("{0:032b} {1:032b}".format(normals, tangents))

		# if x < 100: print("{0:032b}".format(normals))
		# if x < 100: print("{0:032b}".format(tangents))
		# print("\n")

		# vertexList.append(Vector([vx,vy,vz]) * modelScale)

	# uvList = []
	# f.seek(ModelUV1Vert.ModelUV1VertOffset + modelSubset.vertexIndex * 0x04)
	# for x in range(modelSubset.vertexCount):
	#     tu = read_short(f) / 4096.0
	#     tv = read_short(f) / 4096.0

	#     # uvList.append(Vector([tu,1-tv]))

	indexList = []
	f.seek(ModelIndex.ModelIndexOffset + modelSubset.faceIndex * 0x02)
	for x in range(modelSubset.faceCount // 3):
		fa = read_ushort(f)
		fb = read_ushort(f)
		fc = read_ushort(f)
		# indexList.append([fa,fb,fc])

	boneIndicesList = []
	boneWeightsList = []

	# print_hex(modelSubset.vertexCount)
	# print("skinBatchIndex: {0:x} skinBatchCount: {1:x}".format(modelSubset.skinBatchIndex, modelSubset.skinBatchCount))
	for x in range(modelSubset.skinBatchIndex, modelSubset.skinBatchIndex + modelSubset.skinBatchCount):
		modelSkinBatch = ModelSkinBatch.ModelSkinBatchList[x]
		# print("skinDataOffset: {0:08x}  ukw: {1:04x}  skinVertexCount: {2:04x}  skinVertexIndex: {3:04x}".format((modelSkinBatch.skinDataOffset + ModelSkinData.ModelSkinDataOffset), modelSkinBatch.ukw, modelSkinBatch.skinVertexCount, modelSkinBatch.skinVertexIndex))

		f.seek (modelSkinBatch.skinJointRemapOffset)
		boneMap = [read_ushort(f) for y in range(modelSkinBatch.skinJointRemapCount)] if (modelSkinBatch.skinJointRemapCount > 0) else [y for y in range(ModelJointHierarchy.ModelJointCount)]

		f.seek(modelSkinBatch.skinDataOffset + ModelSkinData.ModelSkinDataOffset)
		j = 0
		while j < modelSkinBatch.skinVertexCount:
			influenceCount = read_byte(f)
			for y in range(0x10):               #skin data is grouped up in bundles of 0x10 up until skinVertexCount
				bones = [] ; weights = []
				for z in range(influenceCount + 1):   #1 - 12
					bones.append (boneMap[read_byte(f)]) ; weights.append (read_byte(f) / 256.0 if (influenceCount > 0) else 1.0)
				boneIndicesList.append(bones)
				boneWeightsList.append(weights)
				j += 1
				if j >= modelSkinBatch.skinVertexCount: break

print("Last read @ {0:x}".format(tell(f)))