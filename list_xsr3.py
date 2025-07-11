#!/usr/bin/env python3
blocksize=0x40000//0x200*0x210
pagesize=0x210

import os
import sys
from io import BytesIO

STL_SECTOR_SIZE = 512
STL_MAX_SAM_ENTRIES = 128


class structhelper_io:
    pos = 0

    def __init__(self, data: bytes = None, direction='little'):
        self.data = BytesIO(bytearray(data))
        self.direction = direction

    def setdata(self, data, offset=0):
        self.pos = offset
        self.data = data

    def split_4bit(self, direction=None):
        tmp = self.data.read(1)[0]
        return (tmp >> 4) & 0xF, tmp & 0xF

    def qword(self, direction=None):
        if direction is None:
            direction = self.direction
        dat = int.from_bytes(self.data.read(8), direction)
        return dat

    def signed_qword(self, direction=None):
        if direction is None:
            direction = self.direction
        dat = int.from_bytes(self.data.read(8), direction, signed=True)
        return dat

    def dword(self, direction=None):
        if direction is None:
            direction = self.direction
        dat = int.from_bytes(self.data.read(4), direction)
        return dat

    def signed_dword(self, direction=None):
        if direction is None:
            direction = self.direction
        dat = int.from_bytes(self.data.read(4), direction, signed=True)
        return dat

    def dwords(self, dwords=1, direction=None):
        if direction is None:
            direction = self.direction
        dat = [int.from_bytes(self.data.read(4), direction) for _ in range(dwords)]
        return dat

    def short(self, direction=None):
        if direction is None:
            direction = self.direction
        dat = int.from_bytes(self.data.read(2), direction)
        return dat

    def signed_short(self, direction=None):
        if direction is None:
            direction = self.direction
        dat = int.from_bytes(self.data.read(2), direction, signed=True)
        return dat

    def shorts(self, shorts, direction=None):
        if direction is None:
            direction = self.direction
        dat = [int.from_bytes(self.data.read(2), direction) for _ in range(shorts)]
        return dat

    def byte(self):
        dat = self.data.read(1)[0]
        return dat

    def read(self, length=0):
        if length == 0:
            return self.data.read()
        return self.data.read(length)

    def bytes(self, rlen=1):
        dat = self.data.read(rlen)
        if dat == b'':
            return dat
        if rlen == 1:
            return dat[0]
        return dat

    def signed_bytes(self, rlen=1):
        dat = [int.from_bytes(self.data.read(1), 'little', signed=True) for _ in range(rlen)]
        if dat == b'':
            return dat
        if rlen == 1:
            return dat[0]
        return dat

    def string(self, rlen=1):
        dat = self.data.read(rlen)
        return dat

    def getpos(self):
        return self.data.tell()

    def seek(self, pos):
        self.data.seek(pos)


class STLConfig3:
    def __init__(self, st):
        self.nFillFactor = st.short()  # LogSctsPerUnit : UsableSctsPerUnit
        # Percentage, Full Usage Fill Factor = 100
        self.nSnapshots = st.short()  # The number of snapshot in a unit
        # NUM_OF_SNAPSHOT_1 or NUM_OF_SNAPSHOT_4
        self.nNumOfRsvUnits = st.dword()  # Reserved Units, should be >= 2
        self.nBlksPerUnit = st.dword()  # Maximum sectors per Unit is 256
        self.unknown = st.dword()


class SAMT:
    def __init__(self, st):
        self.valF0 = st.byte()  # Value 0xF0
        self.nDepth = st.byte()  # The depth of the virtual unit
        self.nOffset = st.byte()  # The offset in the virtual unit                */


class EUH3:
    def __init__(self, data):
        st = structhelper_io(bytearray(data))
        self.stCfg = STLConfig3(st)
        self.nXsrSignature = st.dword()
        nInvertedXsrSignature = st.dword()
        self.nLun = st.dword()
        nInvertedLun = st.dword()
        self.nDepth1 = st.short()
        self.nDepth2 = st.short()
        nInvertedDepth1 = st.short()
        nInvertedDepth2 = st.short()
        self.nReadyMark = st.dword()
        nInvertedReadyMark = st.dword()
        self.nZeroCount = st.dword()
        nInvertedZeroCount = st.dword()
        self.nECNT = st.dword()
        nInvertedECNT = st.dword()
        # self.nPadding = st.byte()
        # self.nReserved8 = st.byte()
        # self.nReserved16 = st.short()
        self.nPartID = st.dword()
        nInvertedPartID = st.dword()

        self.valid = self.nDepth1 == (0x10000 - nInvertedDepth1) - 1
        if self.valid:
            # STL config
            # aRsv = st.bytes(STL_SECTOR_SIZE - 4 * 3 - (4 * 15) - STL_MAX_SAM_ENTRIES * 2)
            aRsv = st.bytes(0x1C8)
            # this number of aRsv entries is used in Scanunitheader in STLinterface file
            # they must be same
            self.aSAM = [SAMT(st) for _ in range(STL_MAX_SAM_ENTRIES)]

def main():
    with open("../1.3gp","rb") as rf:
        data=rf.read()
    with open("flash.bin","rb") as rf:
        mdata=rf.read()
        for pos in range(0,len(data),0x200):
            ridx=mdata.find(data[pos:pos+0x200])
            if ridx!=-1:
                pageoffset = ridx//pagesize*pagesize
                blockoffset = ridx//blocksize*blocksize
                idx = (((pageoffset-blockoffset))//0x840)-1
                spare = mdata[pageoffset+0x200:pageoffset+0x210]
                spareblock = int.from_bytes(spare[2:4],'little')
                euh3 = EUH3(mdata[blockoffset:blockoffset+0x840])
                age = int.from_bytes(spare[4:5],'little')
                flag = int.from_bytes(spare[14:15],'little')
                st = euh3.aSAM[idx]
                #print(f"{hex(pos//0x200)}:{hex(pageoffset)}:{hex(blockoffset)} {hex(spareblock)} {hex(age)} -> depth={hex(st.nDepth)} nOffset={hex(st.nOffset)} valF0={hex(st.valF0)}")
                print(f"{hex(pos // 0x200)}:{hex(pageoffset)}:{hex(blockoffset)} {hex(spareblock)} {hex(age)} {hex(flag)}-> {hex(euh3.nLun)} {hex(euh3.nPartID)} {hex(euh3.nDepth1)} {hex(euh3.nDepth2)} {hex(euh3.nECNT)}")
            else:
                print(f"{hex(pos//0x200)}:{pageoffset}:{blockoffset} missing")

if __name__ == "__main__":
    main()