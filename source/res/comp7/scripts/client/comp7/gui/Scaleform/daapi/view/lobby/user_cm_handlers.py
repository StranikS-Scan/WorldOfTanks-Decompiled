# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/Scaleform/daapi/view/lobby/user_cm_handlers.py
from comp7.gui.comp7_constants import PREBATTLE_ACTION_NAME
from comp7.gui.Scaleform.daapi.view.lobby.lobby_constants import USER
from gui.Scaleform.daapi.view.lobby.user_cm_handlers import BaseUserCMHandler, UserVehicleCMHandler
from gui.Scaleform.locale.MENU import MENU
from gui.periodic_battles.models import PrimeTimeStatus
from helpers import dependency
from shared_utils import findFirst
from skeletons.gui.game_control import IComp7Controller

def createComp7Squad(cm):
    cm.createSquad(PREBATTLE_ACTION_NAME.COMP7_SQUAD)


@dependency.replace_none_kwargs(comp7Ctrl=IComp7Controller)
def addComp7SquadInfo(handler, options, userCMInfo, comp7Ctrl=None):
    if not userCMInfo.isIgnored and not handler.isSquadCreator() and handler.prbDispatcher is not None:
        canCreate = not handler.prbEntity.isInQueue()
        if comp7Ctrl.isEnabled():
            primeTimeStatus, _, _ = comp7Ctrl.getPrimeTimeStatus()
            isEnabled = primeTimeStatus == PrimeTimeStatus.AVAILABLE and not comp7Ctrl.isBanned and not comp7Ctrl.isOffline and comp7Ctrl.hasSuitableVehicles() and comp7Ctrl.isQualificationSquadAllowed()
            newComp7SquadItem = handler._makeItem(USER.CREATE_COMP7_SQUAD, MENU.contextmenu(USER.CREATE_COMP7_SQUAD), optInitData={'enabled': canCreate and isEnabled,
             'textColor': 13347959})
            if isinstance(handler, UserVehicleCMHandler):
                if comp7Ctrl.isModePrbActive():
                    regularSquadItem = findFirst(lambda it: it['id'] == USER.CREATE_SQUAD, options)
                    if regularSquadItem is not None:
                        options[options.index(regularSquadItem)] = newComp7SquadItem
            else:
                options.append(newComp7SquadItem)
    return options


class Comp7LeaderboardCMHandler(BaseUserCMHandler):

    def _generateOptions(self, ctx=None):
        userCMInfo = self._getUseCmInfo()
        options = [self._makeItem(USER.INFO, MENU.contextmenu(USER.INFO))]
        options = self._addFriendshipInfo(options, userCMInfo)
        options = self._addRemoveFriendInfo(options, userCMInfo)
        options = self._addChannelInfo(options, userCMInfo)
        options.append(self._makeItem(USER.COPY_TO_CLIPBOARD, MENU.contextmenu(USER.COPY_TO_CLIPBOARD)))
        return options
