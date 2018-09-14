# Embedded file name: scripts/common/Lib/plat-mac/Carbon/LaunchServices.py


def FOUR_CHAR_CODE(x):
    return x


from Carbon.Files import *
kLSRequestAllInfo = -1
kLSRolesAll = -1
kLSUnknownType = FOUR_CHAR_CODE('\x00\x00\x00\x00')
kLSUnknownCreator = FOUR_CHAR_CODE('\x00\x00\x00\x00')
kLSInvalidExtensionIndex = -1
kLSUnknownErr = -10810
kLSNotAnApplicationErr = -10811
kLSNotInitializedErr = -10812
kLSDataUnavailableErr = -10813
kLSApplicationNotFoundErr = -10814
kLSUnknownTypeErr = -10815
kLSDataTooOldErr = -10816
kLSDataErr = -10817
kLSLaunchInProgressErr = -10818
kLSNotRegisteredErr = -10819
kLSAppDoesNotClaimTypeErr = -10820
kLSAppDoesNotSupportSchemeWarning = -10821
kLSServerCommunicationErr = -10822
kLSCannotSetInfoErr = -10823
kLSInitializeDefaults = 1
kLSMinCatInfoBitmap = kFSCatInfoNodeFlags | kFSCatInfoParentDirID | kFSCatInfoFinderInfo | kFSCatInfoFinderXInfo
kLSRequestExtension = 1
kLSRequestTypeCreator = 2
kLSRequestBasicFlagsOnly = 4
kLSRequestAppTypeFlags = 8
kLSRequestAllFlags = 16
kLSRequestIconAndKind = 32
kLSRequestExtensionFlagsOnly = 64
kLSItemInfoIsPlainFile = 1
kLSItemInfoIsPackage = 2
kLSItemInfoIsApplication = 4
kLSItemInfoIsContainer = 8
kLSItemInfoIsAliasFile = 16
kLSItemInfoIsSymlink = 32
kLSItemInfoIsInvisible = 64
kLSItemInfoIsNativeApp = 128
kLSItemInfoIsClassicApp = 256
kLSItemInfoAppPrefersNative = 512
kLSItemInfoAppPrefersClassic = 1024
kLSItemInfoAppIsScriptable = 2048
kLSItemInfoIsVolume = 4096
kLSItemInfoExtensionIsHidden = 1048576
kLSRolesNone = 1
kLSRolesViewer = 2
kLSRolesEditor = 4
kLSUnknownKindID = 0
kLSAcceptDefault = 1
kLSAcceptAllowLoginUI = 2
kLSLaunchDefaults = 1
kLSLaunchAndPrint = 2
kLSLaunchReserved2 = 4
kLSLaunchReserved3 = 8
kLSLaunchReserved4 = 16
kLSLaunchReserved5 = 32
kLSLaunchReserved6 = 64
kLSLaunchInhibitBGOnly = 128
kLSLaunchDontAddToRecents = 256
kLSLaunchDontSwitch = 512
kLSLaunchNoParams = 2048
kLSLaunchAsync = 65536
kLSLaunchStartClassic = 131072
kLSLaunchInClassic = 262144
kLSLaunchNewInstance = 524288
kLSLaunchAndHide = 1048576
kLSLaunchAndHideOthers = 2097152
