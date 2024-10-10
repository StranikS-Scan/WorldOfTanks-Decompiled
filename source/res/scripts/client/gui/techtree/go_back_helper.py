# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/techtree/go_back_helper.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.vehicle_preview.vehicle_preview_constants import VEHICLE_PREVIEW_ALIASES
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.events import LoadGuiImplViewEvent
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
    elif previewView == WulfPreviewAlias.WULF_TECHTREE:
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


class LoadGuiImplViewEventWithCtx(LoadGuiImplViewEvent):

    def __init__(self, loadParams, *args, **kwargs):
        super(LoadGuiImplViewEventWithCtx, self).__init__(loadParams, *args, **kwargs)
        self.ctx = kwargs.get('ctx', {})
        self.name = kwargs.get('name', None)
        return


class WulfPreviewAlias(CONST_CONTAINER):
    WULF_TECHTREE = 'techtree'
