# Embedded file name: scripts/client/gui/shared/utils/key_mapping.py
import BigWorld
import Keys
from gui.battle_control import g_sessionProvider
BW_TO_SCALEFORM = {Keys.KEY_NONE: 666,
 Keys.KEY_MOUSE0: 0,
 Keys.KEY_MOUSE1: 1,
 Keys.KEY_MOUSE2: 2,
 Keys.KEY_MOUSE3: 3,
 Keys.KEY_MOUSE4: 4,
 Keys.KEY_MOUSE5: 5,
 Keys.KEY_MOUSE6: 6,
 Keys.KEY_MOUSE7: 7,
 Keys.KEY_A: 65,
 Keys.KEY_B: 66,
 Keys.KEY_C: 67,
 Keys.KEY_D: 68,
 Keys.KEY_E: 69,
 Keys.KEY_F: 70,
 Keys.KEY_G: 71,
 Keys.KEY_H: 72,
 Keys.KEY_I: 73,
 Keys.KEY_J: 74,
 Keys.KEY_K: 75,
 Keys.KEY_L: 76,
 Keys.KEY_M: 77,
 Keys.KEY_N: 78,
 Keys.KEY_O: 79,
 Keys.KEY_P: 80,
 Keys.KEY_Q: 81,
 Keys.KEY_R: 82,
 Keys.KEY_S: 83,
 Keys.KEY_T: 84,
 Keys.KEY_U: 85,
 Keys.KEY_V: 86,
 Keys.KEY_W: 87,
 Keys.KEY_X: 88,
 Keys.KEY_Y: 89,
 Keys.KEY_Z: 90,
 Keys.KEY_0: 48,
 Keys.KEY_1: 49,
 Keys.KEY_2: 50,
 Keys.KEY_3: 51,
 Keys.KEY_4: 52,
 Keys.KEY_5: 53,
 Keys.KEY_6: 54,
 Keys.KEY_7: 55,
 Keys.KEY_8: 56,
 Keys.KEY_9: 57,
 Keys.KEY_NUMPAD0: 96,
 Keys.KEY_NUMPAD1: 97,
 Keys.KEY_NUMPAD2: 98,
 Keys.KEY_NUMPAD3: 99,
 Keys.KEY_NUMPAD4: 100,
 Keys.KEY_NUMPAD5: 101,
 Keys.KEY_NUMPAD6: 102,
 Keys.KEY_NUMPAD7: 103,
 Keys.KEY_NUMPAD8: 104,
 Keys.KEY_NUMPAD9: 105,
 Keys.KEY_NUMPADSTAR: 106,
 Keys.KEY_ADD: 107,
 Keys.KEY_NUMPADENTER: 108,
 Keys.KEY_NUMPADMINUS: 109,
 Keys.KEY_NUMPADPERIOD: 110,
 Keys.KEY_NUMPADSLASH: 111,
 Keys.KEY_F1: 112,
 Keys.KEY_F2: 113,
 Keys.KEY_F3: 114,
 Keys.KEY_F4: 115,
 Keys.KEY_F5: 116,
 Keys.KEY_F6: 117,
 Keys.KEY_F7: 118,
 Keys.KEY_F8: 119,
 Keys.KEY_F9: 120,
 Keys.KEY_F10: 121,
 Keys.KEY_F11: 122,
 Keys.KEY_F12: 123,
 Keys.KEY_F13: 124,
 Keys.KEY_F14: 125,
 Keys.KEY_F15: 126,
 Keys.KEY_BACKSPACE: 8,
 Keys.KEY_TAB: 9,
 Keys.KEY_RETURN: 13,
 Keys.KEY_RSHIFT: 16,
 Keys.KEY_LSHIFT: 16,
 Keys.KEY_RCONTROL: 17,
 Keys.KEY_LCONTROL: 17,
 Keys.KEY_RALT: 18,
 Keys.KEY_LALT: 18,
 Keys.KEY_PAUSE: 19,
 Keys.KEY_CAPSLOCK: 20,
 Keys.KEY_ESCAPE: 27,
 Keys.KEY_SPACE: 32,
 Keys.KEY_PGUP: 33,
 Keys.KEY_PGDN: 34,
 Keys.KEY_END: 35,
 Keys.KEY_HOME: 36,
 Keys.KEY_LEFTARROW: 37,
 Keys.KEY_UPARROW: 38,
 Keys.KEY_RIGHTARROW: 39,
 Keys.KEY_DOWNARROW: 40,
 Keys.KEY_INSERT: 45,
 Keys.KEY_DELETE: 46,
 Keys.KEY_NUMLOCK: 144,
 Keys.KEY_SCROLL: 145,
 Keys.KEY_SEMICOLON: 186,
 Keys.KEY_EQUALS: 187,
 Keys.KEY_COMMA: 188,
 Keys.KEY_MINUS: 189,
 Keys.KEY_PERIOD: 190,
 Keys.KEY_SLASH: 191,
 Keys.KEY_LBRACKET: 219,
 Keys.KEY_BACKSLASH: 220,
 Keys.KEY_RBRACKET: 221,
 Keys.KEY_APOSTROPHE: 222,
 Keys.KEY_AX: 225,
 Keys.KEY_OEM_102: 225}
SCALEFORM_TO_BW = dict([ (v, k) for k, v in BW_TO_SCALEFORM.iteritems() ])
BW_TO_SCALEFORM_OVERRIDE = {Keys.KEY_NONE: 0,
 Keys.KEY_MOUSE0: 1,
 Keys.KEY_MOUSE1: 2,
 Keys.KEY_MOUSE2: 3,
 Keys.KEY_MOUSE3: 4,
 Keys.KEY_MOUSE4: 5,
 Keys.KEY_MOUSE5: 6,
 Keys.KEY_MOUSE6: 7,
 Keys.KEY_MOUSE7: 8}
SCALEFORM_TO_BW_OVERRIDE = dict([ (v, k) for k, v in BW_TO_SCALEFORM_OVERRIDE.iteritems() ])
SCALEFORM_TO_BW[16] = Keys.KEY_LSHIFT
SCALEFORM_TO_BW[17] = Keys.KEY_LCONTROL
SCALEFORM_TO_BW[18] = Keys.KEY_LALT
voidSymbol = 0

def getBigworldKey(scaleformKey):
    if g_sessionProvider.getCtx().isInBattle and scaleformKey in SCALEFORM_TO_BW_OVERRIDE:
        return SCALEFORM_TO_BW_OVERRIDE[scaleformKey]
    return SCALEFORM_TO_BW.get(scaleformKey, voidSymbol)


def getBigworldNameFromKey(bigworldKey):
    return 'KEY_%s' % BigWorld.keyToString(bigworldKey)


def getBigworldKeyFromName(bigworldName):
    return bigworldName.split('KEY_')[-1]


def getScaleformKey(bigworldKey):
    if g_sessionProvider.getCtx().isInBattle and bigworldKey in BW_TO_SCALEFORM_OVERRIDE:
        return BW_TO_SCALEFORM_OVERRIDE[bigworldKey]
    return BW_TO_SCALEFORM.get(bigworldKey, voidSymbol)
