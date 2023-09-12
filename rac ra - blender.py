import io
import sys
import math
import struct
import uuid
import os
import bpy
import mathutils
import numpy
from mathutils import Matrix, Quaternion, Vector

def clean_scene():      #stolen
    for item in bpy.data.objects:
        if item.type == 'MESH' or item.type == 'EMPTY':
            bpy.data.objects.remove(item)

    check_users = False
    for collection in (
        bpy.data.meshes, 
        bpy.data.armatures, 
        bpy.data.materials, 
        bpy.data.textures, 
        bpy.data.images, 
        bpy.data.collections
    ):
         for item in collection:
             if item.users == 0 or not check_users:
                 collection.remove(item)

def tell(file_object, endian = '<'):
    return file_object.tell()
def print_here(file_object, endian = '<'):
    print ("Here at:    {0:x}".format(tell(file_object)))
def print_hex(file_object, endian = '<'):
    print ("{0:x}".format(file_object))
def alignOffset(file_object, relOffset, alignment):
    if (relOffset % alignment) != 0:
        align = (alignment - (relOffset % alignment))
        file_object.seek(align, 1)
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
def read_udec4n(file_object):
    normal = read_uint(file_object)
    nx = (((normal >> 0) & 0x3FF) / 1023) * 2 - 1
    ny = (((normal >> 10) & 0x3FF) / 1023) * 2 - 1
    nz = (((normal >> 20) & 0x3FF) / 1023) * 2 - 1
    nw = (((normal >> 30) & 0x03))
    
    return (Vector([nx,ny,nz]).normalized())
def read_udec4n_3(file_object):
    Packed = read_uint(file_object)
    
    idx = Packed >> 30;
    tx = ((Packed >> 00 & 0x3FF) / 511.5 - 1.0) / 1.4142135
    ty = ((Packed >> 10 & 0x3FF) / 511.5 - 1.0) / 1.4142135
    tz = ((Packed >> 20 & 0x3FF) / 511.5 - 1.0) / 1.4142135
    tw = 0.0
    
    sum = tx * tx + ty * ty + tz * tz
    if (sum <= 1.0): tw = math.sqrt(1.0 - sum)
    if tw < 0: print(tw)

    qX = 0.0
    qY = 0.0
    qZ = 0.0
    qW = 0.0

    match idx:
        case 0:
            qX = tw; qY = tx; qZ = ty; qW = tz;
        case 1:
            qX = tx; qY = tw; qZ = ty; qW = tz;
        case 2:
            qX = tx; qY = ty; qZ = tw; qW = tz;
        case 3:
            qX = tx; qY = ty; qZ = tz; qW = tw;
    
    tempTangent = [
        1 - 2 * (qY * qY + qZ * qZ),
            2 * (qX * qY + qW * qZ),
            2 * (qX * qZ - qW * qY)
    ]
    tempBitangent = [
            2 * (qX * qY - qW * qZ),
        1 - 2 * (qX * qX + qZ * qZ),
            2 * (qY * qZ + qW * qX)
    ]
#    tempNormal = [
#        (tempTangent[1] * tempBitangent[2]) - (tempTangent[2] * tempBitangent[1]),
#        (tempTangent[2] * tempBitangent[0]) - (tempTangent[0] * tempBitangent[2]),
#        (tempTangent[0] * tempBitangent[1]) - (tempTangent[1] * tempBitangent[0])
#    ]
    
#    normal = Vector3.Cross(m.Row0, m.Row1) * ((q.W < 0.0f) ? -1.0f : 1.0f);
    normal = mathutils.Vector.cross(Vector(tempTangent), Vector(tempBitangent))
    
    return normal
def readBits(stride, vertexCount, f):
    # byteRange = math.ceil(float(stride) / 8)
    componentSize = stride // 3
    # bitRange = (byteRange * 8)
    print("stride: {0:02d} componentSize: {1:02d}".format(stride, componentSize))
    
    divisor = 0
    for x in range(stride): divisor += (2 ** x)
    
    verts = []
    edges = []
    faces = []
    
#    vertexCount = 0x6f
    
    bitIndex = 0
    for x in range(vertexCount):
        byteRange = math.ceil(float(bitIndex + stride) / 8)
        bitRange = (byteRange * 8)
        print("byteRange: {0:02d} bitRange: {1:02d}".format(byteRange, bitRange))

        print_here(f)
        bytes = f.read(byteRange)
#        bits = ''.join(format(ord(chr(byte)), '08b') for byte in bytes[::-1])
        bits = ''.join(format(ord(chr(byte)), '08b') for byte in bytes)
        
#        print(bytes.hex())
#        print("bitStart: {0:2d}".format(bitIndex))
#        print(bits)

        mPos = [0,0,0]

        for y in range(3):
#            b = bits[bitIndex:bitIndex + componentSize]
            b = bits[bitIndex:bitIndex + componentSize][::-1]
            
            # print_hex(int(b, 2) )
            print(b)

            mPos[y] = (int(b, 2) / 4096.0) * 2 - 1
            bitIndex += componentSize

        remainingBits = (bitRange - bitIndex)
        if bitIndex == bitRange: bitIndex = 0
        else:
            f.seek(-1,1)
            bitIndex = (8 - remainingBits)

        verts.append(mPos)
        print(mPos)
#        print("remainingBits: {0:2d} newBitIndex: {1:2d}\n".format(remainingBits, bitIndex))
    
    new_mesh = bpy.data.meshes.new("")
    new_mesh.from_pydata(verts,[],[])

    mesh_obj = bpy.data.objects.new("", new_mesh)
    bpy.context.scene.collection.objects.link(mesh_obj)
    bpy.context.view_layer.objects.active = mesh_obj
    bpy.ops.object.mode_set(mode='EDIT')
    
    


class _sectionTable():
    def __init__(self, file_object):
        self.hash = read_uint(file_object)
        self.offset = read_uint(file_object)
        self.length = read_uint(file_object)
class _ModelAnimMorphInfo():
    def __init__(self, section, file_object):
        class _morphNameTable():
            def __init__(self, file_object):
                self.morphNameHash = read_uint(file_object)
                self.morphInfoOffset = read_uint(file_object)
        class _morphMirrorTable():
            def __init__(self, file_object):
                self.morphNameHash = read_uint(file_object)   #pairing data, LF_x -> RT_x and RT_x -> LF_x, CTR_x not present
                self.morphNameHash2 = read_uint(file_object)
        class _morphDataTable():
            def __init__(self, file_object):
                self.vertexCount = read_ushort(file_object)
                self.indicesCount = read_uint(file_object)  
        class _morphIndexTable():
            def __init__(self, file_object, subsetIndex):
                self.vertexSkip = read_ushort(file_object)
                self.vertexRead = read_ushort(file_object)
                self.subsetIndex = subsetIndex

                if self.vertexRead == 0x00: self.vertexRead = 0x20
                
        print_here(file_object)
        ukw = read_uint(file_object)        #null / offset?
        ukw2 = read_ushort(file_object)     #count? / uint?
        ukw4 = read_ushort(file_object)     #count?
        morphCount = read_ushort(file_object)
        morphMirrorCount = read_ushort(file_object)
        morphNameTableOffset = read_uint(file_object)
        morphMirrorTableOffset = read_uint(file_object)
        ukw4 = read_uint(file_object)       #2

        file_object.seek(morphNameTableOffset + section.offset)
        morphNameTableList = [_morphNameTable(file_object) for x in range(morphCount)]

        file_object.seek(morphMirrorTableOffset + section.offset)
        morphMirrorTableList = [_morphMirrorTable(file_object) for x in range(morphMirrorCount)]
        
        modelAnimMorphDataOffset = 0x297510 #0x24f410
        modelAnimMorphIndicesOffset = 0x9672c0 #0xe0c3f0
        
        print("morphCount: {0:04x} morphMirrorCount: {1:04x}".format(morphCount, morphMirrorCount))
        for x, table in enumerate(morphNameTableList):
            file_object.seek(table.morphInfoOffset + section.offset)
            # print_here(file_object)

            morphNameHash = read_uint(file_object)
            morphNameOffset = read_uint(file_object)
            morphDataOffset = read_uint(file_object)                            #rel to ModelAnimMorphData
            morphIndicesOffset = read_uint(file_object)                         #rel to ModelAnimMorphIndices
            
            print("{0:04d} - {1:s}".format((x+1), getString(file_object, morphNameOffset)))
            read_fixed_byte_string(file_object, 0x04, 1, 1)

            # 02 0c 04 00   0 00000100 00011000 00001000 0000000    24 bits / 08 bits per component
            # 02 0f 05 00   0 00000100 00011110 00001010 0000000    30 bits / 10 bits per component
            # 02 12 06 00   0 00000100 00100100 00001100 0000000    36 bits / 12 bits per component
            # 02 15 07 00   0 00000100 00101010 00001110 0000000    42 bits / 14 bits per component
            # 02 18 08 00   0 00000100 00110000 00010000 0000000    48 bits / 16 bits per component
            # 02 1b 09 00   0 00000100 00110110 00010010 0000000    56 bits / 18 bits per component
            # 02 1e 0a 00   0 00000100 00111100 00010100 0000000    60 bits / 20 bits per componnet
            
            morphPackedBits = read_uint(file_object)                            #would be easeir to read if eveything wasnt shifted down 1 bit
            morphVertexStride = (morphPackedBits & 0x7F80) >> 7                 #strides in bits
            morphVertexComponentSize = (morphPackedBits & 0x7F8000) >> 15       #bits per vertex component
            # print("{0:032b}".format(morphPackedBits))
            
            ukwFloat = read_float(file_object)                                  #bounding?
            ukwFloat2 = read_float(file_object)
            ukwFloat3 = read_float(file_object)
            ukwFloat4 = read_float(file_object)
            # print(ukwFloat,ukwFloat2,ukwFloat3,ukwFloat4)

            morphSubsetCount =              read_ushort(file_object)
            morphSubsetInfoLength =         read_ushort(file_object)                                            #rel to morphSubsetIdList's offset
            morphSubsetInfoEnd =            (tell(file_object) + morphSubsetInfoLength)

            morphDataLength =               read_uint(file_object)                                              #rel to ModelAnimMorphData
            morphIndicesLength =            read_uint(file_object)                                              #rel to ModelAnimMorphIndices
                
            morphSubsetIdList =             [read_byte(file_object) for y in range(morphSubsetCount)]       ;   alignOffset(file_object, tell(file_object), 0x04)
            morphSubsetDataOffsetList =     [read_uint(file_object) for y in range(morphSubsetCount)]           #rel to ModelAnimMorphData
            morphSubsetIndicesOffsetList =  [read_uint(file_object) for y in range(morphSubsetCount)]           #rel to ModelAnimMorphIndices
            morphVertexCountList =          [read_ushort(file_object) for y in range(morphSubsetCount)]     ;   alignOffset(file_object, tell(file_object), 0x04)
            morphDataTableIndexList =       [read_ushort(file_object) for y in range(morphSubsetCount)]     ;   alignOffset(file_object, tell(file_object), 0x04)

            print("morphDataOffset: {0:8x}  morphIndicesOffset: {1:8x}".format(morphDataOffset, morphIndicesOffset))
            print("morphDataLength: {0:8x}  morphIndicesLength: {1:8x}".format(morphDataLength, morphIndicesLength))
            print("bit stride: {0:02d}".format(morphVertexStride))
            
            for y in range(morphSubsetCount):print("{0:2d} {1:8x} {2:8x} {3:4x} {4:4x}".format(morphSubsetIdList[y], morphSubsetDataOffsetList[y], morphSubsetIndicesOffsetList[y], morphVertexCountList[y], morphDataTableIndexList[y]))
            
            subsetListIndex = 0
            morphDataTableList = []
            while (tell(file_object) < morphSubsetInfoEnd):morphDataTableList.append(_morphDataTable(file_object))
            
            morphIndicesList = [[]]
            file_object.seek(modelAnimMorphIndicesOffset + morphIndicesOffset + morphSubsetIndicesOffsetList[subsetListIndex])
            for idx, table in enumerate(morphDataTableList):
                print("{0:4x} {1:4x} {2:4x} {3:4d}".format(table.vertexCount, table.indicesCount, idx, morphSubsetIdList[subsetListIndex]))
                

                if table.indicesCount == 0 and idx == 0:
                    print("pie")

                # skip a vertices then read b vertices
                # when b is 0 interpret it as 0x20 but not a
                # after every table add 0xa00 to b values
                # if morphSubsetIdList[subsetListIndex] == 23: print_here(file_object)
                # if morphSubsetIdList[subsetListIndex] == 26: print_here(file_object)
                for y in range(table.indicesCount): 
                    morphIndexTable = _morphIndexTable(file_object, morphSubsetIdList[subsetListIndex])


                    if morphSubsetIdList[subsetListIndex] == 23:
                        print("[", morphIndexTable.vertexSkip, ", ", morphIndexTable.vertexRead, "],")
                    # if morphSubsetIdList[subsetListIndex] == 26:
                    #   print("[", morphIndexTable.vertexSkip, ", ", morphIndexTable.vertexRead, "],")

                    morphIndicesList[-1].append(morphIndexTable)

                if (idx + 1) in morphDataTableIndexList:
                    subsetListIndex += 1
                    # print_hex(len(morphSubsetIndexList[-1]))
                    print(" ")
                    morphIndicesList.append([])

            # print(morphIndicesList[1][0].subsetIndex)
            # print("[")
            # for o in morphIndicesList[1]:
            #   print("[", o.vertexSkip, ",", o.vertexRead, "],")
            # print("]")

        #complex section

class _ModelBindPose():
    def __init__(self, section, file_object):
        self.ModelBindPoseOffset = tell(file_object)
class _ModelBuilt():
    def __init__(self, section, file_object):
        self.ukw = read_uint(file_object)
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
class _ModelIndex():
    def __init__(self, section, file_object):
        self.ModelIndexOffset = tell(file_object)
class _ModelJoint():
    def __init__(self, section, file_object):
        class _ModelJointTable():
            def __init__(self, file_object):
                self.parentId = read_ushort(file_object)
                self.siblingId = read_ushort(file_object)
                self.childId = read_ushort(file_object)
                self.ukwId = read_ushort(file_object)
                self.boneNameHash = read_uint(file_object)
                self.boneNameOffset = read_uint(file_object)
        self.ModelJointList = [_ModelJointTable(file_object) for x in range(section.length // 0x10)]                
class _ModelJointLookup():
    def __init__(self, section, file_object):
        class _ModelJointLookupTable():
            def __init__(self, file_object):
                self.boneNameHash = read_uint(file_object)
                self.boneStringId = read_uint(file_object) 
        self.ModelJointLookupList = [_ModelJointLookupTable(file_object) for x in range(section.length // 0x08)]
class _ModelLeafIds():
    def __init__(self, section, file_object):
        self.ModelLeafIdsList = [read_ushort(file_object) for x in range(section.length // 0x02)]
class _ModelLocator():
    def __init__(self, section, file_object):
        class _ModelLocatorTable():
            def __init__(self, file_object):
                igLocNameHash = read_uint(file_object)
                igLocNameOffset = read_uint(file_object)
                igLocId = read_uint(file_object)
                file_object.seek(0x34, 1)   #floats
        self.ModelLocatorList = [_ModelLocatorTable(file_object) for x in range(section.length // 0x40)]
class _ModelLocatorLookup():
    def __init__(self, section, file_object):
        class _ModelLocatorLookupTable():
            def __init__(self, file_object):
                self.igLocHash = read_uint(file_object)
                self.igLocParentId = read_uint(file_object)
        self.ModelLocatorLookupList = [_ModelLocatorLookupTable(file_object) for x in range(section.length // 0x08)]
class _ModelLook():
    def __init__(self, section, file_object):
        class _table():
            def __init__(self, file_object):
                self.subsetIndex = read_ushort(file_object)
                self.subsetCount = read_ushort(file_object)
        self.ModelLookList = [[_table(file_object) for y in range(0x08)] for x in range(section.length // 0x20)]
        print("ModelLook                  count: {0:4x}".format(len(self.ModelLookList)))
        #several groups of _table lists defined by ModelLookGroup
        #first group refers to all subsets for model, subsequent groups only refer to subsets for each body part
        #each index of group is for a specific lod, 0 being the highest, 5 being the lowest, range is 8 bc either padding or more possible lods
class _ModelLookBuilt():
    def __init__(self, section, file_object):
        class _ModelLookBuiltTable():
            def __init__(self, file_object):
                self.ukwOffset = read_ulonglong(file_object)
                self.ukwOffset2 = read_ulonglong(file_object)
                self.ukwOffset3 = read_ulonglong(file_object)
                self.ukwOffset4 = read_ulonglong(file_object)
                self.ukwOffset5 = read_ulonglong(file_object)
                self.ukwOffset6 = read_ulonglong(file_object)
                self.ukwOffset7 = read_ulonglong(file_object)
                self.ukwCount = read_ushort(file_object)
                self.ukwCount2 = read_ushort(file_object)
                self.ukwCount3 = read_ushort(file_object)
                self.ukwCount4 = read_ushort(file_object)
                self.ukwCount5 = read_uint(file_object)
                self.ukwNameHash = read_uint(file_object)   #common btw multiple files
                self.modelLookNameHash = read_uint(file_object)
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
                self.groupNameHash = read_uint(file_object)
                self.groupNameOffset = read_uint(file_object)
        self.modelLookGroupCount = read_byte(file_object)
        self.modelLookGroupList = [_ModelLookGroupTable(file_object) for x in range(self.modelLookGroupCount)]
        self.modelLookIdList = []
        for modelLookGroup in self.modelLookGroupList:
            file_object.seek(section.offset + modelLookGroup.modelLookIdOffset + 1)
            self.modelLookIdList.append([read_ushort(file_object) for y in range(modelLookGroup.modelLookIdCount)])
class _ModelMaterial():
    def __init__(self, section, file_object):
        self.ModelMaterialOffset = tell(file_object)
class _ModelMirrorIds():
    def __init__(self, section, file_object):
        pass    #what the fuck is this format?
class _ModelPhysicsData():
    def __init__(self, section, file_object):
        self.offset = tell(file_object)
class _ModelSkinBatch():
    def __init__(self, section, file_object):
        class _ModelSkinBatchTable():
            def __init__(self, file_object):
                self.skinDataOffset = read_uint(file_object)         #relative to 0x79a2
                self.null = read_uint(file_object)
                self.null2 = read_ushort(file_object)
                self.ukw = read_ushort(file_object)
                self.skinVertexCount = read_ushort(file_object)
                self.skinVertexIndex = read_ushort(file_object)
        self.ModelSkinBatchList = [_ModelSkinBatchTable(file_object) for x in range(section.length // 0x10)]
class _ModelSkinData():
    def __init__(self, section, file_object):
        self.ModelSkinDataOffset = tell(file_object)
class _ModelSplines():
    def __init__(self, section, file_object):
        class _table():
            def __init__(self, file_object):
                self.ukw = read_uint(file_object)   #may be two shorts
                self.ukw2 = read_uint(file_object)   #may be two shorts
                self.ukw3 = read_uint(file_object)   #may be two shorts
        self.ukwList = [_table(file_object) for x in range(section.length // 0x0c)]
class _ModelSplineSubsets():
    def __init__(self, section, file_object):
        pass
        #complex section
class _ModelStdVert():
    def __init__(self, section, file_object):
        self.ModelStdVertOffset = tell(file_object)
class _ModelSubset():
    def __init__(self, section, file_object):
        class _ModelSubsetTable():
            def __init__(self, file_object):
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
                self.ukwFlag = read_byte(file_object)           #flag related to ukwIndex and ccbaff15
                self.materialId = read_ushort(file_object)
                self.skinBatchIndex = read_ushort(file_object)
                self.skinBatchCount = read_byte(file_object)
                self.ukw10 = read_byte(file_object)             #related to bindTableCount?
                self.ukw13 = read_ushort(file_object)           #count?
                self.ukw14 = read_ushort(file_object)           #offset?, increases by 0x10 every subset + 0x01 every lod
                self.ukwFloat4 = read_float(file_object)
                self.ukwFloat5 = read_float(file_object)
                self.ukwIndex = read_uint(file_object)          #references ccbaff15
                self.null = read_float(file_object)
        self.ModelSubsetList = [_ModelSubsetTable(file_object) for x in range(section.length // 0x40)]
        print("ModelSubsetCount: {0:8x}".format(len(self.ModelSubsetList)))
class _ModelTexVertShort():
    def __init__(self, section, file_object):
        self.ModelTexVertShortOffset = tell(file_object)

class _0ad3a708():
    def __init__(self, section, file_object):
        class _table():
            def __init__(self, file_object):
                self.ukwFloat = read_float(file_object)
                self.ukwFloat2 = read_float(file_object)
                self.ukwFloat3 = read_float(file_object)
                self.ukwFloat4 = read_float(file_object)
                self.ukw = read_uint(file_object)   
        self.ukwCount = read_uint(file_object)
        file_object.seek(0x0c, 1)                   #null
        self.ukwList = [_table(file_object) for x in range((section.length - 0x10) // 0x10)]
class _0ba45069():
    def __init__(self, section, file_object):
        self.ukw = read_uint(file_object)   #hash?
        self.ukw2 = read_uint(file_object)  #count?

        # print("{0:08x} length: {1:8x} ukw: {2:8x} ukw2: {3:8x}".format(section.hash, section.length, self.ukw, self.ukw2))
class _5a39fab7():
    def __init__(self, section, file_object):
        pass #couple arrays, dont feel like figuring it out
class _5e709570():
    def __init__(self, section, file_object):
        pass
class _707f1b58():
    def __init__(self, section, file_object):
        class _table():
            def __init__(self, file_object):
                file_object.seek(0x40, 1)   #matrix
                file_object.seek(0x40, 1)   #matrix2
                self.ukwNameHash = read_uint(file_object)
                self.ukw = read_ushort(file_object)
                self.ukw2 = read_ushort(file_object)
                self.ukw3 = read_ushort(file_object)
                self.ukw4 = read_ushort(file_object)
                self.ukw5 = read_uint(file_object)
        self.ukwOffset = read_uint(file_object)
        self.ukwOffset2 = read_uint(file_object)
        self.ukwCount = read_ushort(file_object)
        self.ukwCount2 = read_ushort(file_object)
        self.ukw = read_uint(file_object)
        self.ukwList = [_table(file_object) for x in range(self.ukwCount)]
        self.ukwList2 = [read_ushort(file_object) for x in range(self.ukwCount2)]
class _811902d7():
    def __init__(self, section, file_object):
        pass
class _90cdb60c():
    def __init__(self, section, file_object):
        self.ukw = read_short(file_object)      #null
        self.ModelJointCount = read_short(file_object)
        self.ModelLocatorCount = read_short(file_object)
        self.ukw4 = read_short(file_object)     #count?
        self.ukw5 = read_short(file_object)     #0xff/delimiter?
class _9a434b29():
    def __init__(self, section, file_object):
        pass    #contains subsections
class _a600c108():
    def __init__(self, section, file_object):
        pass    #stream/buffer? , shorts
class _add1cbd3():
    def __init__(self, section, file_object):
        pass    #complex, maybe pointed to within
class _b25b3163():
    def __init__(self, section, file_object):
        class _table():
            def __init__(self, file_object):
                self.ukw = read_ushort(file_object)
                self.ukw2 = read_ushort(file_object)
                self.ukw3 = read_ushort(file_object)
                self.ukw4 = read_ushort(file_object)
        self.ukwList = [_table(file_object) for x in range(section.length // 0x08)]
class _bb7303d5():
    def __init__(self, section, file_object):
        class _table():
            def __init__(self, file_object):
                self.ukw = read_uint(file_object)   #may be 64bit int idk
                self.ukw2 = read_uint(file_object)
        self.ukwList = [_table(file_object) for x in range(section.length // 0x08)]
class _ccbaff15():
    def __init__(self, section, file_object):
        # print_here(file_object)
        pass    #looks like weignt data
class _df9fdf12():
    def __init__(self, section, file_object):
        class _table():
            def __init__(self, file_object):
                self.ukw = read_uint(file_object)   #offset?
                self.ukw2 = read_uint(file_object)  #count?, same as subset count per look group
                self.ukw3 = read_uint(file_object)  #offset/index?
                self.ukw4 = read_uint(file_object)  #count?
        self.ukwList = [_table(file_object) for x in range(section.length // 0x10)]     #same count as look group

clean_scene()
os.system("cls")

filePath = r"D:\models\ripped\ratchet and clank rift apart\characters\hero\hero_ratchet\hero_ratchet.model"
f = open(filePath, "rb")

_1TAD = read_fixed_string(f, 4)
fileTypeHash = read_uint(f)
fileLength = read_uint(f)
tableCount = read_uint(f)

sectionTableList = [_sectionTable(f) for x in range(tableCount)]
for section in sectionTableList:
    f.seek(section.offset)
    match section.hash:
        case 0x06eb7efc: ModelLook = _ModelLook(section, f)
        case 0x0859863d: ModelIndex = _ModelIndex(section, f)
        case 0x0ad3a708: _0ad3a708(section, f)
        case 0x0ba45069: _0ba45069(section, f)
        case 0x15df9d3b: ModelJoint = _ModelJoint(section, f)
        case 0x27ca5246: ModelSplines = _ModelSplines(section, f)
        case 0x283d0383: ModelBuilt = _ModelBuilt(section, f)
        case 0x3250bb80: ModelMaterial = _ModelMaterial(section, f)
#        case 0x380a5744: ModelAnimMorphInfo = _ModelAnimMorphInfo(section, f)
        case 0x3c9dabdf: ModelSplineSubsets =_ModelSplineSubsets(section, f)
        case 0x4ccea4ad: ModelLookGroup = _ModelLookGroup(section, f)
        case 0x5a39fab7: _5a39fab7(section, f)
        case 0x5cba9de9: ModelColVert = _ModelColVert(section, f)
#        case 0x5e709570: ModelAnimMorphData = _5e709570(section, f)
#        case 0xa600c108: ModelAnimMorphIndices = _ModelAnimMorphIndices(section, f)
        case 0x6b855eed: ModelTexVertShort = _ModelTexVertShort(section, f)
        case 0x707f1b58: _707f1b58(section, f)
        case 0x731cbc2e: ModelLocatorLookup = _ModelLocatorLookup(section, f)
        case 0x78d9cbde: ModelSubset = _ModelSubset(section, f)
        case 0x811902d7: ModelLookBuilt = _ModelLookBuilt(section, f)
        case 0x90cdb60c: _90cdb60c_ = _90cdb60c(section, f)
        case 0x9a434b29: _9a434b29(section, f)
        case 0x9f614fab: ModelLocator = _ModelLocator(section, f)
        case 0xa98be69b: ModelStdVert = _ModelStdVert(section, f)
        case 0xadd1cbd3: _add1cbd3(section, f)
        case 0xb25b3163: _b25b3163(section, f)
        case 0xb7380e8c: ModelLeafIds = _ModelLeafIds(section, f)
        case 0xbb7303d5: _bb7303d5(section, f)
        case 0xc5354b60: ModelMirrorIds = _ModelMirrorIds(section, f)
        case 0xc61b1ff5: ModelSkinBatch = _ModelSkinBatch(section, f)
        case 0xccbaff15: _ccbaff15(section, f)
        case 0xdca379a2: ModelSkinData = _ModelSkinData(section, f)
        case 0xdcc88a19: ModelBindPose = _ModelBindPose(section, f)
        case 0xdf9fdf12: _df9fdf12(section, f)
        case 0xee31971c: ModelJointLookup = _ModelJointLookup(section, f)
        case 0xefd92e68: ModelPhysicsData = _ModelPhysicsData(section, f)
        case _:
            print("Unknown hash: {0:08x}    offset: {1:8x}  length: {2:8x}".format(section.hash, section.offset, section.length))

modelScale = 1

subsetCollection = bpy.data.collections.new("subsets")             #create collection within blender
bpy.context.scene.collection.children.link(subsetCollection)       #add collection to scene

lookSelection = 4
lodSelection = 0

print("LookCount: {0:2d}".format(len(ModelLook.ModelLookList)))
#for x in range(len(ModelLook.ModelLookList)): print("{0:04d}".format(x), getString(f, ModelLookBuilt.ModelLookBuiltList[x].modelLookNameOffset))

subsetSelectionList = [26]

subsetSelection = ModelLook.ModelLookList[lookSelection][lodSelection]
for x in range(subsetSelection.subsetIndex, (subsetSelection.subsetIndex + subsetSelection.subsetCount)):
#for x in range(len(ModelSubset.ModelSubsetList)):
#for x in subsetSelectionList:
    modelSubset = ModelSubset.ModelSubsetList[x]    
    
    #print("0x{0:04x}".format(x))
    
    vertexList = []
    normalList = []
    uvList = []
    
    f.seek(ModelMaterial.ModelMaterialOffset + (0x10 * modelSubset.materialId))
    materialPath = getString(f, read_ulonglong(f))
    materialName = getString(f, read_ulonglong(f))
    
    f.seek(ModelStdVert.ModelStdVertOffset + modelSubset.vertexIndex * 0x10)
#    print((hex(tell(f))), (hex(modelSubset.vertexCount)))
    for y in range(modelSubset.vertexCount):
        vx = read_short(f) * ModelBuilt.vertexScale
        vy = read_short(f) * ModelBuilt.vertexScale
        vz = read_short(f) * ModelBuilt.vertexScale
        vw = read_short(f) * ModelBuilt.vertexScale
        normals = read_uint(f)
        tu = read_short(f) / 1024.0    #sometimes 16384.0
        tv = read_short(f) / 1024.0

        vertexList.append(Vector([vx,vy,vz]) * modelScale)
        uvList.append(Vector([tu,1-tv]))
        normalList.append(normals)
    
    indexList = []
    f.seek(ModelIndex.ModelIndexOffset + modelSubset.faceIndex * 0x02)
    for y in range(modelSubset.faceCount // 3):
        fa = read_ushort(f)
        fb = read_ushort(f)
        fc = read_ushort(f)

        if modelSubset.ukw9 == 0x01: indexList.append([fa - modelSubset.vertexIndex,fb - modelSubset.vertexIndex,fc - modelSubset.vertexIndex])
        else: indexList.append([fa,fb,fc])
    
    meshName = getString(f, ModelLookBuilt.ModelLookBuiltList[lookSelection].modelLookNameOffset)
#    meshName = materialName
#    meshName = "{0:02d}".format(x)
    meshName = str(modelSubset.ukw10)

    new_mesh = bpy.data.meshes.new(meshName)
    new_mesh.from_pydata(vertexList, [], indexList)
    new_mesh.use_auto_smooth = True

    new_mesh.uv_layers.new()
    uv_layer = new_mesh.uv_layers.active.data
    for loop in new_mesh.loops:
        uv_layer[loop.index].uv = uvList[loop.vertex_index]

    mesh_obj = bpy.data.objects.new(meshName, new_mesh)
    subsetCollection.objects.link(mesh_obj)


print("Last read @ {0:x}".format(tell(f)))