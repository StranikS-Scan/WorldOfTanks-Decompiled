# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/plat-mac/Carbon/Dragconst.py


def FOUR_CHAR_CODE(x):
    return x


from Carbon.TextEdit import *
from Carbon.QuickDraw import *
fkDragActionAll = -1
kDragHasLeftSenderWindow = 1
kDragInsideSenderApplication = 2
kDragInsideSenderWindow = 4
kDragRegionAndImage = 16
flavorSenderOnly = 1
flavorSenderTranslated = 2
flavorNotSaved = 4
flavorSystemTranslated = 256
kDragHasLeftSenderWindow = 1L
kDragInsideSenderApplication = 2L
kDragInsideSenderWindow = 4L
kDragBehaviorNone = 0
kDragBehaviorZoomBackAnimation = 1L
kDragRegionAndImage = 16L
kDragStandardTranslucency = 0L
kDragDarkTranslucency = 1L
kDragDarkerTranslucency = 2L
kDragOpaqueTranslucency = 3L
kDragRegionBegin = 1
kDragRegionDraw = 2
kDragRegionHide = 3
kDragRegionIdle = 4
kDragRegionEnd = 5
kZoomNoAcceleration = 0
kZoomAccelerate = 1
kZoomDecelerate = 2
flavorSenderOnly = 1
flavorSenderTranslated = 2
flavorNotSaved = 4
flavorSystemTranslated = 256
flavorDataPromised = 512
kDragFlavorTypeHFS = FOUR_CHAR_CODE('hfs ')
kDragFlavorTypePromiseHFS = FOUR_CHAR_CODE('phfs')
flavorTypeHFS = kDragFlavorTypeHFS
flavorTypePromiseHFS = kDragFlavorTypePromiseHFS
kDragPromisedFlavorFindFile = FOUR_CHAR_CODE('rWm1')
kDragPromisedFlavor = FOUR_CHAR_CODE('fssP')
kDragPseudoCreatorVolumeOrDirectory = FOUR_CHAR_CODE('MACS')
kDragPseudoFileTypeVolume = FOUR_CHAR_CODE('disk')
kDragPseudoFileTypeDirectory = FOUR_CHAR_CODE('fold')
flavorTypeDirectory = FOUR_CHAR_CODE('diry')
kFlavorTypeClippingName = FOUR_CHAR_CODE('clnm')
kFlavorTypeClippingFilename = FOUR_CHAR_CODE('clfn')
kFlavorTypeDragToTrashOnly = FOUR_CHAR_CODE('fdtt')
kFlavorTypeFinderNoTrackingBehavior = FOUR_CHAR_CODE('fntb')
kDragTrackingEnterHandler = 1
kDragTrackingEnterWindow = 2
kDragTrackingInWindow = 3
kDragTrackingLeaveWindow = 4
kDragTrackingLeaveHandler = 5
kDragActionNothing = 0L
kDragActionCopy = 1L
kDragActionAlias = 2L
kDragActionGeneric = 4L
kDragActionPrivate = 8L
kDragActionMove = 16L
kDragActionDelete = 32L
dragHasLeftSenderWindow = kDragHasLeftSenderWindow
dragInsideSenderApplication = kDragInsideSenderApplication
dragInsideSenderWindow = kDragInsideSenderWindow
dragTrackingEnterHandler = kDragTrackingEnterHandler
dragTrackingEnterWindow = kDragTrackingEnterWindow
dragTrackingInWindow = kDragTrackingInWindow
dragTrackingLeaveWindow = kDragTrackingLeaveWindow
dragTrackingLeaveHandler = kDragTrackingLeaveHandler
dragRegionBegin = kDragRegionBegin
dragRegionDraw = kDragRegionDraw
dragRegionHide = kDragRegionHide
dragRegionIdle = kDragRegionIdle
dragRegionEnd = kDragRegionEnd
zoomNoAcceleration = kZoomNoAcceleration
zoomAccelerate = kZoomAccelerate
zoomDecelerate = kZoomDecelerate
kDragStandardImage = kDragStandardTranslucency
kDragDarkImage = kDragDarkTranslucency
kDragDarkerImage = kDragDarkerTranslucency
kDragOpaqueImage = kDragOpaqueTranslucency
