# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/Scaleform/daapi/view/lobby/user_cm_handlers.py
import typing
from comp7_light.gui.comp7_light_constants import PREBATTLE_ACTION_NAME
from comp7_light.gui.Scaleform.daapi.view.lobby.lobby_constants import USER
from gui.Scaleform.locale.MENU import MENU
from gui.periodic_battles.models import PrimeTimeStatus
from helpers import dependency
from shared_utils import findFirst
from skeletons.gui.game_control import IComp7LightController
from gui.Scaleform.daapi.view.lobby.user_cm_handlers import UserVehicleCMHandler
if typing.TYPE_CHECKING:
    from gui.Scaleform.daapi.view.lobby.user_cm_handlers import BaseUserCMHandler

def createComp7LightSquad(cm):
    cm.createSquad(PREBATTLE_ACTION_NAME.COMP7_LIGHT_SQUAD)


@dependency.replace_none_kwargs(comp7LightCtrl=IComp7LightController)
def addComp7LightSquadInfo(handler, options, userCMInfo, comp7LightCtrl=None):
    if userCMInfo.isIgnored or handler.isSquadCreator() or handler.prbDispatcher is None:
        return options
    elif not comp7LightCtrl.isEnabled():
        return options
    else:
        canCreate = not handler.prbEntity.isInQueue()
        primeTimeStatus, _, _ = comp7LightCtrl.getPrimeTimeStatus()
        isEnabled = primeTimeStatus == PrimeTimeStatus.AVAILABLE and not comp7LightCtrl.isBanned and not comp7LightCtrl.isOffline and comp7LightCtrl.hasSuitableVehicles()
        newComp7LightSquadItem = handler._makeItem(USER.CREATE_COMP7_LIGHT_SQUAD, MENU.contextmenu(USER.CREATE_COMP7_LIGHT_SQUAD), optInitData={'enabled': canCreate and isEnabled,
         'textColor': 13347959})
        if isinstance(handler, UserVehicleCMHandler):
            if comp7LightCtrl.isModePrbActive():
                regularSquadItem = findFirst(lambda it: it['id'] == USER.CREATE_SQUAD, options)
                if regularSquadItem is not None:
                    options[options.index(regularSquadItem)] = newComp7LightSquadItem
        else:
            options.append(newComp7LightSquadItem)
        return options
