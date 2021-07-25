# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/go_back_helper.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform import MENU
from helpers import i18n
from shared_utils import CONST_CONTAINER

class BackButtonContextKeys(CONST_CONTAINER):
    BLUEPRINT_MODE = 'blueprintMode'
    NATION = 'nation'
    EXIT = 'exit'
    ROOT_CD = 'rootCD'


BACK_BTN_LABELS = {VIEW_ALIAS.LOBBY_HANGAR: 'hangar',
 VIEW_ALIAS.LOBBY_STORAGE: 'storage',
 VIEW_ALIAS.LOBBY_TECHTREE: 'techtree',
 VIEW_ALIAS.LOBBY_RESEARCH: 'research'}

def getBackBtnLabel(exitEvent, previewView, vehicleName=''):
    key = BACK_BTN_LABELS.get(previewView, 'hangar')
    if key == BACK_BTN_LABELS[VIEW_ALIAS.LOBBY_RESEARCH]:
        return i18n.makeString(MENU.viewheader_backbtn_descrlabel(key), tankName=vehicleName.upper())
    if key == BACK_BTN_LABELS[VIEW_ALIAS.LOBBY_TECHTREE]:
        key = _getBlueprintViewLabel(exitEvent, key)
    return MENU.viewheader_backbtn_descrlabel(key)


def _getBlueprintViewLabel(exitEvent, key):
    nation = exitEvent.ctx[BackButtonContextKeys.NATION]
    blueprintMode = exitEvent.ctx.get(BackButtonContextKeys.BLUEPRINT_MODE, False)
    key = ''.join([key, '/', nation])
    if blueprintMode:
        key = ''.join([key, '/', 'blueprints'])
    return key
