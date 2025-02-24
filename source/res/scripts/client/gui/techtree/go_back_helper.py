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
    if previewView == VIEW_ALIAS.LOBBY_RESEARCH:
        labelPath = descriptionLabels.research
    elif previewView in VEHICLE_PREVIEW_ALIASES:
        labelPath = descriptionLabels.preview
    elif previewView == VIEW_ALIAS.LOBBY_STORAGE:
        labelPath = descriptionLabels.storage
    elif previewView == WulfPreviewAlias.WULF_TECHTREE:
        nation = exitEvent.ctx[BackButtonContextKeys.NATION]
        blueprintMode = exitEvent.ctx.get(BackButtonContextKeys.BLUEPRINT_MODE, False)
        labelPath = descriptionLabels.techtree.dyn(nation)
        if blueprintMode:
            labelPath = labelPath.blueprints
    else:
        labelPath = descriptionLabels.hangar
    return backport.text(labelPath(), tankName=vehicleName)


class LoadGuiImplViewEventWithCtx(LoadGuiImplViewEvent):

    def __init__(self, loadParams, *args, **kwargs):
        super(LoadGuiImplViewEventWithCtx, self).__init__(loadParams, *args, **kwargs)
        self.ctx = kwargs.get('ctx', {})
        self.name = kwargs.get('name', None)
        return


class WulfPreviewAlias(CONST_CONTAINER):
    WULF_TECHTREE = 'techtree'
