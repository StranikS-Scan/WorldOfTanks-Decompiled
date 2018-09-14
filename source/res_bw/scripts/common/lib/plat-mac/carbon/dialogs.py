# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/plat-mac/Carbon/Dialogs.py


def FOUR_CHAR_CODE(x):
    return x


kControlDialogItem = 4
kButtonDialogItem = kControlDialogItem | 0
kCheckBoxDialogItem = kControlDialogItem | 1
kRadioButtonDialogItem = kControlDialogItem | 2
kResourceControlDialogItem = kControlDialogItem | 3
kStaticTextDialogItem = 8
kEditTextDialogItem = 16
kIconDialogItem = 32
kPictureDialogItem = 64
kUserDialogItem = 0
kHelpDialogItem = 1
kItemDisableBit = 128
ctrlItem = 4
btnCtrl = 0
chkCtrl = 1
radCtrl = 2
resCtrl = 3
statText = 8
editText = 16
iconItem = 32
picItem = 64
userItem = 0
itemDisable = 128
kStdOkItemIndex = 1
kStdCancelItemIndex = 2
ok = kStdOkItemIndex
cancel = kStdCancelItemIndex
kStopIcon = 0
kNoteIcon = 1
kCautionIcon = 2
stopIcon = kStopIcon
noteIcon = kNoteIcon
cautionIcon = kCautionIcon
kOkItemIndex = 1
kCancelItemIndex = 2
overlayDITL = 0
appendDITLRight = 1
appendDITLBottom = 2
kAlertStopAlert = 0
kAlertNoteAlert = 1
kAlertCautionAlert = 2
kAlertPlainAlert = 3
kAlertDefaultOKText = -1
kAlertDefaultCancelText = -1
kAlertDefaultOtherText = -1
kAlertStdAlertOKButton = 1
kAlertStdAlertCancelButton = 2
kAlertStdAlertOtherButton = 3
kAlertStdAlertHelpButton = 4
kDialogFlagsUseThemeBackground = 1
kDialogFlagsUseControlHierarchy = 2
kDialogFlagsHandleMovableModal = 4
kDialogFlagsUseThemeControls = 8
kAlertFlagsUseThemeBackground = 1
kAlertFlagsUseControlHierarchy = 2
kAlertFlagsAlertIsMovable = 4
kAlertFlagsUseThemeControls = 8
kDialogFontNoFontStyle = 0
kDialogFontUseFontMask = 1
kDialogFontUseFaceMask = 2
kDialogFontUseSizeMask = 4
kDialogFontUseForeColorMask = 8
kDialogFontUseBackColorMask = 16
kDialogFontUseModeMask = 32
kDialogFontUseJustMask = 64
kDialogFontUseAllMask = 255
kDialogFontAddFontSizeMask = 256
kDialogFontUseFontNameMask = 512
kDialogFontAddToMetaFontMask = 1024
kDialogFontUseThemeFontIDMask = 128
kHICommandOther = FOUR_CHAR_CODE('othr')
kStdCFStringAlertVersionOne = 1
kStdAlertDoNotDisposeSheet = 1
kStdAlertDoNotAnimateOnDefault = 2
kStdAlertDoNotAnimateOnCancel = 4
kStdAlertDoNotAnimateOnOther = 8
