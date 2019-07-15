# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/auxiliary/crew_books_helper.py
from collections import defaultdict
import BigWorld
from CurrentVehicle import g_currentVehicle
from account_helpers import AccountSettings
from account_helpers.AccountSettings import CREW_BOOKS_VIEWED
from adisp import async
from nations import INDICES, NONE_INDEX
from frameworks.wulf.view.array import Array
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew_books.crew_book_skill_model import CrewBookSkillModel
from gui.impl.gen.view_models.views.lobby.crew_books.crew_book_tankman_model import CrewBookTankmanModel
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Vehicle import getIconResourceName
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers.dependency import descriptor, replace_none_kwargs
from items.components.crew_books_constants import CREW_BOOK_RARITY
from items.components import skills_constants
from items import tankmen
from items.components.crew_skins_constants import NO_CREW_SKIN_ID
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
MIN_ROLE_LEVEL = 100
MAX_SKILL_VIEW_COUNT = 4
_g_crewBooksViewedCache = None

def crewBooksViewedCache():
    global _g_crewBooksViewedCache
    if _g_crewBooksViewedCache is None:
        _g_crewBooksViewedCache = _CrewBooksViewedCache()
    elif _g_crewBooksViewedCache.userLogin != getattr(BigWorld.player(), 'name', ''):
        _g_crewBooksViewedCache.destroy()
        _g_crewBooksViewedCache = _CrewBooksViewedCache()
    return _g_crewBooksViewedCache


class _CrewBooksViewedCache(object):
    _itemsCache = descriptor(IItemsCache)
    _lobbyContext = descriptor(ILobbyContext)

    def __init__(self):
        self.__viewedItems = AccountSettings.getSettings(CREW_BOOKS_VIEWED)
        self.__userLogin = getattr(BigWorld.player(), 'name', '')
        self.__booksCountByNation = defaultdict(lambda : defaultdict(int))
        self.__syncOwnedItems()
        self._itemsCache.onSyncCompleted += self.__onCacheResync

    @property
    def userLogin(self):
        return self.__userLogin

    def addViewedItems(self, nationID):
        if self.__needUpdate:
            for bookType, count in self.__booksCountByNation.iteritems():
                if bookType == CREW_BOOK_RARITY.PERSONAL:
                    self.__viewedItems[bookType] = count
                self.__viewedItems[bookType][nationID] = count[nationID]

            AccountSettings.setSettings(CREW_BOOKS_VIEWED, self.__viewedItems)
            self.__needUpdate = False

    def haveNewCrewBooks(self):
        vehicle = g_currentVehicle.item
        if vehicle is None or not self._lobbyContext.getServerSettings().isCrewBooksEnabled():
            return False
        else:
            currentNation = vehicle.nationID
            for bookType, count in self.__booksCountByNation.iteritems():
                if bookType == CREW_BOOK_RARITY.PERSONAL:
                    if self.__viewedItems[bookType] < count:
                        self.__needUpdate = True
                        return True
                if self.__viewedItems[bookType].setdefault(currentNation, 0) < count[currentNation]:
                    self.__needUpdate = True
                    return True

            return False

    @async
    def onCrewBooksUpdated(self, diff, callback):
        inventory = diff.get('inventory', {})
        if GUI_ITEM_TYPE.CREW_BOOKS in inventory:
            for cd, count in inventory[GUI_ITEM_TYPE.CREW_BOOKS].iteritems():
                item = tankmen.getItemByCompactDescr(cd)
                if count is None:
                    count = 0
                if item.type == CREW_BOOK_RARITY.PERSONAL:
                    self.__booksCountByNation[item.type] = count
                self.__booksCountByNation[item.type][self.__getNationID(item.nation)] = count

            self.__needUpdate = True
        callback(True)
        return

    def destroy(self):
        self._itemsCache.onSyncCompleted -= self.__onCacheResync
        self.__booksCountByNation.clear()
        self.__viewedItems.clear()

    def __onCacheResync(self, reason, diff):
        if reason not in (CACHE_SYNC_REASON.CLIENT_UPDATE, CACHE_SYNC_REASON.DOSSIER_RESYNC):
            self.__syncOwnedItems()

    def __syncOwnedItems(self):
        items = self._itemsCache.items.getItems(GUI_ITEM_TYPE.CREW_BOOKS, REQ_CRITERIA.CREW_ITEM.IN_ACCOUNT)
        for item in items.itervalues():
            bookType = item.getBookType()
            if bookType == CREW_BOOK_RARITY.PERSONAL:
                self.__booksCountByNation[bookType] = item.getFreeCount()
            self.__booksCountByNation[bookType][item.getNationID()] = item.getFreeCount()

        self.__needUpdate = True

    def __getNationID(self, nationName):
        return INDICES.get(nationName, NONE_INDEX)


class XpGainResult(object):
    NEW_SKILLS = 'new_skills'
    SURPLUS_LEVELS = 'surplus_levels'


@replace_none_kwargs(itemsCache=IItemsCache)
def gainedLevels(tankmanInvId, crewBookCD, itemsCache=None):
    result = {}
    if crewBookCD is None:
        return result
    else:

        def _newSkillsCount(descr):
            if tankman.role == tankman.ROLES.COMMANDER:
                skillsList = list(skills_constants.ACTIVE_SKILLS)
            else:
                skillsList = list(tankman._NON_COMMANDER_SKILLS)
            i = 0
            while descr.roleLevel == 100 and (descr.lastSkillLevel == 100 or not descr.skills) and skillsList:
                skillName = skillsList.pop()
                if skillName not in descr.skills:
                    descr.addSkill(skillName)
                    i += 1

            return i

        def _calculateSurplus(xp, surplus, descr, result):
            if surplus == 0:
                xpCost = descr.levelUpXpCost(descr.lastSkillLevel, descr.lastSkillNumber - descr.freeSkillsNumber)
                result[XpGainResult.SURPLUS_LEVELS] = round(xp / (xpCost * 1.0), 2)
                if result[XpGainResult.SURPLUS_LEVELS] == 0:
                    result[XpGainResult.SURPLUS_LEVELS] = format(result[XpGainResult.SURPLUS_LEVELS], '.2f')
            else:
                result[XpGainResult.SURPLUS_LEVELS] = surplus

        def _fillResult(newSkillsCount, descr, levelBeforeAdd, bookXP, result):
            if newSkillsCount:
                result[XpGainResult.NEW_SKILLS] = newSkillsCount
                surplus = descr.lastSkillLevel
                _calculateSurplus(descr.freeXP, surplus, descr, result)
            else:
                surplus = descr.lastSkillLevel - levelBeforeAdd
                _calculateSurplus(bookXP, surplus, descr, result)

        tankman = itemsCache.items.getTankman(tankmanInvId)
        descr = tankmen.TankmanDescr(tankman.strCD)
        xp = itemsCache.items.getItemByCD(crewBookCD).getXP()
        roleLevel = descr.roleLevel
        if roleLevel < tankmen.MAX_SKILL_LEVEL:
            descr.addXP(xp)
            newSkillsCount = _newSkillsCount(descr)
            _fillResult(newSkillsCount, descr, 0, xp, result)
        else:
            _newSkillsCount(descr)
            levelBeforeAdd = descr.lastSkillLevel
            descr.addXP(xp)
            newSkillsCount = _newSkillsCount(descr)
            _fillResult(newSkillsCount, descr, levelBeforeAdd, xp, result)
        return result


class TankmanModelPresenterBase(object):
    __itemsCache = descriptor(IItemsCache)
    __lobbyContext = descriptor(ILobbyContext)
    __slots__ = ()

    def getModel(self, index, tankmanInvId=None, isTooltipEnable=True):
        model = self._createModel()
        with model.transaction() as m:
            m.setIsTooltipEnable(isTooltipEnable)
            if tankmanInvId is None:
                self._formatEmptyModel(m, index)
            else:
                self._formatModel(m, index, tankmanInvId)
        return model

    def _createModel(self):
        return CrewBookTankmanModel()

    def _formatModel(self, model, index, tankmanInvId):
        tankman = self.__itemsCache.items.getTankman(int(tankmanInvId))
        tankmenIcons = R.images.gui.maps.icons.tankmen
        with model.transaction() as m:
            m.setIdx(index)
            if tankman.skinID != NO_CREW_SKIN_ID and self.__lobbyContext.getServerSettings().isCrewSkinsEnabled():
                skinItem = self.__itemsCache.items.getCrewSkin(tankman.skinID)
                m.setTankmanIcon(tankmenIcons.icons.big.crewSkins.dyn(getIconResourceName(skinItem.getIconID()))())
            else:
                m.setTankmanIcon(tankmenIcons.icons.big.dyn(getIconResourceName(tankman.extensionLessIcon))())
            m.setRoleIcon(tankmenIcons.roles.big.dyn(getIconResourceName(tankman.extensionLessIconRole))())
            m.setInvID(tankman.invID)
            m.setRoleLevel(str(tankman.roleLevel))

    def _formatEmptyModel(self, model, index):
        model.setIdx(index)
        model.setTankmanIcon(R.images.gui.maps.icons.crewBooks.tankmanComponents.crew_empty())
        model.setIsEmpty(True)


class TankmanModelPresenter(TankmanModelPresenterBase):
    __itemsCache = descriptor(IItemsCache)
    __slots__ = ()

    def _formatModel(self, model, index, tankmanInvId):
        super(TankmanModelPresenter, self)._formatModel(model, index, tankmanInvId)
        tankman = self.__itemsCache.items.getTankman(int(tankmanInvId))
        with model.transaction() as m:
            m.setIsLowRoleLevel(tankman.roleLevel < MIN_ROLE_LEVEL)
            if tankman.vehicleDescr.type.compactDescr != tankman.vehicleNativeDescr.type.compactDescr:
                nativeVehicle = self.__itemsCache.items.getItemByCD(tankman.vehicleNativeDescr.type.compactDescr)
                m.setIsWrongVehicle(True)
                m.setNativeVehicle(nativeVehicle.userName)


class TankmanSkillListPresenter(object):
    __itemsCache = descriptor(IItemsCache)

    def getList(self, tankmanInvId, isTooltipEnable=True, crewBookCD=None):
        tankman = self.__itemsCache.items.getTankman(int(tankmanInvId))
        self._gainedLevels = gainedLevels(tankmanInvId, crewBookCD)
        wulfList = Array()
        if len(tankman.skills) + tankman.newSkillCount[0] <= MAX_SKILL_VIEW_COUNT:
            self._createList(wulfList, tankman, isTooltipEnable)
        else:
            self._createShortList(wulfList, tankman, isTooltipEnable)
        self._availableForLearn(wulfList, tankman)
        return wulfList

    def _availableForLearn(self, wulfList, tankman):
        canLearnSkills, lastSkillLevel = tankman.newSkillCount
        if XpGainResult.NEW_SKILLS in self._gainedLevels:
            gainedSkills = self._gainedLevels[XpGainResult.NEW_SKILLS]
            if XpGainResult.SURPLUS_LEVELS in self._gainedLevels:
                gainedSkills -= 1
        else:
            gainedSkills = 0
        if tankman.hasNewSkill(True) and XpGainResult.NEW_SKILLS not in self._gainedLevels:
            canLearnSkills -= 1
        compactSkills = canLearnSkills + gainedSkills
        isMaxSkillsLearned = len(tankman.availableSkills(True)) <= compactSkills
        hasUnlearnedSkill = XpGainResult.SURPLUS_LEVELS in self._gainedLevels and XpGainResult.NEW_SKILLS in self._gainedLevels or tankman.newSkillCount[0] > 0
        if compactSkills > 0:
            tankmanSkillVM = CrewBookSkillModel()
            tankmanSkillVM.setIsTooltipEnable(False)
            tankmanSkillVM.setIcon(R.images.gui.maps.icons.tankmen.skills.small.new_skill())
            tankmanSkillVM.setTankmanInvId(tankman.invID)
            if compactSkills > 1:
                tankmanSkillVM.setIsCompact(True)
                tankmanSkillVM.setDescription(str(compactSkills))
            wulfList.addViewModel(tankmanSkillVM)
        if hasUnlearnedSkill and isMaxSkillsLearned is False:
            tankmanSkillVM = CrewBookSkillModel()
            tankmanSkillVM.setIsTooltipEnable(False)
            tankmanSkillVM.setIcon(R.images.gui.maps.icons.tankmen.skills.small.new_current_skill())
            tankmanSkillVM.setTankmanInvId(tankman.invID)
            tankmanSkillVM.setIsUnlearned(True)
            if XpGainResult.NEW_SKILLS not in self._gainedLevels:
                tankmanSkillVM.setDescription(str(lastSkillLevel))
            if XpGainResult.SURPLUS_LEVELS in self._gainedLevels:
                tankmanSkillVM.setGainProgress(str(self._gainedLevels[XpGainResult.SURPLUS_LEVELS]))
                tankmanSkillVM.setIsGainProgressVisible(True)
                if float(self._gainedLevels[XpGainResult.SURPLUS_LEVELS]) == 0:
                    tankmanSkillVM.setIsLowGainedXp(True)
            wulfList.addViewModel(tankmanSkillVM)

    def _createList(self, wulfList, tankman, isTooltipEnable):
        skillsIconsSmall = R.images.gui.maps.icons.tankmen.skills.small
        for tankmanSkill in tankman.skills:
            tankmanSkillVM = CrewBookSkillModel()
            tankmanSkillVM.setIsTooltipEnable(isTooltipEnable)
            tankmanSkillVM.setIcon(skillsIconsSmall.dyn(getIconResourceName(tankmanSkill.extensionLessIconName))())
            tankmanSkillVM.setTankmanInvId(tankman.invID)
            tankmanSkillVM.setSkillName(tankmanSkill.name)
            wulfList.addViewModel(tankmanSkillVM)
            if tankmanSkill.level < MIN_ROLE_LEVEL and XpGainResult.NEW_SKILLS not in self._gainedLevels:
                tankmanSkillVM.setDescription(str(tankmanSkill.level))
                tankmanSkillVM.setIsUnlearned(True)
                if XpGainResult.SURPLUS_LEVELS in self._gainedLevels:
                    tankmanSkillVM.setGainProgress(str(self._gainedLevels[XpGainResult.SURPLUS_LEVELS]))
                    tankmanSkillVM.setIsGainProgressVisible(True)
                    if float(self._gainedLevels[XpGainResult.SURPLUS_LEVELS]) == 0:
                        tankmanSkillVM.setIsLowGainedXp(True)

    def _createShortList(self, wulfList, tankman, isTooltipEnable):
        reversedList = []
        hasUnlearnedSkill = False
        skillsCount = len(tankman.skills)
        skillsIconsSmall = R.images.gui.maps.icons.tankmen.skills.small
        for tankmanSkill in reversed(tankman.skills):
            tankmanSkillVM = CrewBookSkillModel()
            reversedList.append(tankmanSkillVM)
            tankmanSkillVM.setIsTooltipEnable(isTooltipEnable)
            tankmanSkillVM.setIcon(skillsIconsSmall.dyn(getIconResourceName(tankmanSkill.extensionLessIconName))())
            tankmanSkillVM.setTankmanInvId(tankman.invID)
            tankmanSkillVM.setSkillName(tankmanSkill.name)
            if tankmanSkill.level < MIN_ROLE_LEVEL and XpGainResult.NEW_SKILLS not in self._gainedLevels:
                hasUnlearnedSkill = True
                tankmanSkillVM.setDescription(str(tankmanSkill.level))
                tankmanSkillVM.setIsUnlearned(True)
                if XpGainResult.SURPLUS_LEVELS in self._gainedLevels:
                    tankmanSkillVM.setGainProgress(str(self._gainedLevels[XpGainResult.SURPLUS_LEVELS]))
                    tankmanSkillVM.setIsGainProgressVisible(True)
                    if float(self._gainedLevels[XpGainResult.SURPLUS_LEVELS]) == 0:
                        tankmanSkillVM.setIsLowGainedXp(True)
            if hasUnlearnedSkill:
                skillsCount -= 1
            tankmanSkillVM.setIsCompact(True)
            tankmanSkillVM.setDescription(str(skillsCount))
            break

        for viewModel in reversed(reversedList):
            wulfList.addViewModel(viewModel)
