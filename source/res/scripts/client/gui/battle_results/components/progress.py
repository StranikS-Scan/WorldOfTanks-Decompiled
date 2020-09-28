# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/components/progress.py
import logging
from itertools import chain
from gui.battle_results.components import base
from gui.battle_results.reusable.progress import VehicleProgressHelper
from gui.battle_results.br_constants import ProgressAction
from battle_pass_common import BattlePassConsts
from gui.impl import backport
from gui.impl.auxiliary.rewards_helper import getProgressiveRewardVO
from gui.impl.gen import R
from gui.shared.formatters import text_styles, getItemUnlockPricesVO, getItemPricesVO
from gui.shared.gui_items import Tankman
from gui.shared.gui_items.crew_skin import localizedFullName
from gui.shared.gui_items.Vehicle import getLevelIconPath
from gui.shared.gui_items.Tankman import getCrewSkinIconSmall
from gui.shared.gui_items.gui_item_economics import ItemPrice
from gui.Scaleform.genConsts.PROGRESSIVEREWARD_CONSTANTS import PROGRESSIVEREWARD_CONSTANTS as prConst
from gui.Scaleform.daapi.view.lobby.server_events.events_helpers import getBattlePassQuestInfo
from gui.Scaleform.daapi.view.lobby.customization.progression_helpers import getProgressionPostBattleInfo, parseEventID, getC11nProgressionLinkBtnParams
from helpers import dependency
from items.components.crew_skins_constants import NO_CREW_SKIN_ID
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.hangar_spaces_switcher import IHangarSpacesSwitcher
_logger = logging.getLogger(__name__)
_MIN_BATTLES_TO_SHOW_PROGRESS = 5

def _makeTankmanDescription(roleName, fullName):
    role = text_styles.main(roleName)
    name = text_styles.standard(fullName)
    return backport.text(R.strings.battle_results.common.crewMember.description(), name=name, role=role)


def _makeVehicleDescription(vehicle):
    vehicleType = text_styles.standard(vehicle.typeUserName)
    vehicleName = text_styles.main(vehicle.userName)
    return backport.text(R.strings.battle_results.common.vehicle.details(), vehicle=vehicleName, type=vehicleType)


@dependency.replace_none_kwargs(itemsCache=IItemsCache, lobbyContext=ILobbyContext)
def _makeTankmanVO(tman, avgBattles2NewSkill, itemsCache=None, lobbyContext=None):
    prediction = ''
    if avgBattles2NewSkill > 0:
        prediction = backport.text(R.strings.battle_results.common.newSkillPrediction(), battles=backport.getIntegralFormat(avgBattles2NewSkill))
    data = {'title': backport.text(R.strings.battle_results.common.crewMember.newSkill()),
     'prediction': prediction,
     'linkEvent': ProgressAction.NEW_SKILL_UNLOCK_TYPE,
     'linkId': tman.invID}
    if tman.skinID != NO_CREW_SKIN_ID and lobbyContext.getServerSettings().isCrewSkinsEnabled():
        skinItem = itemsCache.items.getCrewSkin(tman.skinID)
        data['tankmenIcon'] = getCrewSkinIconSmall(skinItem.getIconID())
        fullTankmanName = localizedFullName(skinItem)
    else:
        data['tankmenIcon'] = Tankman.getSmallIconPath(tman.nationID, tman.descriptor.iconID)
        fullTankmanName = tman.fullUserName
    data['description'] = _makeTankmanDescription(tman.roleUserName, fullTankmanName)
    return data


def _makeUnlockModuleVO(item, unlockProps):
    return {'title': backport.text(R.strings.battle_results.common.fitting.research()),
     'description': text_styles.main(item.userName),
     'fittingType': item.getGUIEmblemID(),
     'lvlIcon': getLevelIconPath(item.level),
     'price': getItemUnlockPricesVO(unlockProps),
     'linkEvent': ProgressAction.RESEARCH_UNLOCK_TYPE,
     'linkId': unlockProps.parentID}


def _makeUnlockVehicleVO(item, unlockProps, avgBattlesTillUnlock):
    prediction = ''
    if avgBattlesTillUnlock > 0:
        prediction = backport.text(R.strings.battle_results.common.researchPrediction(), battles=avgBattlesTillUnlock)
    return {'title': backport.text(R.strings.battle_results.common.vehicle.research()),
     'description': _makeVehicleDescription(item),
     'vehicleIcon': item.iconSmall,
     'lvlIcon': getLevelIconPath(item.level),
     'prediction': prediction,
     'price': getItemUnlockPricesVO(unlockProps),
     'linkEvent': ProgressAction.RESEARCH_UNLOCK_TYPE,
     'linkId': unlockProps.parentID}


def _makeVehiclePurchaseVO(item, unlockProps, price):
    return {'title': backport.text(R.strings.battle_results.common.vehicle.purchase()),
     'description': _makeVehicleDescription(item),
     'vehicleIcon': item.iconSmall,
     'lvlIcon': getLevelIconPath(item.level),
     'price': getItemPricesVO(ItemPrice(price=price, defPrice=price)),
     'linkEvent': ProgressAction.PURCHASE_UNLOCK_TYPE,
     'linkId': unlockProps.parentID}


def _makeModulePurchaseVO(item, unlockProps, price):
    return {'title': backport.text(R.strings.battle_results.common.fitting.purchase()),
     'description': text_styles.main(item.userName),
     'fittingType': item.itemTypeName,
     'lvlIcon': getLevelIconPath(item.level),
     'price': getItemPricesVO(ItemPrice(price=price, defPrice=price)),
     'linkEvent': ProgressAction.PURCHASE_UNLOCK_TYPE,
     'linkId': unlockProps.parentID}


class VehicleProgressBlock(base.StatsBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        for intCD, data in reusable.personal.getVehicleCDsIterator(result):
            vehicleBattleXp = data.get('xp', 0)
            pureCreditsReceived = data.get('pureCreditsReceived', 0)
            tankmenXps = dict(data.get('xpByTmen', []))
            helper = VehicleProgressHelper(intCD)
            ready2UnlockModulesVOs, ready2UnlockVehiclesVOs = self.__getReady2UnlockItemsVOs(helper, vehicleBattleXp)
            ready2BuyModulesVOs, ready2BuyVehiclesVOs = self.__getReady2BuyItemsVOs(helper, pureCreditsReceived)
            tankmenVOs = self.__getNewSkilledTankmenVOs(helper, tankmenXps)
            progress = list(chain(ready2UnlockModulesVOs, ready2BuyModulesVOs, tankmenVOs, ready2UnlockVehiclesVOs, ready2BuyVehiclesVOs))
            helper.clear()
            for item in progress:
                self.addComponent(self.getNextComponentIndex(), base.DirectStatsItem('', item))

    @staticmethod
    def __getReady2UnlockItemsVOs(helper, vehicleBattleXp):
        ready2UnlockVehicles, ready2UnlockModules = helper.getReady2UnlockItems(vehicleBattleXp)
        ready2UnlockVehiclesVOs = []
        for item, unlockProps, _ in ready2UnlockVehicles:
            avgBattles2Unlock = helper.getAvgBattles2Unlock(unlockProps)
            if not helper.isEnoughXPToUnlock(unlockProps):
                0 < avgBattles2Unlock <= _MIN_BATTLES_TO_SHOW_PROGRESS and ready2UnlockVehiclesVOs.append(_makeUnlockVehicleVO(item, unlockProps, avgBattles2Unlock))

        ready2UnlockModulesVOs = [ _makeUnlockModuleVO(item, unlockProps) for item, unlockProps, _ in ready2UnlockModules ]
        return (ready2UnlockModulesVOs, ready2UnlockVehiclesVOs)

    @staticmethod
    def __getReady2BuyItemsVOs(helper, pureCreditsReceived):
        ready2BuyVehicles, ready2BuyModules = helper.getReady2BuyItems(pureCreditsReceived)
        ready2BuyVehiclesVOs = [ _makeVehiclePurchaseVO(item, unlockProps, price) for item, unlockProps, price in ready2BuyVehicles ]
        ready2BuyModulesVOs = [ _makeModulePurchaseVO(item, unlockProps, price) for item, unlockProps, price in ready2BuyModules ]
        return (ready2BuyModulesVOs, ready2BuyVehiclesVOs)

    @staticmethod
    def __getNewSkilledTankmenVOs(helper, tankmenXps):
        tankmenVOs = []
        for tman, isCompletedSkill in helper.getNewSkilledTankmen(tankmenXps):
            avgBattles2NewSkill = 0
            if not isCompletedSkill:
                avgBattles2NewSkill = helper.getAvgBattles2NewSkill(tman)
                if avgBattles2NewSkill <= 0 or avgBattles2NewSkill > _MIN_BATTLES_TO_SHOW_PROGRESS:
                    continue
            tankmenVOs.append(_makeTankmanVO(tman, avgBattles2NewSkill))

        return tankmenVOs


class QuestsProgressBlock(base.StatsBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        questsProgress = reusable.progress.getPlayerQuestProgress()
        personalMissions = reusable.progress.getPlayerPersonalMissionProgress()
        personalMissionInfo = reusable.progress.packPersonalMissions(personalMissions)
        commonQuestsInfo = reusable.progress.packQuests(questsProgress)
        if reusable.battlePassProgress is not None:
            if BattlePassConsts.PROGRESSION_INFO_PREV in reusable.battlePassProgress:
                info = reusable.battlePassProgress[BattlePassConsts.PROGRESSION_INFO_PREV]
                self.addComponent(self.getNextComponentIndex(), base.DirectStatsItem('', getBattlePassQuestInfo(info)))
            if BattlePassConsts.PROGRESSION_INFO in reusable.battlePassProgress:
                info = reusable.battlePassProgress[BattlePassConsts.PROGRESSION_INFO]
                self.addComponent(self.getNextComponentIndex(), base.DirectStatsItem('', getBattlePassQuestInfo(info)))
        for info in personalMissionInfo:
            self.addComponent(self.getNextComponentIndex(), base.DirectStatsItem('', info))

        for vehicleIntCD, c11nProgression in reusable.personal.getC11nProgress().iteritems():
            for intCD, progressionData in sorted(c11nProgression.iteritems(), key=lambda (_, d): -d.get('level', 0)):
                info = getProgressionPostBattleInfo(intCD, vehicleIntCD, progressionData)
                if info is not None:
                    self.addComponent(self.getNextComponentIndex(), ProgressiveCustomizationVO('', info))

        for info in commonQuestsInfo:
            self.addComponent(self.getNextComponentIndex(), base.DirectStatsItem('', info))

        return


class ProgressiveRewardVO(base.StatsItem):
    __slots__ = ()

    def _convert(self, record, reusable):
        data = reusable.progress.processProgressiveRewardData()
        if data is None:
            return
        else:
            descText = text_styles.standard(backport.text(R.strings.battle_results.progressiveReward.descr()))
            return getProgressiveRewardVO(currentStep=data.currentStep, probability=data.probability, maxSteps=data.maxSteps, showBg=True, align=prConst.WIDGET_LAYOUT_H, isHighTitle=True, hasCompleted=data.hasCompleted, descText=descText)


class ProgressiveCustomizationVO(base.DirectStatsItem):
    _itemsCache = dependency.descriptor(IItemsCache)
    __hangarSpacesSwitcher = dependency.descriptor(IHangarSpacesSwitcher)
    __slots__ = ()

    def getVO(self):
        questInfo = self._value.get('questInfo', {})
        questID = questInfo.get('questID', None)
        if questInfo and questID is not None:
            _, vehicleIntCD = parseEventID(questID)
            vehicle = self._itemsCache.items.getItemByCD(vehicleIntCD)
            linkBtnEnabled, linkBtnTooltip = getC11nProgressionLinkBtnParams(vehicle)
            switchItems = self.__hangarSpacesSwitcher.itemsToSwitch
            isBrSpace = self.__hangarSpacesSwitcher.currentItem == switchItems.BATTLE_ROYALE
            if isBrSpace:
                linkBtnEnabled = False
            self._value['linkBtnEnabled'] = linkBtnEnabled
            self._value['linkBtnTooltip'] = backport.text(linkBtnTooltip)
        return self._value
