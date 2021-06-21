# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/go_back_helper.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.impl import backport
from gui.impl.gen import R
from shared_utils import CONST_CONTAINER

class BackButtonContextKeys(CONST_CONTAINER):
    BLUEPRINT_MODE = 'blueprintMode'
    NATION = 'nation'
    EXIT = 'exit'
    ROOT_CD = 'rootCD'


def getBackBtnDescription(exitEvent, previewView, vehicleName=''):
    descriptionLabels = R.strings.menu.viewHeader.backBtn.descrLabel
    alias = descriptionLabels.hangar
    if previewView == VIEW_ALIAS.LOBBY_RESEARCH:
        alias = descriptionLabels.research
    elif previewView == VIEW_ALIAS.LOBBY_TECHTREE:
        nation = exitEvent.ctx[BackButtonContextKeys.NATION]
        blueprintMode = exitEvent.ctx.get(BackButtonContextKeys.BLUEPRINT_MODE, False)
        if blueprintMode:
            alias = descriptionLabels.techtree.dyn(nation).blueprints
        else:
            alias = descriptionLabels.techtree.dyn(nation)
    ctx = {'tankName': vehicleName}
    return backport.text(alias(), **ctx)
