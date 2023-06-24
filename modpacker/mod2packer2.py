# mod2packer.py
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
    "1CHN","2CHN","3CHN","M.K.","5CHN","6CHN","7CHN","8CHN",
    "9CHN","10CH","11CH","12CH","13CH","14CH","15CH","16CH",
    "17CH","18CH","19CH","20CH","21CH","22CH","23CH","24CH",
    "25CH","26CH","27CH","28CH","29CH","30CH","31CH","32CH",
    "33CH","34CH","35CH","36CH","37CH","38CH","39CH","40CH",
    "41CH","42CH","43CH","44CH","45CH","46CH","47CH","48CH",
    "49CH","50CH","51CH","52CH","53CH","54CH","55CH","56CH",
    "57CH","58CH","59CH","60CH","61CH","62CH","63CH","64CH",
    "65CH","66CH","67CH","68CH","69CH","70CH","71CH","72CH",
    "73CH","74CH","75CH","76CH","77CH","78CH","79CH","80CH",
    "81CH","82CH","83CH","84CH","85CH","86CH","87CH","88CH",
    "89CH","90CH","91CH","92CH","93CH","94CH","95CH","96CH",
    "97CH","98CH","99CH"
    ]

def compareMagic(magic):
    for i in range(32):
        if magic == ModChannelsTable[i]:
            return i + 1
    return 0

def periodToNote(lower, upper):
    newPeriod = (upper << 8) + lower
    for i in range(len(ModPeriodTable)):
        if (ModPeriodTable[i] > newPeriod) and (ModPeriodTable[i+1] < newPeriod):
            return i
        if ModPeriodTable[i] == newPeriod:
            return i
    return 0 # oops, no note found!

with open(sys.argv[2], "wb+") as PTMfile:
    with open(sys.argv[1], "rb") as MODfile:
        MODfile.seek(1080)
        numChannels = compareMagic(str(MODfile.read(4), encoding="utf-8"))
        if numChannels != 0:
            PTMfile.seek(0)
            MODfile.seek(0)
            PTMfile.write(b"LMF1")
            PTMfile.write(MODfile.read(20))
            for i in range(31):
                PTMfile.write(MODfile.read(22))
                smpLenB = MODfile.read(2)
                smpLen = int.from_bytes(smpLenB, byteorder="big")
                smpHead1 = MODfile.read(1)
                defVolB = MODfile.read(1)
                smpHead2 = MODfile.read(4)
                PTMfile.write(smpLenB)
                PTMfile.write(smpHead1)
                if smpLen == 0:
                    PTMfile.write((0).to_bytes(1, byteorder="big"))
                else:
                    PTMfile.write(defVolB)
                PTMfile.write(smpHead2)
            MODfile.seek(950)
            numOrdersBytes = MODfile.read(1)
            numOrders = int.from_bytes(numOrdersBytes, byteorder="big")
            PTMfile.write(numOrdersBytes)
            restartPos = MODfile.read(1)
            PTMfile.write(restartPos)
            numPatterns = 0
            for i in range(128):
                patternNumber = int.from_bytes(MODfile.read(1), byteorder="big")
                PTMfile.write(patternNumber.to_bytes(1, byteorder="big"))
                if patternNumber > numPatterns:
                    numPatterns = patternNumber
            PTMfile.write(numChannels.to_bytes(1, byteorder="big"))
            MODfile.seek(1084)
            for patternNumber in range(numPatterns):
                for rowNumber in range(64):
                    for channelNumber in range(numChannels):
                        eventPart1 = int.from_bytes(MODfile.read(1), byteorder="little")
                        lowerPeriod = int.from_bytes(MODfile.read(1), byteorder="little")
                        eventPart3 = int.from_bytes(MODfile.read(1), byteorder="little")
                        effectParam = MODfile.read(1)
                        upperPeriod = eventPart1 & 15
                        note = periodToNote(lowerPeriod, upperPeriod)
                        instrument = (((eventPart1 & 240) << 4) + (eventPart3 & 240)) >> 4
                        effectNumber = eventPart3 & 15
                        byte1 = (note << 1) + (instrument >> 4)
                        byte2 = ((instrument & 15) << 4) + effectNumber
                        PTMfile.write(byte1.to_bytes(1, byteorder="big"))
                        PTMfile.write(byte2.to_bytes(1, byteorder="big"))
                        PTMfile.write(effectParam)
            PTMfile.write(MODfile.read())
