# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rankedBattles/ranked_battles_divisions.py
from gui.Scaleform.daapi.view.lobby.rankedBattles.ranked_battles_page import IResetablePage
from gui.Scaleform.daapi.view.meta.RankedBattlesDivisionsViewMeta import RankedBattlesDivisionsViewMeta
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.ranked_battles.ranked_builders import divisions_vos
from helpers import dependency
from skeletons.gui.game_control import IRankedBattlesController

class RankedBattlesDivisionsView(RankedBattlesDivisionsViewMeta, IResetablePage):
    __rankedController = dependency.descriptor(IRankedBattlesController)
    __slots__ = ('__selectedDivisionIdx',)

    def __init__(self):
        super(RankedBattlesDivisionsView, self).__init__()
        self.__selectedDivisionIdx = None
        return

    def onDivisionChanged(self, index):
        self.__selectedDivisionIdx = index
        self.__updateSounds()
        if self.progressComponent:
            self.progressComponent.selectDivision(self.__selectedDivisionIdx)

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(RankedBattlesDivisionsView, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == RANKEDBATTLES_ALIASES.RANKED_BATTLES_DIVISIONS_PROGRESS_UI:
            viewPy.selectDivision(self.__selectedDivisionIdx)

    def reset(self):
        self.__selectedDivisionIdx = None
        self.__setDivisionHeader()
        if self.progressComponent:
            self.progressComponent.reset()
        return

    @property
    def progressComponent(self):
        return self.getComponent(RANKEDBATTLES_ALIASES.RANKED_BATTLES_DIVISIONS_PROGRESS_UI)

    def _populate(self):
        super(RankedBattlesDivisionsView, self)._populate()
        self.__rankedController.onUpdated += self.__setDivisionHeader
        self.__setDivisionHeader()

    def _dispose(self):
        self.__rankedController.onUpdated -= self.__setDivisionHeader
        super(RankedBattlesDivisionsView, self)._dispose()

    def __getSelectedDivision(self):
        return self.__rankedController.getDivisions()[self.__selectedDivisionIdx]

    def __getDivisionsData(self):
        data = []
        currentDivisionIdx = 0
        for division in self.__rankedController.getDivisions():
            data.append(divisions_vos.getDivisionVO(division))
            if division.isCurrent():
                currentDivisionIdx = division.getID()

        return (data, currentDivisionIdx)

    def __setDivisionHeader(self):
        divisions, newSelectedDivisionIdx = self.__getDivisionsData()
        if self.__selectedDivisionIdx is None:
            self.__selectedDivisionIdx = newSelectedDivisionIdx
        self.as_setDataS({'divisions': divisions,
         'selectedDivisionIdx': self.__selectedDivisionIdx})
        return

    def __updateSounds(self):
        selectedDivision = self.__getSelectedDivision()
        soundManager = self.__rankedController.getSoundManager()
        if selectedDivision.isUnlocked():
            soundManager.setProgressSound(selectedDivision.getUserID())
        else:
            soundManager.setProgressSound(self.__rankedController.getCurrentDivision().getUserID(), isLoud=False)
