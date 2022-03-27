# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/battle_queue/rts_battle_queue.py
from CurrentVehicle import g_currentVehicle
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control.prb_getters import getArenaGUIType
from gui.Scaleform.daapi.view.meta.RTSBattleQueueMeta import RTSBattleQueueMeta
from gui.Scaleform.locale.MENU import MENU
from gui.shared.gui_items.Vehicle import getTypeSmallIconPath
from gui.shared.formatters import text_styles
from helpers import dependency
from constants import ARENA_BONUS_TYPE
from skeletons.gui.shared import IItemsCache
from skeletons.gui.game_control import IRTSBattlesController

class RTSBattleQueue(RTSBattleQueueMeta):
    __strPath = R.strings.rts_battles.battleQueue
    __rtsController = dependency.descriptor(IRTSBattlesController)
    __itemsCache = dependency.descriptor(IItemsCache)
    TIME_UNTIL_TANKER_SUGGESTION = 10
    NUM_COMMANDER_TANKER_SUGGESTION = 2

    def __init__(self, _=None):
        super(RTSBattleQueue, self).__init__()
        self.__isQueueUnbalanced = False
        self.__avgCommanderWaitTime = 0
        self.__numOfCommander = 0
        self.__bootcampAdditionalInfo = ''

    def onSwitchVehicleClick(self):
        self.as_hideSwitchVehicleS()
        self.prbEntity.reloadQueue()

    def onEnqueued(self, queueType, *args):
        self._updateClientState()

    def setCommanderInfo(self, avgWaitTime, numOfCommanders):
        self.__avgCommanderWaitTime = avgWaitTime
        self.__numOfCommander = numOfCommanders

    def getCreateTime(self):
        return self._createTime

    def isQueueUnbalanced(self):
        return self.__isQueueUnbalanced

    def _getVO(self):
        vehicle = g_currentVehicle.item
        isCommander = self.__rtsController.isCommander()
        isRTSBootcamp = self.__rtsController.getBattleMode() == ARENA_BONUS_TYPE.RTS_BOOTCAMP
        titleText = self.__strPath.bootcamp() if isRTSBootcamp else self.__strPath.title()
        return {'title': backport.text(titleText),
         'additional': self._provider.additionalInfo() if self._provider.needAdditionalInfo() else '',
         'description': MENU.loading_battletypes_desc(getArenaGUIType(queueType=self._provider.getQueueType())),
         'tankLabel': text_styles.main(self._provider.getTankInfoLabel()),
         'tankIcon': '' if isCommander else getTypeSmallIconPath(vehicle.type),
         'tankName': '' if isCommander else vehicle.shortUserName,
         'teamName': backport.text(self.__getTeamName(isCommander)),
         'isRTSBootcamp': isRTSBootcamp}

    def _updateTimer(self):
        super(RTSBattleQueue, self)._updateTimer()
        if self.__rtsController.isCommander() and self.__rtsController.getBattleMode() == ARENA_BONUS_TYPE.RTS:
            isQueueUnbalanced = self.__avgCommanderWaitTime > self.TIME_UNTIL_TANKER_SUGGESTION and self.__numOfCommander >= self.NUM_COMMANDER_TANKER_SUGGESTION
            if isQueueUnbalanced != self.__isQueueUnbalanced:
                self.__isQueueUnbalanced = isQueueUnbalanced
                self.as_setTypeInfoS(self._getVO())
            return
        isRTSBootcamp = self.__rtsController.getBattleMode() == ARENA_BONUS_TYPE.RTS_BOOTCAMP
        if isRTSBootcamp and self.__bootcampAdditionalInfo != self._provider.additionalInfo():
            self.__bootcampAdditionalInfo = self._provider.additionalInfo()
            self.as_setTypeInfoS(self._getVO())

    @classmethod
    def __getTeamName(cls, isCommanderRole):
        return cls.__strPath.widget.team.commander() if isCommanderRole else cls.__strPath.widget.team.tankman()
