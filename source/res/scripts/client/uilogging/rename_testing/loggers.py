# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/rename_testing/loggers.py
from helpers import dependency
from skeletons.connection_mgr import IConnectionManager
from uilogging.base.logger import MetricsLogger
from uilogging.rename_testing.constants import FEATURE, RENAME_TESTING_ACTION_CLICK, RenameTestingItems

@dependency.replace_none_kwargs(connectionMgr=IConnectionManager)
def _renameTestingPartnerID(connectionMgr=None):
    return str(connectionMgr.lastSessionID or '')


class RenameTestingUILogger(MetricsLogger):
    __slots__ = ('__partnerID',)

    def __init__(self):
        super(RenameTestingUILogger, self).__init__(FEATURE)
        self.__partnerID = _renameTestingPartnerID()

    def __logClick(self, item):
        self.log(action=RENAME_TESTING_ACTION_CLICK, item=item, partnerID=self.__partnerID)

    def logHangarEnter(self):
        self.__logClick(RenameTestingItems.HANGAR_ENTER)

    def logModeSelectorOpen(self):
        self.__logClick(RenameTestingItems.MODE_SELECTOR_OPEN)

    def logTrainingModSelectorItem(self):
        self.__logClick(RenameTestingItems.TRAINING_MODE_SELECTOR_CARD)

    def logTrainingOpenCreateRoomDialog(self):
        self.__logClick(RenameTestingItems.TRAINING_OPEN_CREATE_ROOM_DIALOG)

    def logTrainingJoinRoom(self):
        self.__logClick(RenameTestingItems.TRAINING_JOIN_ROOM)

    def logPlatoonMenuSection(self):
        self.__logClick(RenameTestingItems.PLATOON_MENU_SECTION)

    def logCreateNewPlatoon(self):
        self.__logClick(RenameTestingItems.CREATE_NEW_PLATOON)

    def logPlatoonFindPlayers(self):
        self.__logClick(RenameTestingItems.PLATOON_FIND_PLAYERS)

    def logPlatoonReadyButton(self):
        self.__logClick(RenameTestingItems.PLATOON_READY_BUTTON)

    def logPlatoonFightButton(self):
        self.__logClick(RenameTestingItems.PLATOON_FIGHT_BUTTON)

    def logTrainingStartBattle(self):
        self.__logClick(RenameTestingItems.TRAINING_START_BATTLE)

    def logTrainingCreateRoom(self):
        self.__logClick(RenameTestingItems.TRAINING_CREATE_ROOM)
