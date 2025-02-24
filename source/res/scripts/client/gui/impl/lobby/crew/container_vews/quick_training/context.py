# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/container_vews/quick_training/context.py
import typing
from gui.impl.auxiliary.crew_books_helper import crewBooksViewedCache
from gui.impl.gen.view_models.views.lobby.crew.crew_constants import CrewConstants
from gui.impl.lobby.container_views.base.context import TankmanContext
from gui.impl.lobby.crew.crew_helpers.quick_training_selection_data import QuickTrainingSelectionData
from gui.impl.lobby.crew.crew_helpers.skill_formatters import SkillLvlFormatter
from gui.impl.lobby.crew.crew_helpers.skill_helpers import quickEarnTmanSkills
from gui.impl.lobby.crew.crew_helpers.stepper_calculator import FreeXpStepperCalculator
from gui.impl.lobby.crew.utils import TRAINING_TIPS
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Tankman import NO_SLOT, NO_TANKMAN
from gui.shared.gui_items.Vehicle import NO_VEHICLE_ID
from gui.shared.gui_items.crew_book import sortItems
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from items.components.crew_books_constants import CREW_BOOK_RARITY
from items.tankmen import MAX_SKILLS_EFFICIENCY, MAX_SKILL_LEVEL
from shared_utils import first
from skeletons.gui.lobby_context import ILobbyContext
if typing.TYPE_CHECKING:
    from typing import List, Tuple
    from gui.shared.gui_items.crew_book import CrewBook
    from gui.shared.gui_items.Tankman import Tankman
    from gui.shared.gui_items.Vehicle import Vehicle
CREW_TIPS = {1: TRAINING_TIPS.NOT_FULL_CREW,
 2: TRAINING_TIPS.LOW_PE_CREW,
 3: TRAINING_TIPS.LOW_PE_NOT_FULL_CREW,
 4: TRAINING_TIPS.NOT_TRAINED_THIS_VEHICLE,
 5: TRAINING_TIPS.NOT_FULL_AND_NOT_TRAINED_CREW,
 6: TRAINING_TIPS.LOW_PE_NOT_TRAINED_CREW,
 7: TRAINING_TIPS.LOW_PE_NOT_TRAINED_NOT_FULL_CREW}

class TankmanAutoselector(object):
    selectedIdx = NO_SLOT
    selectedTman = None
    selectedTmanWithIssues = None
    selectedTmanWithPerkLimit = None

    def clear(self):
        self.selectedIdx = NO_SLOT
        self.selectedTman = None
        self.selectedTmanWithIssues = None
        self.selectedTmanWithPerkLimit = None
        return

    def validateTankman(self, tankmanId, idx, isMaxSkillXp, isUntrained, hasMaxSkillsEfficiency):
        if not isMaxSkillXp:
            if not (isUntrained or self.selectedTman) and hasMaxSkillsEfficiency:
                self.selectedTman = tankmanId
                self.selectedIdx = idx
            elif not (self.selectedTman or self.selectedTmanWithIssues):
                self.selectedTmanWithIssues = tankmanId
                self.selectedIdx = idx
        elif self.selectedIdx == NO_SLOT:
            self.selectedTmanWithPerkLimit = tankmanId
            self.selectedIdx = idx

    def getSelectedTankman(self):
        return (self.selectedTman or self.selectedTmanWithIssues or self.selectedTmanWithPerkLimit, self.selectedIdx)


class QuickTrainingViewContext(TankmanContext):
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, vehicleID, tankmanID):
        self._slotIdx = NO_SLOT
        self._vehicleID = vehicleID
        self._vehicle = None
        self._crewBooks = None
        self._isFullCrew = True
        self._isAllCrewMaxTrained = True
        self._hasCrewMaxedTman = False
        self._hasCrewUntrainedTman = False
        self._hasCrewLowTrainedTman = False
        self._willAnyTmanBeMaxed = False
        self._willAllTmenGainMaxXp = False
        self._willAllTmenBeMaxed = False
        self._alreadyMaxedTankmanName = None
        self._willBeMaxedTankmanName = None
        self._possibleCrewSkills = []
        self._possibleCrewSkillEfficiencis = []
        self._stepper = FreeXpStepperCalculator(self.itemsCache.items.shop.freeXPToTManXPRate)
        self._selectionData = QuickTrainingSelectionData()
        self._autoselector = TankmanAutoselector()
        super(QuickTrainingViewContext, self).__init__(tankmanID)
        self.__getCurrentVehicle()
        self.__getCrewBooks()
        self.__setInitialCrewProperties(tankmanID)
        return

    @property
    def vehicleID(self):
        return self._vehicleID

    @property
    def isMentoringLicenseEnabled(self):
        return self.lobbyContext.getServerSettings().isMentoringLicenseEnabled()

    @property
    def vehicle(self):
        return self._vehicle

    @property
    def crew(self):
        if self.isSingleTankman:
            return [(0, self.tankman)]
        else:
            return self._vehicle.crew if self._vehicle else [(0, None)]

    @property
    def crewBooks(self):
        return self._crewBooks

    @property
    def slotIdx(self):
        return self._slotIdx

    @property
    def isFullCrew(self):
        return self._isFullCrew

    @property
    def isAllCrewMaxTrained(self):
        return self._isAllCrewMaxTrained

    @property
    def isCurrTmanMaxTrained(self):
        return True if not self.tankman else self.tankman.descriptor.isMaxSkillXp()

    @property
    def isSingleTankman(self):
        return not (self.tankman is None or self.tankman.isInTank)

    @property
    def hasCurrTmanMaxSkillsEfficiency(self):
        return True if not self.tankman else self.tankman.descriptor.hasMaxEfficiency()

    @property
    def hasCrewMaxedTman(self):
        return self._hasCrewMaxedTman

    @property
    def hasCrewUntrainedTman(self):
        return self._hasCrewUntrainedTman

    @property
    def hasCrewLowTrainedTman(self):
        return self._hasCrewLowTrainedTman

    @property
    def canCrewSelectBook(self):
        return self._isFullCrew and not (self._isAllCrewMaxTrained or self._willAllTmenBeMaxed or self._hasCrewLowTrainedTman or self._hasCrewUntrainedTman)

    @property
    def canCrewSelectPersonalBook(self):
        return self._hasCrewLowTrainedTman or not self._isAllCrewMaxTrained

    @property
    def canCrewSelectFreeXp(self):
        return self.itemsCache.items.stats.freeXP > 0 and not self._isAllCrewMaxTrained

    @property
    def canCurrentTankmanUseFreeXp(self):
        if not self.tankman:
            return True
        aquiringPersonalXp, aquiringCommonXp = self._selectionData.getAllAquiringBooksXpValue()
        return self.tankman.isMaxSkillEfficiency and not self.tankman.descriptor.isMaxSkillXp() and not (self._selectionData.freeXp == 0 and self.tankman.descriptor.isMaxSkillXp(aquiringPersonalXp + aquiringCommonXp))

    @property
    def canCurrentTankmanUsePersonalBook(self):
        return True if not self.tankman else not self.tankman.descriptor.isMaxedXp()

    @property
    def canCurrentTankmanUseMorePersonalBook(self):
        if not self.tankman:
            return True
        fullAquiringPersonalXp, fullAquiringCommonXp = self._selectionData.getAllAquiringBooksXpValue()
        extraXp = fullAquiringPersonalXp + fullAquiringCommonXp + self.__getComputableFreeXpValue()
        return not self.tankman.descriptor.isMaxedXp(extraXp)

    @property
    def willAnyTmanBeMaxed(self):
        return self._willAnyTmanBeMaxed

    @property
    def willAllTmenGainMaxXp(self):
        return self._willAllTmenGainMaxXp

    @property
    def alreadyMaxedTankmanName(self):
        return self._alreadyMaxedTankmanName

    @property
    def possibleMaxedTankmanName(self):
        return self._willBeMaxedTankmanName

    @property
    def stepper(self):
        return self._stepper

    @property
    def selection(self):
        return self._selectionData

    @property
    def accountMaxedTankmenCount(self):
        return len(self.itemsCache.items.getTankmen(REQ_CRITERIA.TANKMAN.IS_POST_PROGRESSION_AVAILABLE).values())

    @property
    def rewardBook(self):
        rewardBookId = crewBooksViewedCache().rewardBookId()
        return first(self.itemsCache.items.getItems(GUI_ITEM_TYPE.CREW_BOOKS, REQ_CRITERIA.CREW_ITEM.ID(rewardBookId)).values())

    @property
    def maxPossibleXpCount(self):
        return 0 if self.tankman is None else self._stepper.getMaxPossibleValue()

    @property
    def crewTip(self):
        untrained = int(self._hasCrewUntrainedTman)
        lowTrained = int(self._hasCrewLowTrainedTman)
        notFull = int(not self._isFullCrew or self.isSingleTankman)
        return CREW_TIPS.get(untrained << 2 | lowTrained << 1 | notFull)

    @property
    def postProgressionXp(self):
        return self.itemsCache.items.stats.postProgressionXP

    @property
    def xpDefaultConversionRate(self):
        return self.itemsCache.items.shop.defaults.freeXPToTManXPRate

    @property
    def xpDiscountConversionRate(self):
        return self.itemsCache.items.shop.freeXPToTManXPRate

    @property
    def xpConversionDiscount(self):
        return int(round(abs(1 - float(self.xpDefaultConversionRate) / self.xpDiscountConversionRate) * 100))

    @property
    def hiddenShopItems(self):
        return self.itemsCache.items.shop.getHiddens()

    def update(self, tankmanID=NO_TANKMAN, slotIdx=NO_SLOT):
        prevTankmanId = self.tankmanID
        self._slotIdx = slotIdx
        super(QuickTrainingViewContext, self).update(tankmanID)
        if tankmanID != NO_TANKMAN:
            self._stepper.setCurrentTankman(self.tankman)
            if prevTankmanId != tankmanID:
                self.__updateWithNewTankman()

    def getAcquiringFreeXpValue(self):
        return self._selectionData.freeXp * self.xpDiscountConversionRate

    def getPossibleCrewSkillsAndEfficiencies(self):
        return (self._possibleCrewSkills, self._possibleCrewSkillEfficiencis)

    def updateOnFreeXpGlobalChange(self):
        if self._selectionData.freeXp > self.itemsCache.items.stats.freeXP:
            self._selectionData.freeXp = self.itemsCache.items.stats.freeXP

    def updateOnGlobalSync(self):
        if self.tankman and self.tankman.isInTank:
            tankmanId = self.tankmanID
        else:
            tankmanId = NO_TANKMAN
        self.update(self.tankmanID, self._slotIdx)
        self.__getCurrentVehicle()
        self.__setInitialCrewProperties(tankmanId=tankmanId)

    def updateBooks(self):
        self.__getCrewBooks()

    def updatePossibleCrewState(self):
        willGainMaxXp = []
        maxCrewTmenCount = 0
        willBeMaxedTmenCount = 0
        crewLength = len(self.crew)
        personalBooksXp, commonBooksXp = self._selectionData.getAllAquiringBooksXpValue()
        totalPersonalXp = self.__getComputableFreeXpValue() + personalBooksXp + commonBooksXp
        self._willBeMaxedTankmanName = None
        self._willAnyTmanBeMaxed = False
        self._willAllTmenBeMaxed = False
        self._willAllTmenGainMaxXp = False
        self._possibleCrewSkillEfficiencis = [0] * crewLength
        self._possibleCrewSkills = [ (CrewConstants.DONT_SHOW_LEVEL,
         CrewConstants.DONT_SHOW_LEVEL,
         SkillLvlFormatter(),
         SkillLvlFormatter()) for _ in range(crewLength) ]
        self._stepper.setAquiringPersonalXp(commonBooksXp + personalBooksXp)
        for idx, tankman in self.crew:
            if tankman is None:
                continue
            skillData, self._possibleCrewSkillEfficiencis[idx] = quickEarnTmanSkills(tankman, totalPersonalXp if self.tankmanID == tankman.invID else commonBooksXp)
            self._possibleCrewSkills[idx] = skillData
            if tankman.descriptor.isMaxedXp():
                maxCrewTmenCount += 1
                continue
            willCurrTmanBeMaxed = skillData[1] == tankman.maxSkillsCount and skillData[3].formattedSkillLvl == MAX_SKILL_LEVEL and self._possibleCrewSkillEfficiencis[idx] == MAX_SKILLS_EFFICIENCY
            willGainMaxXp.append(willCurrTmanBeMaxed)
            if willCurrTmanBeMaxed:
                maxCrewTmenCount += 1
                willBeMaxedTmenCount += 1
                self._willAnyTmanBeMaxed = True
                if self._willBeMaxedTankmanName is None:
                    self._willBeMaxedTankmanName = tankman.getFullUserNameWithSkin()
            if tankman.invID == self.tankmanID:
                self._stepper.setManualInputPossibleValues(skillData[1], int(skillData[3].formattedSkillLvl))

        if willBeMaxedTmenCount > 1:
            self._willBeMaxedTankmanName = None
        self._willAllTmenBeMaxed = maxCrewTmenCount == crewLength
        self._willAllTmenGainMaxXp = len(willGainMaxXp) == crewLength and all(willGainMaxXp)
        return

    def __getComputableFreeXpValue(self):
        return (self._selectionData.preSelectedFreeXp or self._selectionData.freeXp) * self.xpDiscountConversionRate

    def __getCurrentVehicle(self):
        if self._vehicleID == NO_VEHICLE_ID or self.isSingleTankman:
            self._vehicleID = self.tankman.vehicleNativeDescr.type.compactDescr
            self._vehicle = self.itemsCache.items.getItemByCD(self._vehicleID)
        else:
            self._vehicle = self.itemsCache.items.getVehicle(self._vehicleID)

    def __getCrewBooks(self):
        criteria = REQ_CRITERIA.CREW_ITEM.NATIONS([self._vehicle.nationID])
        criteria ^= REQ_CRITERIA.CREW_ITEM.BOOK_RARITIES(CREW_BOOK_RARITY.NO_NATION_TYPES)
        items = self.itemsCache.items.getItems(GUI_ITEM_TYPE.CREW_BOOKS, criteria)
        self._crewBooks = sortItems(items.values())

    def __setInitialCrewProperties(self, tankmanId=NO_TANKMAN):
        alreadyMaxedTmenCount = 0
        self._isFullCrew = True
        self._hasCrewMaxedTman = False
        self._isAllCrewMaxTrained = True
        self._hasCrewUntrainedTman = False
        self._hasCrewLowTrainedTman = False
        self._alreadyMaxedTankmanName = None
        self._autoselector.clear()
        for idx, tankman in self.crew:
            if tankman is None:
                self._isFullCrew = False
                continue
            if self._slotIdx == NO_SLOT and tankmanId != NO_TANKMAN and tankmanId == tankman.invID:
                self._slotIdx = idx
            isUntrained = tankman.isUntrained
            isMaxSkillXp = tankman.descriptor.isMaxSkillXp()
            hasMaxSkillsEfficiency = tankman.descriptor.hasMaxEfficiency()
            isFullTrained = isMaxSkillXp and hasMaxSkillsEfficiency
            if isFullTrained:
                alreadyMaxedTmenCount += 1
                if self._alreadyMaxedTankmanName is None:
                    self._alreadyMaxedTankmanName = tankman.getFullUserNameWithSkin()
            if tankmanId == NO_TANKMAN:
                self._autoselector.validateTankman(tankman.invID, idx, isMaxSkillXp, isUntrained, hasMaxSkillsEfficiency)
            self._hasCrewMaxedTman = self._hasCrewMaxedTman or isFullTrained
            self._isAllCrewMaxTrained = self._isAllCrewMaxTrained and isFullTrained
            self._hasCrewUntrainedTman = self._hasCrewUntrainedTman or isUntrained or tankman.isInPremiumTank
            self._hasCrewLowTrainedTman = self._hasCrewLowTrainedTman or not hasMaxSkillsEfficiency

        if alreadyMaxedTmenCount > 1:
            self._alreadyMaxedTankmanName = None
        if tankmanId == NO_TANKMAN:
            self.update(*self._autoselector.getSelectedTankman())
        return

    def __updateWithNewTankman(self):
        if self._selectionData.freeXp > 0:
            if self.canCurrentTankmanUseFreeXp:
                self._selectionData.freeXp = self._stepper.getSkillUpXpCost()
            else:
                self._selectionData.freeXp = 0
        if not self.canCurrentTankmanUsePersonalBook:
            bookId = self._selectionData.getPersonalBookId()
            if bookId:
                book = self.itemsCache.items.getItemByCD(bookId)
                self._selectionData.setBook(book, 0)
