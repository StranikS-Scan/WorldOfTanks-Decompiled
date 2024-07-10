# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/messenger/formatters/loot_box_auto_open_subformatters.py
from adisp import adisp_async, adisp_process
from fun_random.gui.Scaleform.daapi.view.lobby.server_events.awards_formatters import getFunAwardsPacker
from fun_random.gui.feature.util.fun_mixins import FunAssetPacksMixin
from fun_random.gui.impl.lobby.common.lootboxes import FunRandomLootBoxTypes
from fun_random.notification.decorators import FunRandomProgressionStageMessageDecorator
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import CurtailingAwardsComposer
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.loot_box_compensation_tooltip_types import LootBoxCompensationTooltipTypes
from gui.impl.lobby.awards.packers import getVehicleUIData
from gui.server_events.awards_formatters import AWARDS_SIZES, LABEL_ALIGN
from gui.server_events.bonuses import getNonQuestBonuses, LootBoxTokensBonus, getMergedCompensatedBonuses, VehiclesBonus
from gui.shared.formatters import text_styles
from gui.shared.gui_items.Vehicle import getNationLessName
from helpers import dependency
from messenger import g_settings
from messenger.formatters.auto_boxes_subformatters import AsyncAutoLootBoxSubFormatter
from messenger.formatters.service_channel import QuestAchievesFormatter
from messenger.formatters.service_channel_helpers import MessageData
from shared_utils import first
from skeletons.gui.shared import IItemsCache
MAX_AWARDS_COUNT = 4
MAIN_REWARD_PADDING = -12
MAIN_REWARD_GAP = -12
SMALL_REWARD_GAP = 5

class FunRandomMessageAwardsComposer(CurtailingAwardsComposer):
    itemsCache = dependency.descriptor(IItemsCache)

    def _packBonus(self, bonus, size=AWARDS_SIZES.SMALL):
        bonusDict = super(FunRandomMessageAwardsComposer, self)._packBonus(bonus, size)
        if size == AWARDS_SIZES.S232X174:
            bonusDict['padding'] = MAIN_REWARD_PADDING
            bonusDict['gap'] = MAIN_REWARD_GAP
            if bonus.align == LABEL_ALIGN.RIGHT:
                bonusDict['label'] = bonus.getFormattedLabel(text_styles.highTitle)
        elif size == AWARDS_SIZES.SMALL:
            bonusDict['gap'] = SMALL_REWARD_GAP
        if bonus.compensationReason is not None and bonus.compensationReason.bonusName == VehiclesBonus.VEHICLES_BONUS:
            self.__packCompensationData(bonus, bonusDict, size)
        return bonusDict

    def _packMergedBonuses(self, mergedBonuses, size=AWARDS_SIZES.SMALL):
        bonusesDict = super(FunRandomMessageAwardsComposer, self)._packMergedBonuses(mergedBonuses, size)
        if size == AWARDS_SIZES.SMALL:
            bonusesDict['gap'] = SMALL_REWARD_GAP
        return bonusesDict

    def __packCompensationData(self, bonus, bonusDict, size):
        vehicle = self.itemsCache.items.getItemByCD(bonus.compensationReason.specialArgs[0])
        if vehicle:
            iconAfterRes = R.images.gui.maps.icons.quests.bonuses.big.dyn(bonus.bonusName)
            if not iconAfterRes.exists():
                iconAfterRes = R.images.gui.maps.icons.quests.bonuses.big.gold
            specialArgs = {'labelBefore': '',
             'iconAfter': backport.image(iconAfterRes()),
             'labelAfter': bonus.getFormattedLabel(),
             'bonusName': bonus.bonusName,
             'countBefore': 1,
             'tooltipType': LootBoxCompensationTooltipTypes.VEHICLE}
            uiData = getVehicleUIData(vehicle)
            formattedTypeName = uiData['vehicleType']
            uiData['vehicleType'] = '{}_elite'.format(formattedTypeName) if vehicle.isElite else formattedTypeName
            specialArgs.update(uiData)
            vehicleName = getNationLessName(vehicle.name)
            vehIcon = R.images.gui.maps.shop.vehicles.c_180x135.dyn(vehicleName)()
            if vehIcon < 1:
                vehicleName = vehicleName.replace('-', '_')
                vehIcon = R.images.gui.maps.shop.vehicles.c_180x135.dyn(vehicleName)()
            specialArgs['iconBefore'] = backport.image(vehIcon) if vehIcon > 0 else ''
            bonusDict['isWulfTooltip'] = True
            bonusDict['tooltip'] = TOOLTIPS_CONSTANTS.VEHICLE_COMPENSATION
            bonusDict['specialArgs'] = [specialArgs.items()]
            bonusDict['overlayType'] = 'vehicleCompensation_%s' % size
            bonusDict['hasCompensation'] = False


class FunRandomLootboxAutoOpenFormatter(AsyncAutoLootBoxSubFormatter, FunAssetPacksMixin):
    __MESSAGE_TEMPLATE = 'FunRandomLootBoxesAutoOpenMessage'

    def __init__(self):
        super(FunRandomLootboxAutoOpenFormatter, self).__init__()
        self._achievesFormatter = QuestAchievesFormatter()

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        if isSynced:
            data = message.data or {}
            formattedRewards = g_settings.msgTemplates.format(self.__MESSAGE_TEMPLATE, ctx={'header': self.getModeUserName(),
             'rewardText': backport.text(R.strings.fun_random.notification.lootboxAutoOpen.rewardText())}, data={'linkageData': self._collectBonusesData(data)})
            settingsRewards = self._getGuiSettings(message, self.__MESSAGE_TEMPLATE, decorator=FunRandomProgressionStageMessageDecorator)
            callback([MessageData(formattedRewards, settingsRewards)])
        else:
            callback([MessageData(None, None)])
        return

    @classmethod
    def _isBoxOfThisGroup(cls, boxID):
        return cls._isBoxOfRequiredTypes(boxID, FunRandomLootBoxTypes.ALL)

    def _collectBonusesData(self, data):
        legendaryRewards = []
        otherRewards = []
        for lootBoxID, lootBoxData in data.iteritems():
            if self._isBoxOfThisGroup(lootBoxID):
                lb = self._itemsCache.items.tokens.getLootBoxByID(lootBoxID)
                awardList = legendaryRewards if lb.getType() == FunRandomLootBoxTypes.LEGENDARY else otherRewards
                awardList.append(lootBoxData.get('rewards', {}))

        composer = FunRandomMessageAwardsComposer(MAX_AWARDS_COUNT, getFunAwardsPacker())
        legendaryFormatted = composer.getFormattedBonuses(self.__getRawBonuses(legendaryRewards), AWARDS_SIZES.S232X174)
        bgIcon = backport.image(self.getModeIconsResRoot().library.notification_bg())
        if len(legendaryFormatted) == 1:
            return {'mainReward': first(legendaryFormatted),
             'rewards': composer.getFormattedBonuses(self.__getRawBonuses(otherRewards), AWARDS_SIZES.SMALL),
             'bgIcon': bgIcon}
        else:
            legendaryRewards.extend(otherRewards)
            rawBonuses = self.__getRawBonuses(legendaryRewards)
            mainFormatted = composer.getFormattedBonuses(rawBonuses, AWARDS_SIZES.S232X174)
            if len(mainFormatted) == 1:
                return {'mainReward': first(mainFormatted),
                 'rewards': [],
                 'bgIcon': bgIcon}
            return {'mainReward': None,
             'rewards': composer.getFormattedBonuses(rawBonuses, AWARDS_SIZES.SMALL),
             'bgIcon': bgIcon}
            return None

    def __getRawBonuses(self, rewards):
        mergedRewards = getMergedCompensatedBonuses(rewards)
        rawDataBonuses = []
        for k, v in mergedRewards.iteritems():
            rawDataBonuses.extend(getNonQuestBonuses(k, v))

        return [ b for b in rawDataBonuses if not isinstance(b, LootBoxTokensBonus) ]
