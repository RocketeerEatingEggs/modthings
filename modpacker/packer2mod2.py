# packer2mod.py
# by RocketeerEatingEggs

import sys
import math

ModPeriodTable = [
    0, # required by the converter to add no note
    
     3424, 3232, 3048, 2880, 2712, 2560, 2416, 2280, 2152, 2032, 1920, 1812, # octave 2
     1712, 1616, 1524, 1440, 1356, 1280, 1208, 1140, 1076, 1016,  960,  906, # octave 3
      856,  808,  762,  720,  678,  640,  604,  570,  538,  508,  480,  453, # octave 4, amiga
      428,  404,  381,  360,  339,  320,  302,  285,  269,  254,  240,  226, # octave 5, amiga
      214,  202,  190,  180,  170,  160,  151,  143,  135,  127,  120,  113, # octave 6, amiga
      107,  101,   95,   90,   85,   80,   75,   71,   67,   63,   60,   56, # octave 7
       53,   50,   47,   45,   42,   40,   37,   35,   33,   31,   30,   28, # octave 8
    0
    ]

ModChannelsTable = [
    b"1CHN",b"2CHN",b"3CHN",b"M.K.",b"5CHN",b"6CHN",b"7CHN",b"8CHN",
    b"9CHN",b"10CH",b"11CH",b"12CH",b"13CH",b"14CH",b"15CH",b"16CH",
    b"17CH",b"18CH",b"19CH",b"20CH",b"21CH",b"22CH",b"23CH",b"24CH",
    b"25CH",b"26CH",b"27CH",b"28CH",b"29CH",b"30CH",b"31CH",b"32CH",
    b"33CH",b"34CH",b"35CH",b"36CH",b"37CH",b"38CH",b"39CH",b"40CH",
    b"41CH",b"42CH",b"43CH",b"44CH",b"45CH",b"46CH",b"47CH",b"48CH",
    b"49CH",b"50CH",b"51CH",b"52CH",b"53CH",b"54CH",b"55CH",b"56CH",
    b"57CH",b"58CH",b"59CH",b"60CH",b"61CH",b"62CH",b"63CH",b"64CH",
    b"65CH",b"66CH",b"67CH",b"68CH",b"69CH",b"70CH",b"71CH",b"72CH",
    b"73CH",b"74CH",b"75CH",b"76CH",b"77CH",b"78CH",b"79CH",b"80CH",
    b"81CH",b"82CH",b"83CH",b"84CH",b"85CH",b"86CH",b"87CH",b"88CH",
    b"89CH",b"90CH",b"91CH",b"92CH",b"93CH",b"94CH",b"95CH",b"96CH",
    b"97CH",b"98CH",b"99CH"
    ]

def periodToNote(lower, upper):
    newPeriod = (upper << 8) + lower
    for i in range(len(ModPeriodTable)):
        if (ModPeriodTable[i] > newPeriod) and (ModPeriodTable[i+1] < newPeriod):
            return i
        if ModPeriodTable[i] == newPeriod:
            return i
    return 0 # oops, no note found!

with open(sys.argv[2], "wb+") as MODfile:
    with open(sys.argv[1], "rb") as MKfile:
        if str(MKfile.read(4), encoding="utf-8") == "LMF1":
            MKfile.seek(4)
            MODfile.write(MKfile.read(20))
            smpLengths = []
            for i in range(31):
                MODfile.write(MKfile.read(22))
                smpLengthBytes = MKfile.read(2)
                smpLength = int.from_bytes(smpLengthBytes, byteorder="big")
                smpLengths.append(smpLength*2)
                smpHead = MKfile.read(6)
                MODfile.write(smpLengthBytes)
                MODfile.write(smpHead)
            numOrdersBytes = MKfile.read(1)
            numOrders = int.from_bytes(numOrdersBytes, byteorder="big")
            MODfile.write(numOrdersBytes)
            restartPos = MKfile.read(1)
            MODfile.write(restartPos)
            numPatterns = 0
            for i in range(128):
                patternNumber = int.from_bytes(MKfile.read(1), byteorder="big")
                MODfile.write(patternNumber.to_bytes(1, byteorder="big"))
                if patternNumber > numPatterns:
                    numPatterns = patternNumber
            numChannels = int.from_bytes(MKfile.read(1), byteorder="big")
            MODfile.write(ModChannelsTable[numChannels-1])
            for patternNumber in range(numPatterns):
                for rowNumber in range(64):
                    for channelNumber in range(numChannels):
                        evP1 = int.from_bytes(MKfile.read(1), byteorder="big")
                        evP2 = int.from_bytes(MKfile.read(1), byteorder="big")
                        evP3 = MKfile.read(1)
                        note = (evP1 & 254) >> 1
                        inst1 = (evP1 & 1) << 4
                        inst2 = evP2 & 240
                        fxTp = evP2 & 15
                        period = ModPeriodTable[note]
                        byte1 = inst1 + (period >> 8)
                        byte2 = period & 255
                        byte3 = inst2 + fxTp
                        MODfile.write(byte1.to_bytes(1, byteorder="big"))
                        MODfile.write(byte2.to_bytes(1, byteorder="big"))
                        MODfile.write(byte3.to_bytes(1, byteorder="big"))
                        MODfile.write(evP3)
            MODfile.write(MKfile.read())
