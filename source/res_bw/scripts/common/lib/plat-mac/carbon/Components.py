# Embedded file name: scripts/common/Lib/plat-mac/Carbon/Components.py


def FOUR_CHAR_CODE(x):
    return x


kAppleManufacturer = FOUR_CHAR_CODE('appl')
kComponentResourceType = FOUR_CHAR_CODE('thng')
kComponentAliasResourceType = FOUR_CHAR_CODE('thga')
kAnyComponentType = 0
kAnyComponentSubType = 0
kAnyComponentManufacturer = 0
kAnyComponentFlagsMask = 0
cmpIsMissing = 536870912L
cmpWantsRegisterMessage = 2147483648L
kComponentOpenSelect = -1
kComponentCloseSelect = -2
kComponentCanDoSelect = -3
kComponentVersionSelect = -4
kComponentRegisterSelect = -5
kComponentTargetSelect = -6
kComponentUnregisterSelect = -7
kComponentGetMPWorkFunctionSelect = -8
kComponentExecuteWiredActionSelect = -9
kComponentGetPublicResourceSelect = -10
componentDoAutoVersion = 1
componentWantsUnregister = 2
componentAutoVersionIncludeFlags = 4
componentHasMultiplePlatforms = 8
componentLoadResident = 16
defaultComponentIdentical = 0
defaultComponentAnyFlags = 1
defaultComponentAnyManufacturer = 2
defaultComponentAnySubType = 4
defaultComponentAnyFlagsAnyManufacturer = defaultComponentAnyFlags + defaultComponentAnyManufacturer
defaultComponentAnyFlagsAnyManufacturerAnySubType = defaultComponentAnyFlags + defaultComponentAnyManufacturer + defaultComponentAnySubType
registerComponentGlobal = 1
registerComponentNoDuplicates = 2
registerComponentAfterExisting = 4
registerComponentAliasesOnly = 8
platform68k = 1
platformPowerPC = 2
platformInterpreted = 3
platformWin32 = 4
platformPowerPCNativeEntryPoint = 5
mpWorkFlagDoWork = 1
mpWorkFlagDoCompletion = 2
mpWorkFlagCopyWorkBlock = 4
mpWorkFlagDontBlock = 8
mpWorkFlagGetProcessorCount = 16
mpWorkFlagGetIsRunning = 64
cmpAliasNoFlags = 0
cmpAliasOnlyThisFile = 1
uppComponentFunctionImplementedProcInfo = 752
uppGetComponentVersionProcInfo = 240
uppComponentSetTargetProcInfo = 1008
uppCallComponentOpenProcInfo = 1008
uppCallComponentCloseProcInfo = 1008
uppCallComponentCanDoProcInfo = 752
uppCallComponentVersionProcInfo = 240
uppCallComponentRegisterProcInfo = 240
uppCallComponentTargetProcInfo = 1008
uppCallComponentUnregisterProcInfo = 240
uppCallComponentGetMPWorkFunctionProcInfo = 4080
uppCallComponentGetPublicResourceProcInfo = 15344
