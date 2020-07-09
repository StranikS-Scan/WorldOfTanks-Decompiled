# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ClientSelectableRankedObject.py
from adisp import process
from ClientSelectableObject import ClientSelectableObject
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.Scaleform.genConsts.RANKEDBATTLES_CONSTS import RANKEDBATTLES_CONSTS
from helpers import dependency
from skeletons.gui.game_control import IRankedBattlesController

class ClientSelectableRankedObject(ClientSelectableObject):
    __rankedController = dependency.descriptor(IRankedBattlesController)

    def onEnterWorld(self, prereqs):
        super(ClientSelectableRankedObject, self).onEnterWorld(prereqs)
        self.__rankedController.onGameModeStatusUpdated += self.__onGameModeStatusUpdate
        self.__onGameModeStatusUpdate()

    def onLeaveWorld(self):
        self.__rankedController.onGameModeStatusUpdated -= self.__onGameModeStatusUpdate
        super(ClientSelectableRankedObject, self).onLeaveWorld()

    def onMouseClick(self):
        super(ClientSelectableRankedObject, self).onMouseClick()
        isEnabled = self.__rankedController.isEnabled()
        isYearGap = self.__rankedController.isYearGap()
        isYearLBEnabled = self.__rankedController.isYearLBEnabled()
        hasCurSeason = self.__rankedController.getCurrentSeason() is not None
        if isEnabled:
            if hasCurSeason:
                self.__switchToRankedPrb()
            elif isYearGap and isYearLBEnabled:
                self.__showYearlyLeaders()
            else:
                self.__showBetweenSeason()
        else:
            self.__showYearlyLeaders()
        return

    def __onGameModeStatusUpdate(self, *_):
        isEnabled = self.__rankedController.isEnabled()
        hasCurSeason = self.__rankedController.getCurrentSeason() is not None
        hasPrevSeason = self.__rankedController.getPreviousSeason() is not None
        if isEnabled and not hasCurSeason and not hasPrevSeason:
            self.setEnable(False)
        else:
            self.setEnable(True)
        return

    def __showBetweenSeason(self):
        ctx = {'selectedItemID': RANKEDBATTLES_CONSTS.RANKED_BATTLES_RANKS_ID}
        self.__rankedController.showRankedBattlePage(ctx)

    def __showYearlyLeaders(self):
        ctx = {'selectedItemID': RANKEDBATTLES_CONSTS.RANKED_BATTLES_YEAR_RATING_ID}
        self.__rankedController.showRankedBattlePage(ctx)

    @process
    def __switchToRankedPrb(self):
        yield g_prbLoader.getDispatcher().doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.RANKED))
