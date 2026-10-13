# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/scaleform/daapi/view/lobby/halloween_user_cm_handlers.py
from __future__ import absolute_import
import adisp
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.view.lobby.rally.UnitUserCMHandler import UnitUserCMHandler
from gui.Scaleform.daapi.view.lobby.lobby_constants import USER
from gui.Scaleform.daapi.view.lobby.user_cm_handlers import AppealCMHandler
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control.entities.base.ctx import PrbAction
from halloween.gui.halloween_gui_constants import PREBATTLE_ACTION_NAME
from halloween.gui.shared.event_dispatcher import showHangar
from halloween.skeletons.halloween_controller import IHalloweenController
from halloween.uilogging.loggers import HWMetricsLogger
from halloween.uilogging.logging_constants import HWLogKeys
from halloween_common.halloween_constants import PREBATTLE_TYPE
from helpers import dependency
from shared_utils import findFirst
CREATE_HALLOWEEN_SQUAD = 'createHalloweenSquad'
EXCLUDE_CM_CLASS = (UnitUserCMHandler,)
CLOSE_POSTBATTLE_OPTIONS = (USER.INFO, USER.CLAN_INFO, USER.CREATE_PRIVATE_CHANNEL)
HIGHLIGHT_COLOR = 13347959

@adisp.adisp_process
@dependency.replace_none_kwargs(ctrl=IHalloweenController)
def createHalloweenSquadHandler(cm, ctrl=None):
    if not ctrl.isEventPrb():
        action = PrbAction(PREBATTLE_ACTION_NAME.HALLOWEEN_SQUAD, accountsToInvite=[cm.databaseID])
        result = yield ctrl.prbDispatcher.doSelectAction(action, fadeCtx={'layer': WindowLayer.OVERLAY,
         'waitForLayoutReady': R.views.halloween.mono.lobby.hangar()})
        if not result:
            return
        showHangar()
    else:
        arenaUniqueID = getattr(cm, 'arenaUniqueID', None)
        cm.doSelect(PREBATTLE_ACTION_NAME.HALLOWEEN_SQUAD, (cm.databaseID,), extData={'arenaUniqueID': arenaUniqueID})
    return


@dependency.replace_none_kwargs(ctrl=IHalloweenController)
def halloweenSquadOptionBuilder(cm, options, userCMInfo, ctrl=None):
    if userCMInfo.isIgnored or cm.isSquadCreator() or cm.prbDispatcher is None or isinstance(cm, EXCLUDE_CM_CLASS):
        return options
    elif not ctrl.isAvailable():
        return options
    else:
        squadItem = findFirst(lambda it: it['id'] == USER.CREATE_SQUAD, options)
        inviteItem = findFirst(lambda it: it['id'] == USER.INVITE, options)
        userNameItem = findFirst(lambda it: it['id'] == USER.COPY_TO_CLIPBOARD, options)
        if not cm.isSquadAlreadyCreated(PREBATTLE_TYPE.HALLOWEEN):
            hwSquadItem = cm.makeItem(CREATE_HALLOWEEN_SQUAD, backport.text(R.strings.halloween_menu.contextMenu.createHalloweenSquad()), optInitData={'enabled': not cm.prbEntity.isInQueue(),
             'textColor': HIGHLIGHT_COLOR})
            if squadItem:
                options.insert(options.index(squadItem) + 1, hwSquadItem)
            elif userNameItem:
                options.insert(options.index(userNameItem) + 1, hwSquadItem)
        elif inviteItem:
            enabled = userCMInfo.databaseID not in cm.prbEntity.getPlayers()
            inviteItem['initData'].update({'textColor': HIGHLIGHT_COLOR,
             'enabled': enabled})
        return options


class HWAppealCMHandler(AppealCMHandler):

    def __init__(self, cmProxy, ctx=None):
        super(HWAppealCMHandler, self).__init__(cmProxy, ctx)
        self.__uiLogger = HWMetricsLogger(HWLogKeys.BATTLE_RESULT_STATS_CM)

    def onOptionSelect(self, optionId):
        self.__uiLogger.onClick(HWLogKeys.CONTEXT_MENU_BUTTON, optionId)
        super(HWAppealCMHandler, self).onOptionSelect(optionId=optionId)
        if optionId in CLOSE_POSTBATTLE_OPTIONS:
            showHangar()
