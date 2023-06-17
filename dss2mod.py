# Converts DSS (Digital Sound Studio) modules to MOD (ProTracker) modules.
# The DSS fileformat is a less capable module format (no vibrato? seriously?)
# As far as I am aware, the music composition tool that used this format
# is lost media at the moment.
# I have not fully reverse-engineered the fileformat yet. By that, I mean some
# files have missing effects.

import sys
import math

with open(sys.argv[2], "wb+") as MODfile:
    with open(sys.argv[1], "rb") as DSSfile:
        if str(DSSfile.read(4), encoding="utf-8") == "MMU2":
            # TODO: version checking
            # everything below is v3 specific
            DSSfile.seek(10)
            MODfile.seek(20)
            for i in range(31):
                smpName = DSSfile.read(22)
                DSSfile.seek(10, 1)
                smpLenALp = DSSfile.read(2)
                smpLength = DSSfile.read(2)
                DSSfile.seek(2, 1)
                smpRepStart = DSSfile.read(2)
                smpRepLength = DSSfile.read(2)
                smpLength = int.from_bytes(smpLength, byteorder="big")
                smpLenALp = int.from_bytes(smpLenALp, byteorder="big")
                smpRepStart = int.from_bytes(smpRepStart, byteorder="big")
                smpRepLength = int.from_bytes(smpRepLength, byteorder="big")
                smpFineAndVolume = DSSfile.read(2)
                if smpRepLength > 1:
                    smpLength = smpLength + smpRepLength + smpLenALp
                smpLength = smpLength.to_bytes(2, byteorder="big")
                smpRepStart = smpRepStart.to_bytes(2, byteorder="big")
                smpRepLength = smpRepLength.to_bytes(2, byteorder="big")
                DSSfile.seek(2, 1)
                MODfile.write(smpName)
                MODfile.write(smpLength)
                MODfile.write(smpFineAndVolume)
                MODfile.write(smpRepStart)
                MODfile.write(smpRepLength)
            restPos = DSSfile.read(1)
            # some of the following code fixes problems in some songs
            # this includes two of zero reality inc's songs
            numOrders = int.from_bytes(DSSfile.read(1), byteorder="big")
            MODfile.write(numOrders.to_bytes(1, byteorder="big"))
            MODfile.write(restPos)
            numPatterns = 0
            MODfile.write(bytes(numOrders))
            MODfile.seek(-numOrders, 1)
            for i in range(numOrders):
                patternNumber = int.from_bytes(DSSfile.read(1), byteorder="big")
                MODfile.write(patternNumber.to_bytes(1, byteorder="big"))
                if patternNumber > numPatterns:
                    numPatterns = patternNumber
            MODfile.write(bytes(128-numOrders))
            MODfile.write(b"M.K.")
            DSSfile.seek(1566)
            for patNum in range(numPatterns + 1):
                for chnlNum in range(4):
                    for rowNum in range(64):
                        DSSevB1 = int.from_bytes(DSSfile.read(1), byteorder="big")
                        DSSevB2 = int.from_bytes(DSSfile.read(1), byteorder="big")
                        DSSevB3 = int.from_bytes(DSSfile.read(1), byteorder="big")
                        DSSevB4 = int.from_bytes(DSSfile.read(1), byteorder="big")
                        if (DSSevB1 & 7 == 0) and (DSSevB2 == 0):
                            # see also: the weird f@@kery that goes on in
                            # Gregory Mignon's "More Opium"
                            DSSevB1 = 0
                        if (DSSevB1 & 7 == 7) and (DSSevB2 == 255):
                            DSSevB1 = 0
                            DSSevB2 = 0
                            DSSevB3 = 3
                            DSSevB4 = 0
                        if DSSevB3 == 0:
                            DSSevB3 = 0
                        elif DSSevB3 == 1:
                            DSSevB3 = 1
                        elif DSSevB3 == 2:
                            DSSevB3 = 2
                        elif DSSevB3 == 3:
                            DSSevB3 = 12
                        elif DSSevB3 == 5:
                            DSSevB3 = 15
                        elif DSSevB3 == 6:
                            DSSevB3 = 13
                            # below line stops issues in color.dss
                            DSSevB4 = 0
                        elif DSSevB3 == 7:
                            DSSevB3 = 14
                            DSSevB4 = DSSevB4 & 15
                        elif DSSevB3 == 11:
                            DSSevB3 = 15
                        elif DSSevB3 == 14:
                            DSSevB3 = 10
                            DSSevB4 = (DSSevB4 << 4) & 240
                        elif DSSevB3 == 15:
                            DSSevB3 = 10
                            DSSevB4 = DSSevB4 & 15
                        elif DSSevB3 == 20:
                            DSSevB3 = 14
                            DSSevB4 = 96
                        elif DSSevB3 == 21:
                            DSSevB3 = 14
                            DSSevB4 = DSSevB4 & 15
                            DSSevB4 += 96
                        elif DSSevB3 == 22:
                            DSSevB3 = 14
                            DSSevB4 = DSSevB4 & 15
                            DSSevB4 += 144
                        elif DSSevB3 == 23:
                            DSSevB3 = 14
                            DSSevB4 = DSSevB4 & 15
                            DSSevB4 += 208
                        elif DSSevB3 == 24:
                            DSSevB3 = 14
                            DSSevB4 = DSSevB4 & 15
                            DSSevB4 += 192
                        elif DSSevB3 == 25:
                            DSSevB3 = 9
                        elif DSSevB3 == 27:
                            DSSevB3 = 3
                        else:
                            DSSevB3 = 0
                            DSSevB4 = 0
                        # leftovers from reverse engineering effect numbers
                        # use this to find more effects
                        #if (DSSevB3 >= 240) and (DSSevB3 < 256):
                        #    DSSevB3 -= 240
                        #else:
                        #    DSSevB3 = 0
                        #    DSSevB4 = 0
                        MODevB1 = (((DSSevB1 >> 3) & 16)) + (DSSevB1 & 7)
                        MODevB2 = DSSevB2
                        MODevB3 = DSSevB3 + (((DSSevB1 >> 3) & 15) << 4)
                        MODevB4 = DSSevB4
                        MODfile.write(MODevB1.to_bytes(1, byteorder="big"))
                        MODfile.write(MODevB2.to_bytes(1, byteorder="big"))
                        MODfile.write(MODevB3.to_bytes(1, byteorder="big"))
                        MODfile.write(MODevB4.to_bytes(1, byteorder="big"))
            MODfile.write(DSSfile.read())
