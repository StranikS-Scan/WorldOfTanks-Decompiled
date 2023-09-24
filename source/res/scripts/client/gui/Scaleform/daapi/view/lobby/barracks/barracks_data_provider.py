# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/barracks/barracks_data_provider.py
from typing import Dict
from CurrentVehicle import g_currentVehicle
from gui.Scaleform import MENU
from gui.Scaleform.framework.entities.DAAPIDataProvider import DAAPIDataProvider
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.game_control.restore_contoller import getTankmenRestoreInfo
from gui.impl import backport
from gui.server_events import recruit_helper
from gui.shared.formatters import text_styles
from gui.shared.gui_items.Tankman import Tankman, getCrewSkinIconSmall
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.gui_items.crew_skin import localizedFullName
from gui.shared.money import Currency
from gui.shared.tooltips import ACTION_TOOLTIPS_TYPE
from gui.shared.tooltips.formatters import packActionTooltipData
from gui.shared.tooltips.tankman import getRecoveryStatusText, formatRecoveryLeftValue
from gui.shared.utils.functions import makeTooltip
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency, i18n
from items.components.crew_skins_constants import NO_CREW_SKIN_ID
from skeletons.gui.game_control import IRestoreController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache

def _makeRecoveryPeriodText(restoreInfo):
    price, timeLeft = restoreInfo
    timeStr = formatRecoveryLeftValue(timeLeft)
    if not price.isDefined():
        textStyle = text_styles.main
    elif price.getCurrency() == Currency.GOLD:
        textStyle = text_styles.gold
    else:
        textStyle = text_styles.credits
    return textStyle(timeStr)


def _getTankmanLockMessage(invVehicle):
    if invVehicle.isInBattle:
        return (True, i18n.makeString('#menu:tankmen/lockReason/inbattle'))
    if invVehicle.invID == g_currentVehicle.invID and (g_currentVehicle.isInPrebattle() or g_currentVehicle.isInBattle()):
        return (True, i18n.makeString('#menu:tankmen/lockReason/prebattle'))
    return (True, i18n.makeString('#menu:tankmen/lockReason/disabled')) if invVehicle.isDisabled else (False, '')


@dependency.replace_none_kwargs(itemsCache=IItemsCache, lobbyContext=ILobbyContext)
def _packTankmanData(tankman, itemsCache=None, lobbyContext=None):
    tankmanVehicle = itemsCache.items.getItemByCD(tankman.vehicleNativeDescr.type.compactDescr)
    if tankman.isInTank:
        vehicle = itemsCache.items.getVehicle(tankman.vehicleInvID)
        vehicleID = vehicle.invID
        slot = tankman.vehicleSlotIdx
        isLocked, msg = _getTankmanLockMessage(vehicle)
        actionBtnEnabled = not isLocked
        isInCurrentTank = g_currentVehicle.isPresent() and tankmanVehicle.invID == g_currentVehicle.invID
        isInSelfVehicle = vehicle.shortUserName == tankmanVehicle.shortUserName
        isInSelfVehicleType = vehicle.type == tankmanVehicle.type
    else:
        isLocked, msg = False, ''
        actionBtnEnabled = True
        isInCurrentTank = False
        vehicleID = None
        slot = None
        isInSelfVehicle = True
        isInSelfVehicleType = True
    data = {'fullName': tankman.fullUserName,
     'rank': tankman.rankUserName,
     'specializationLevel': tankman.realRoleLevel.lvl,
     'role': tankman.roleUserName,
     'vehicleType': tankmanVehicle.shortUserName,
     'iconFile': tankman.smallIconPath,
     'rankIconFile': tankman.iconRank,
     'contourIconFile': tankmanVehicle.iconContour,
     'tankmanID': tankman.invID,
     'nationID': tankman.nationID,
     'typeID': tankmanVehicle.innationID,
     'roleType': tankman.descriptor.role,
     'tankType': tankmanVehicle.type,
     'inTank': tankman.isInTank,
     'compact': str(tankman.invID),
     'lastSkillLevel': tankman.descriptor.lastSkillLevel,
     'actionBtnEnabled': actionBtnEnabled,
     'inCurrentTank': isInCurrentTank,
     'vehicleID': vehicleID,
     'slot': slot,
     'locked': isLocked,
     'lockMessage': msg,
     'isInSelfVehicleClass': isInSelfVehicleType,
     'isInSelfVehicleType': isInSelfVehicle,
     'notRecruited': False,
     'hasCommanderFeature': tankman.role == Tankman.ROLES.COMMANDER,
     'roles': tankman.roles()}
    if tankman.skinID != NO_CREW_SKIN_ID:
        skinItem = itemsCache.items.getCrewSkin(tankman.skinID)
        iconFile = getCrewSkinIconSmall(skinItem.getIconID())
        data['iconFile'] = iconFile
        data['fullName'] = localizedFullName(skinItem)
    return data


def _packNotRecruitedTankman(recruitInfo):
    expiryTime = recruitInfo.getExpiryTime()
    recruitBeforeStr = i18n.makeString(MENU.BARRACKS_NOTRECRUITEDACTIVATEBEFORE, date=expiryTime) if expiryTime else ''
    availableRoles = recruitInfo.getRoles()
    roleType = availableRoles[0] if len(availableRoles) == 1 else ''
    result = {'rank': recruitBeforeStr,
     'specializationLevel': recruitInfo.getRoleLevel(),
     'role': text_styles.counter(recruitInfo.getLabel()),
     'vehicleType': '',
     'iconFile': recruitInfo.getSmallIconPath(),
     'rankIconFile': '',
     'contourIconFile': '',
     'tankmanID': -1,
     'nationID': -1,
     'typeID': -1,
     'roleType': roleType,
     'tankType': '',
     'inTank': False,
     'compact': '',
     'lastSkillLevel': recruitInfo.getLastSkillLevel(),
     'actionBtnEnabled': True,
     'inCurrentTank': False,
     'vehicleID': None,
     'slot': None,
     'locked': False,
     'lockMessage': '',
     'isInSelfVehicleClass': True,
     'isInSelfVehicleType': True,
     'notRecruited': True,
     'isRankNameVisible': True,
     'recoveryPeriodText': None,
     'roles': availableRoles if len(availableRoles) == 1 else [],
     'actionBtnLabel': MENU.BARRACKS_BTNRECRUITNOTRECRUITED,
     'actionBtnTooltip': TOOLTIPS.BARRACKS_TANKMEN_RECRUIT,
     'skills': [],
     'isSkillsVisible': False,
     'recruitID': str(recruitInfo.getRecruitID())}
    return result


def _packDismissedTankman(tankman):
    skillsList = []
    for skill in tankman.skills:
        skillsList.append({'tankmanID': tankman.invID,
         'id': str(tankman.skills.index(skill)),
         'name': skill.userName,
         'desc': skill.description,
         'icon': skill.icon,
         'level': skill.level,
         'active': skill.isEnable})

    newSkillsCount, lastNewSkillLvl = tankman.newSkillCount
    if newSkillsCount > 0:
        skillsList.append({'buy': True,
         'buyCount': newSkillsCount - 1,
         'tankmanID': tankman.invID,
         'level': lastNewSkillLvl})
    restoreInfo = getTankmenRestoreInfo(tankman)
    actionBtnTooltip = makeTooltip(TOOLTIPS.BARRACKS_TANKMEN_RECOVERYBTN_HEADER, getRecoveryStatusText(restoreInfo))
    tankmanData = _packTankmanData(tankman)
    tankmanData.update({'isRankNameVisible': False,
     'recoveryPeriodText': _makeRecoveryPeriodText(restoreInfo),
     'actionBtnLabel': MENU.BARRACKS_BTNRECOVERY,
     'actionBtnTooltip': actionBtnTooltip,
     'skills': skillsList,
     'isSkillsVisible': True})
    return tankmanData


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _packBuyBerthsSlot(itemsCache=None):
    berths = itemsCache.items.stats.tankmenBerthsCount
    berthPrice, berthCount = itemsCache.items.shop.getTankmanBerthPrice(berths)
    defaultBerthPrice, _ = itemsCache.items.shop.defaults.getTankmanBerthPrice(berths)
    action = None
    if berthPrice != defaultBerthPrice:
        action = packActionTooltipData(ACTION_TOOLTIPS_TYPE.ECONOMICS, 'berthsPrices', True, berthPrice, defaultBerthPrice)
    return {'buy': True,
     'price': backport.getGoldFormat(berthPrice.getSignValue(Currency.GOLD)),
     'actionPriceData': action,
     'count': berthCount}


def _packActiveTankman(tankman):
    if isinstance(tankman, Tankman):
        tankmanData = _packTankmanData(tankman)
        if tankman.isInTank:
            actionBtnLabel = MENU.BARRACKS_BTNUNLOAD
            actionBtnTooltip = TOOLTIPS.BARRACKS_TANKMEN_UNLOAD
        else:
            actionBtnLabel = MENU.BARRACKS_BTNDISSMISS
            actionBtnTooltip = TOOLTIPS.BARRACKS_TANKMEN_DISMISS
        tankmanData.update({'isRankNameVisible': True,
         'recoveryPeriodText': None,
         'actionBtnLabel': actionBtnLabel,
         'actionBtnTooltip': actionBtnTooltip,
         'skills': None,
         'isSkillsVisible': False})
        return tankmanData
    else:
        return tankman


class BarracksDataProvider(DAAPIDataProvider):
    restore = dependency.descriptor(IRestoreController)
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(BarracksDataProvider, self).__init__()
        self.__list = []
        self.__totalCount = 0
        self.__filteredCount = 0
        self.__placeCount = 0

    def buildList(self, items):
        self.__list = items
        self.refresh()

    def emptyItem(self):
        return None

    @property
    def collection(self):
        return self.__list

    def clear(self):
        self.__list = []

    @property
    def totalCount(self):
        return self.__totalCount

    @property
    def filteredCount(self):
        return self.__filteredCount

    @property
    def placeCount(self):
        return self.__placeCount

    def showDismissedTankmen(self, criteria):
        allTankmen = self.restore.getDismissedTankmen()
        filteredList = filter(criteria, allTankmen)
        self.__totalCount = len(allTankmen)
        self.__filteredCount = len(filteredList)
        self.__placeCount = self.restore.getMaxTankmenBufferLength()
        self.setItemWrapper(_packDismissedTankman)
        self.buildList(filteredList)

    def showNotRecruitedTankmen(self):
        notRecruitedList = recruit_helper.getAllRecruitsInfo(sortByExpireTime=True)
        self.__totalCount = self.__filteredCount = len(notRecruitedList)
        self.__placeCount = 0
        self.setItemWrapper(_packNotRecruitedTankman)
        self.buildList(notRecruitedList)

    def showActiveTankmen(self, criteria):
        allTankmen = self.itemsCache.items.removeUnsuitableTankmen(self.itemsCache.items.getTankmen().values(), ~REQ_CRITERIA.VEHICLE.IS_CREW_HIDDEN | ~REQ_CRITERIA.VEHICLE.BATTLE_ROYALE)
        self.__totalCount = len(allTankmen)
        tankmenInBarracks = 0
        tankmenList = [_packBuyBerthsSlot()]
        for tankman in allTankmen:
            if not tankman.isInTank:
                tankmenInBarracks += 1
            if criteria(tankman):
                tankmenList.append(tankman)

        self.__filteredCount = len(tankmenList) - 1
        slots = self.itemsCache.items.stats.tankmenBerthsCount
        if tankmenInBarracks < slots:
            tankmenList.insert(1, {'empty': True,
             'freePlaces': slots - tankmenInBarracks})
        self.__placeCount = max(slots - tankmenInBarracks, 0)
        self.setItemWrapper(_packActiveTankman)
        self.buildList(tankmenList)
