# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/go_back_helper.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.impl import backport
from gui.impl.gen import R
from shared_utils import CONST_CONTAINER
VEHICLE_PREVIEW_ALIASES = (VIEW_ALIAS.VEHICLE_PREVIEW,
 VIEW_ALIAS.HERO_VEHICLE_PREVIEW,
 VIEW_ALIAS.OFFER_GIFT_VEHICLE_PREVIEW,
 VIEW_ALIAS.TRADE_IN_VEHICLE_PREVIEW,
 VIEW_ALIAS.MARATHON_VEHICLE_PREVIEW,
 VIEW_ALIAS.CONFIGURABLE_VEHICLE_PREVIEW,
 VIEW_ALIAS.WOT_PLUS_VEHICLE_PREVIEW)

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
    elif previewView in VEHICLE_PREVIEW_ALIASES:
        alias = descriptionLabels.preview
    ctx = {'tankName': vehicleName}
    return backport.text(alias(), **ctx)
