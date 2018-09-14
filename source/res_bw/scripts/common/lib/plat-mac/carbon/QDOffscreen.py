# Embedded file name: scripts/common/Lib/plat-mac/Carbon/QDOffscreen.py


def FOUR_CHAR_CODE(x):
    return x


pixPurgeBit = 0
noNewDeviceBit = 1
useTempMemBit = 2
keepLocalBit = 3
useDistantHdwrMemBit = 4
useLocalHdwrMemBit = 5
pixelsPurgeableBit = 6
pixelsLockedBit = 7
mapPixBit = 16
newDepthBit = 17
alignPixBit = 18
newRowBytesBit = 19
reallocPixBit = 20
clipPixBit = 28
stretchPixBit = 29
ditherPixBit = 30
gwFlagErrBit = 31
pixPurge = 1L << pixPurgeBit
noNewDevice = 1L << noNewDeviceBit
useTempMem = 1L << useTempMemBit
keepLocal = 1L << keepLocalBit
useDistantHdwrMem = 1L << useDistantHdwrMemBit
useLocalHdwrMem = 1L << useLocalHdwrMemBit
pixelsPurgeable = 1L << pixelsPurgeableBit
pixelsLocked = 1L << pixelsLockedBit
kAllocDirectDrawSurface = 16384L
mapPix = 1L << mapPixBit
newDepth = 1L << newDepthBit
alignPix = 1L << alignPixBit
newRowBytes = 1L << newRowBytesBit
reallocPix = 1L << reallocPixBit
clipPix = 1L << clipPixBit
stretchPix = 1L << stretchPixBit
ditherPix = 1L << ditherPixBit
gwFlagErr = 1L << gwFlagErrBit
deviceIsIndirect = 1L
deviceNeedsLock = 2L
deviceIsStatic = 4L
deviceIsExternalBuffer = 8L
deviceIsDDSurface = 16L
deviceIsDCISurface = 32L
deviceIsGDISurface = 64L
deviceIsAScreen = 128L
deviceIsOverlaySurface = 256L
