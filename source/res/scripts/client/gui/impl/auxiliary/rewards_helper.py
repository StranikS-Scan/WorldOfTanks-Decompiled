# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/auxiliary/rewards_helper.py
import itertools
import logging
import types
from itertools import izip_longest
import typing
from collections import namedtuple
from gui.impl.new_year.new_year_helper import formatRomanNumber
from shared_utils import first
from blueprints.BlueprintTypes import BlueprintTypes
from constants import PREMIUM_ENTITLEMENTS, LOOTBOX_TOKEN_PREFIX
from frameworks.wulf import ViewFlags
from battle_royale.gui.constants import ROYALE_POSTBATTLE_REWARDS_COUNT
from frameworks.wulf import ViewSettings
from gui.Scaleform.genConsts.PROGRESSIVEREWARD_CONSTANTS import PROGRESSIVEREWARD_CONSTANTS as prConst
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import BonusNameQuestsBonusComposer
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import LootBoxBonusComposer
from gui.impl import backport
from gui.impl.auxiliary.tooltips.compensation_tooltip import CompensationTooltipContent
from gui.impl.auxiliary.tooltips.compensation_tooltip import CrewSkinsCompensationTooltipContent
from gui.impl.auxiliary.tooltips.compensation_tooltip import VehicleCompensationTooltipContent
from gui.impl.backport import createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.blueprints.blueprint_screen_tooltips import BlueprintScreenTooltips
from gui.impl.gen.view_models.views.lobby.progressive_reward.progressive_reward_step_model import ProgressiveRewardStepModel
from gui.impl.gen.view_models.views.loot_box_compensation_tooltip_model import LootBoxCompensationTooltipModel
from gui.impl.gen.view_models.views.loot_box_compensation_tooltip_types import LootBoxCompensationTooltipTypes
from gui.impl.gen.view_models.views.loot_box_vehicle_compensation_tooltip_model import LootBoxVehicleCompensationTooltipModel
from gui.impl.gen.view_models.views.loot_box_view.blueprint_final_fragment_renderer_model import BlueprintFinalFragmentRendererModel
from gui.impl.gen.view_models.views.loot_box_view.blueprint_fragment_renderer_model import BlueprintFragmentRendererModel
from gui.impl.gen.view_models.views.loot_box_view.congrats_view_model import CongratsViewModel
from gui.impl.gen.view_models.views.loot_box_view.crew_book_renderer_model import CrewBookRendererModel
from gui.impl.gen.view_models.views.loot_box_view.loot_animated_renderer_model import LootAnimatedRendererModel
from gui.impl.gen.view_models.views.loot_box_view.loot_compensation_renderer_model import LootCompensationRendererModel
from gui.impl.gen.view_models.views.loot_box_view.loot_congrats_types import LootCongratsTypes
from gui.impl.gen.view_models.views.loot_box_view.loot_conversion_renderer_model import LootConversionRendererModel
from gui.impl.gen.view_models.views.loot_box_view.loot_def_renderer_model import LootDefRendererModel
from gui.impl.gen.view_models.views.loot_box_view.loot_new_year_toy_renderer_model import LootNewYearToyRendererModel
from gui.impl.gen.view_models.views.loot_box_view.loot_renderer_types import LootRendererTypes
from gui.impl.gen.view_models.views.loot_box_view.loot_vehicle_compensation_renderer_model import LootVehicleCompensationRendererModel
from gui.impl.gen.view_models.views.loot_box_view.loot_vehicle_renderer_model import LootVehicleRendererModel
from gui.impl.lobby.seniority_awards.seniority_awards_bonuses_packers import getSeniorityAwardsBonusPacker
from gui.impl.gen.view_models.views.loot_box_view.loot_vehicle_video_renderer_model import LootVehicleVideoRendererModel
from gui.server_events.awards_formatters import getPackRentVehiclesAwardPacker, getRoyaleAwardsPacker
from gui.server_events.awards_formatters import getPostBattleAwardsPacker
from gui.server_events.bonuses import getNonQuestBonuses, BlueprintsBonusSubtypes
from gui.server_events.recruit_helper import getRecruitInfo
from gui.shared.formatters import text_styles
from gui.shared.gui_items import Vehicle, GUI_ITEM_TYPE
from gui.shared.gui_items.Tankman import getCrewSkinIconBig
from gui.shared.gui_items.crew_skin import localizedFullName
from gui.shared.money import ZERO_MONEY, Money, Currency
from gui.shared.utils.functions import makeTooltip
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.utils.requesters.blueprints_requester import getUniqueBlueprints
from helpers import dependency, int2roman
from new_year.ny_toy_info import NewYearCurrentToyInfo
from new_year.ny_constants import GuestsQuestsTokens
from optional_bonuses import BONUS_MERGERS
from skeletons.gui.game_control import IBattlePassController
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController
STYLES_TAGS = ['NY_style']
VIDEO_TAGS = ['NY2019_video',
 'NY2020_video',
 'NY2021_video',
 'NY2022_video',
 'NY2023_video',
 'NY2024_video']
_logger = logging.getLogger(__name__)
_DEFAULT_ALIGN = 'center'
_DEFAULT_DISPLAYED_AWARDS_COUNT = 6
TMAN_TOKENS = 'tmanToken'

class BlueprintBonusTypes(object):
    BLUEPRINTS = 'blueprints'
    FINAL_BLUEPRINTS = 'finalBlueprints'
    BLUEPRINTS_ANY = 'blueprintsAny'
    ALL = (BLUEPRINTS, FINAL_BLUEPRINTS, BLUEPRINTS_ANY)


class CrewBonusTypes(object):
    CREW_BOOK_BONUSES = 'crewBooks'
    CREW_SKIN_BONUSES = 'crewSkins'
    ALL = (CREW_BOOK_BONUSES, CREW_SKIN_BONUSES)


NEW_STYLE_FORMATTED_BONUSES = tuple(itertools.chain((TMAN_TOKENS,)))
_BONUSES_ORDER = (Currency.CREDITS,
 PREMIUM_ENTITLEMENTS.BASIC,
 PREMIUM_ENTITLEMENTS.PLUS,
 Currency.GOLD,
 Currency.CRYSTAL,
 'vehicles',
 'freeXP',
 'freeXPFactor',
 'creditsFactor',
 'tankmen',
 'items',
 'slots',
 'berths',
 'dossier',
 'customizations',
 'goodies',
 'tokens',
 'blueprints',
 CrewBonusTypes.CREW_SKIN_BONUSES,
 CrewBonusTypes.CREW_BOOK_BONUSES,
 'finalBlueprints',
 Currency.EVENT_COIN,
 Currency.BPCOIN)
BLUEPRINTS_CONGRAT_TYPES = (LootCongratsTypes.CONGRAT_TYPE_BLUEPRINT, LootCongratsTypes.CONGRAT_TYPE_BLUEPRINT_PART)
_COMPENSATION_TOOLTIP_CONTENT_RES_IDS = (R.views.common.tooltip_window.loot_box_compensation_tooltip.LootBoxCompensationTooltipContent(), R.views.common.tooltip_window.loot_box_compensation_tooltip.CrewSkinsCompensationTooltipContent(), R.views.common.tooltip_window.loot_box_compensation_tooltip.LootBoxVehicleCompensationTooltipContent())
_COMPENSATION_TOOLTIP_CONTENT_CLASSES = {LootBoxCompensationTooltipTypes.CREW_SKINS: CrewSkinsCompensationTooltipContent,
 LootBoxCompensationTooltipTypes.BASE: CompensationTooltipContent,
 LootBoxCompensationTooltipTypes.VEHICLE: VehicleCompensationTooltipContent}
_MIN_PROBABILITY = 7
_MAX_PROBABILITY = 15
_MIN_VEHICLE_LVL_BLUEPRINT_AWARD = 8
SeniorityAwards = namedtuple('SeniorityAwards', 'bonuses currencies')

def getVehByStyleCD(styleIntCD):
    itemsCache = dependency.instance(IItemsCache)
    items = itemsCache.items
    style = items.getItemByCD(styleIntCD)
    vehicles = items.getVehicles(REQ_CRITERIA.CUSTOM(style.mayInstall))
    return first(vehicles.itervalues()) if vehicles else None


class LootRewardDefModelPresenter(object):
    __slots__ = ('_reward',)

    def __init__(self):
        super(LootRewardDefModelPresenter, self).__init__()
        self._reward = None
        return

    def getModel(self, reward, ttId, isSmall=False, showCongrats=False, isEpic=False):
        self._setReward(reward)
        model = self._createModel()
        with model.transaction() as m:
            self._formatModel(m, ttId, showCongrats)
            m.setRendererType(self._getRendererType())
            m.setIsSmall(isSmall)
            m.setIsEpic(isEpic)
        return model

    def _setReward(self, reward):
        self._reward = reward

    def _createModel(self):
        return LootDefRendererModel()

    def _getRendererType(self):
        return LootRendererTypes.DEF

    def _formatModel(self, model, ttId, showCongrats):
        with model.transaction() as m:
            m.setBonusName(self._reward.get('bonusName') or '')
            m.setIcon(self._reward.get('imgSource') or '')
            m.setLabelStr(self._reward.get('label') or '')
            m.setTooltipId(ttId)
            m.setHasCompensation(bool(self._reward.get('hasCompensation', False)))
            m.setLabelAlign(self._reward.get('align', _DEFAULT_ALIGN) or _DEFAULT_ALIGN)
            m.setHighlightType(self._reward.get('highlightIcon') or '')
            m.setOverlayType(self._reward.get('overlayIcon') or '')
            m.setIsEnabled(bool(self._reward.get('isEnabled', True)))
            m.setRewardName(self._reward.get('bonusName') or '')
            m.setSpecialAlias(self._reward.get('specialAlias') or '')


class LootRewardAnimatedModelPresenter(LootRewardDefModelPresenter):
    __slots__ = ('__anmType', '__anmRes', '__soundId')

    def __init__(self, anmType, anmUrl=R.invalid(), soundId=R.invalid()):
        super(LootRewardAnimatedModelPresenter, self).__init__()
        self.__anmType = anmType
        self.__anmRes = anmUrl
        self.__soundId = soundId

    def _createModel(self):
        return LootAnimatedRendererModel()

    def _getRendererType(self):
        return LootRendererTypes.ANIMATED

    def _formatModel(self, model, ttId, showCongrats):
        super(LootRewardAnimatedModelPresenter, self)._formatModel(model, ttId, showCongrats)
        with model.transaction() as tx:
            tx.setAnimationType(self.__anmType)
            tx.setAnimation(self.__anmRes)
            tx.setAnimationSound(self.__soundId)


class LootRewardConversionModelPresenter(LootRewardAnimatedModelPresenter):
    __slots__ = ('__iconFrom',)

    def __init__(self, iconFrom, soundId=R.invalid()):
        super(LootRewardConversionModelPresenter, self).__init__(LootAnimatedRendererModel.SWF_ANIMATION, R.animations.rewards.conversion(), soundId)
        self.__iconFrom = iconFrom

    def _createModel(self):
        return LootConversionRendererModel()

    def _getRendererType(self):
        return LootRendererTypes.CONVERSION

    def _formatModel(self, model, ttId, showCongrats):
        super(LootRewardConversionModelPresenter, self)._formatModel(model, ttId, showCongrats)
        model.setIconFrom(self.__iconFrom)


class CompensationModelPresenter(LootRewardAnimatedModelPresenter):
    __slots__ = ()

    def __init__(self, soundId=R.invalid()):
        super(CompensationModelPresenter, self).__init__(LootAnimatedRendererModel.SWF_ANIMATION, R.animations.rewards.conversion_money(), soundId)

    def _createModel(self):
        return LootCompensationRendererModel()

    def _getRendererType(self):
        return LootRendererTypes.COMPENSATION

    def _formatModel(self, model, ttId, showCongrats):
        super(CompensationModelPresenter, self)._formatModel(model, ttId, showCongrats)
        compensationReason = self._reward.get('compensationReason', None)
        with model.transaction() as tx:
            tx.setIconFrom(compensationReason.get('imgSource', ''))
            tx.setLabelBeforeStr(compensationReason.get('label', ''))
            tx.setLabelBefore(compensationReason.get('label', ''))
            tx.setIconBefore(compensationReason.get('imgSource', ''))
            tx.setLabelAfter(self._reward.get('label', ''))
            tx.setIconAfter(self._reward.get('imgSource', ''))
            tx.setLabelAlign(compensationReason.get('align', _DEFAULT_ALIGN) or _DEFAULT_ALIGN)
            tx.setLabelAlignAfter(self._reward.get('align', _DEFAULT_ALIGN) or _DEFAULT_ALIGN)
            specialArgs = compensationReason.get('specialArgs', None)
            if specialArgs and isinstance(specialArgs, (types.ListType, types.TupleType)):
                if len(specialArgs) > 1 and specialArgs[1]:
                    tx.setCountBefore(specialArgs[1])
        return


class VehicleCompensationModelPresenter(CompensationModelPresenter):
    __slots__ = ()
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, soundId=R.sounds.gui_lootbox_reward_circles()):
        super(VehicleCompensationModelPresenter, self).__init__(soundId)

    def _createModel(self):
        return LootVehicleCompensationRendererModel()

    def _getRendererType(self):
        return LootRendererTypes.VEHICLE_COMPENSATION

    def _formatModel(self, model, ttId, showCongrats):
        super(VehicleCompensationModelPresenter, self)._formatModel(model, ttId, showCongrats)
        compensationReason = self._reward.get('compensationReason', None)
        specialArgs = compensationReason.get('specialArgs', None)
        if specialArgs and isinstance(specialArgs, (types.ListType, types.TupleType)):
            compactDescr = specialArgs[0]
            vehicle = self.itemsCache.items.getItemByCD(compactDescr)
            if vehicle is not None:
                shortName = vehicle.shortUserName
                vehicleType = formatEliteVehicle(vehicle.isElite, vehicle.type)
                vehicleLevel = formatRomanNumber(vehicle.level)
                with model.transaction() as tx:
                    tx.setIconFrom(compensationReason.get('imgSource', ''))
                    tx.setLabelBeforeStr(compensationReason.get('label', ''))
                    tx.setLabelBefore('')
                    tx.setIconBefore(vehicle.getShopIcon(size=STORE_CONSTANTS.ICON_SIZE_SMALL))
                    tx.setLabelAfter(self._reward.get('label', ''))
                    tx.setIconAfter(self._reward.get('imgSource', ''))
                    tx.setVehicleType(vehicleType)
                    tx.setVehicleLvl(vehicleLevel)
                    tx.setVehicleName(shortName)
                    tx.setIsElite(vehicle.isElite)
        return


class VehicleCompensationWithoutAnimationPresenter(VehicleCompensationModelPresenter):

    def _getRendererType(self):
        return LootRendererTypes.VEHICLE_COMPENSATION_WITHOUT_ANIMATION


class LootNewYearToyPresenter(LootRewardDefModelPresenter):
    __slots__ = ('__toyID',)
    __itemsCache = dependency.descriptor(IItemsCache)
    __nyController = dependency.descriptor(INewYearController)

    def __init__(self):
        super(LootNewYearToyPresenter, self).__init__()
        self.__toyID = 0

    def _createModel(self):
        return LootNewYearToyRendererModel()

    def _getRendererType(self):
        return LootRendererTypes.NEW_YEAR_TOY

    def _setReward(self, reward):
        super(LootNewYearToyPresenter, self)._setReward(reward=reward)
        specialArgs = self._reward.get('specialArgs')
        if specialArgs:
            self.__toyID = specialArgs[0]

    def _formatModel(self, model, ttId, showCongrats):
        with model.transaction() as tx:
            toyInfo = NewYearCurrentToyInfo(self.__toyID)
            tx.setBonusName(self._reward.get('bonusName') or '')
            tx.setLabelStr(self._reward.get('label') or '')
            tx.setToyID(toyInfo.getID())
            tx.setDecorationImage(toyInfo.getIcon())
            tx.setRankImage(toyInfo.getRankIcon())
            tx.setIcon(self._reward.get('imgSource') or '')
            tx.setRank(toyInfo.getRank())


class CrewSkinsCompensationModelPresenter(CompensationModelPresenter):
    __slots__ = ()

    def _getRendererType(self):
        return LootRendererTypes.CREWSKINS_COMPENSATION


class BlueprintFinalFragmentModelPresenter(LootRewardAnimatedModelPresenter):
    __slots__ = ('__vehicle',)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(BlueprintFinalFragmentModelPresenter, self).__init__(LootAnimatedRendererModel.SWF_ANIMATION, R.animations.rewards.finalBlueprintFragment(), R.sounds.gui_blueprint_last_fragment_convert())

    def _createModel(self):
        return BlueprintFinalFragmentRendererModel() if self.__vehicle is not None and self.__vehicle.level >= _MIN_VEHICLE_LVL_BLUEPRINT_AWARD else super(BlueprintFinalFragmentModelPresenter, self)._createModel()

    def _getRendererType(self):
        return LootRendererTypes.BLUEPRINT_FINAL_FRAGMENT if self.__vehicle is not None and self.__vehicle.level >= _MIN_VEHICLE_LVL_BLUEPRINT_AWARD else super(BlueprintFinalFragmentModelPresenter, self)._getRendererType()

    def _setReward(self, reward):
        super(BlueprintFinalFragmentModelPresenter, self)._setReward(reward=reward)
        specialArgs = self._reward.get('specialArgs', None)
        if specialArgs and isinstance(specialArgs, (types.ListType, types.TupleType)):
            compactDescr = specialArgs[0]
            self.__vehicle = self.__itemsCache.items.getItemByCD(compactDescr)
        else:
            _logger.error('SpecialArgs for blueprint is not specified!')
        return

    def _formatModel(self, model, ttId, showCongrats):
        super(BlueprintFinalFragmentModelPresenter, self)._formatModel(model, ttId, showCongrats)
        if self.__vehicle is not None:
            self._formatVehicle(self.__vehicle, model, showCongrats)
        return

    def _formatVehicle(self, vehicle, model, showCongrats):
        _fillVehicleBlueprintCongratsModel(vehicle, model, self.__itemsCache, LootCongratsTypes.CONGRAT_TYPE_BLUEPRINT, showCongrats)

    @classmethod
    def validate(cls, reward, rewardType):
        vehicle = _getVehicleFromReward(reward)
        return False if not vehicle else vehicle is not None and vehicle.level >= _MIN_VEHICLE_LVL_BLUEPRINT_AWARD


class CrewBookModelPresenter(LootRewardDefModelPresenter):
    __slots__ = ()
    __itemsCache = dependency.descriptor(IItemsCache)

    def _createModel(self):
        return CrewBookRendererModel()

    def _getRendererType(self):
        return LootRendererTypes.CREW_BOOK

    def _formatModel(self, model, ttId, showCongrats):
        super(CrewBookModelPresenter, self)._formatModel(model, ttId, showCongrats)
        _fillCrewBookCongratsModel(model, LootCongratsTypes.INIT_CONGRAT_TYPE_CREW_BOOKS, showCongrats)

    @classmethod
    def validate(cls, reward, rewardType):
        if rewardType == LootCongratsTypes.INIT_CONGRAT_TYPE_CREW_BOOKS:
            return True
        else:
            specialArgs = reward.get('specialArgs', None)
            if not specialArgs or not isinstance(specialArgs, (types.ListType, types.TupleType)):
                return False
            compactDescr = specialArgs[0]
            item = cls.__itemsCache.items.getItemByCD(compactDescr)
            return not item.isCommon()


class BlueprintFragmentRewardPresenter(LootRewardDefModelPresenter):
    __slots__ = ('_vehicle',)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(BlueprintFragmentRewardPresenter, self).__init__()
        self._vehicle = None
        return

    def _setReward(self, reward):
        super(BlueprintFragmentRewardPresenter, self)._setReward(reward=reward)
        self._vehicle = None
        specialArgs = self._reward.get('specialArgs', None)
        if specialArgs and isinstance(specialArgs, (types.ListType, types.TupleType)):
            compactDescr = specialArgs[0]
            self._vehicle = self.__itemsCache.items.getItemByCD(compactDescr)
        else:
            _logger.error('Can not find vehicle compactDescr in specialArgs!')
        return

    def _getRendererType(self):
        return LootRendererTypes.VEHICLE if self._vehicle is not None and self._vehicle.level >= _MIN_VEHICLE_LVL_BLUEPRINT_AWARD else super(BlueprintFragmentRewardPresenter, self)._getRendererType()

    def _createModel(self):
        return BlueprintFragmentRendererModel() if self._vehicle is not None and self._vehicle.level >= _MIN_VEHICLE_LVL_BLUEPRINT_AWARD else super(BlueprintFragmentRewardPresenter, self)._createModel()

    def _formatModel(self, model, ttId, showCongrats):
        super(BlueprintFragmentRewardPresenter, self)._formatModel(model, ttId, showCongrats)
        if self._vehicle is not None:
            self._formatVehicle(self._vehicle, model, showCongrats)
        return

    def _formatVehicle(self, vehicle, model, showCongrats):
        _fillVehicleBlueprintCongratsModel(vehicle, model, self.__itemsCache, LootCongratsTypes.CONGRAT_TYPE_BLUEPRINT_PART, showCongrats)

    @classmethod
    def validate(cls, reward, rewardType):
        vehicle = _getVehicleFromReward(reward)
        return False if not vehicle else vehicle is not None and vehicle.level >= _MIN_VEHICLE_LVL_BLUEPRINT_AWARD


class VehicleRewardPresenter(LootRewardDefModelPresenter):
    __itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('_vehicle',)

    def __init__(self):
        super(VehicleRewardPresenter, self).__init__()
        self._vehicle = None
        return

    def _setReward(self, reward):
        super(VehicleRewardPresenter, self)._setReward(reward=reward)
        self._vehicle = None
        specialArgs = self._reward.get('specialArgs', None)
        if specialArgs and isinstance(specialArgs, (types.ListType, types.TupleType)):
            compactDescr = specialArgs[0]
            self._vehicle = self.__itemsCache.items.getItemByCD(compactDescr)
        else:
            _logger.error('Can not find vehicle compactDescr in specialArgs!')
        return

    def _getRendererType(self):
        return LootRendererTypes.VEHICLE if self._vehicle is not None else super(VehicleRewardPresenter, self)._getRendererType()

    def _createModel(self):
        return LootVehicleRendererModel() if self._vehicle is not None else super(VehicleRewardPresenter, self)._createModel()

    def _formatModel(self, model, ttId, showCongrats):
        super(VehicleRewardPresenter, self)._formatModel(model, ttId, showCongrats)
        if self._vehicle is not None:
            self._formatVehicle(self._vehicle, model, showCongrats)
        return

    def _formatVehicle(self, vehicle, model, showCongrats):
        with model.congratsViewModel.transaction() as tx:
            self._formatVehicleModel(showCongrats, tx, vehicle)

    def _formatVehicleModel(self, showCongrats, tx, vehicle):
        vehicleType = formatEliteVehicle(vehicle.isElite, vehicle.type)
        tx.setVehicleIsElite(vehicle.isElite)
        tx.setVehicleType(vehicleType)
        tx.setVehicleLvl(formatRomanNumber(vehicle.level))
        tx.setVehicleName(vehicle.userName)
        tx.setCongratsType(LootCongratsTypes.CONGRAT_TYPE_VEHICLE)
        tx.setCongratsSourceId(str(vehicle.intCD))
        tx.setShowCongrats(showCongrats)


class LootVehicleRewardPresenter(VehicleRewardPresenter):

    def _formatVehicle(self, vehicle, model, showCongrats):
        with model.congratsViewModel.transaction() as tx:
            self._formatVehicleModel(showCongrats, tx, vehicle)
            tx.setVehicleImage(vehicle.getSnapshotIcon() or '')


class RankedLootVehicleRewardPresenter(LootVehicleRewardPresenter):

    def _formatVehicle(self, vehicle, model, showCongrats):
        super(RankedLootVehicleRewardPresenter, self)._formatVehicle(vehicle, model, showCongrats)
        model.congratsViewModel.setVehicleImage(vehicle.getShopIcon())


DEF_COMPENSATION_PRESENTERS = {'vehicles': VehicleCompensationModelPresenter(),
 CrewBonusTypes.CREW_SKIN_BONUSES: CrewSkinsCompensationModelPresenter()}

def checkAndFillVehicles(bonus, alwaysVisibleBonuses, bonuses, onlyVideoVehicle=True):
    hasVehicle = False
    for vehBonus in bonus:
        for vehicle, _ in vehBonus.getVehicles():
            if isVideoVehicle(vehicle):
                hasVehicle = True
                break

        if hasVehicle and onlyVideoVehicle:
            alwaysVisibleBonuses.append(vehBonus)
        bonuses.append(vehBonus)

    return hasVehicle


def checkAndFillCustomizations(bonus, alwaysVisibleBonuses, bonuses):
    hasStyle = False
    for customBonus in bonus:
        for bonusData in customBonus.getCustomizations():
            bonusType = bonusData.get('custType')
            bonusValue = bonusData.get('value')
            item = customBonus.getC11nItem(bonusData)
            if bonusType and bonusValue and bonusType == 'style' and isSpecialStyle(item.intCD):
                hasStyle = True
                break

        if hasStyle:
            alwaysVisibleBonuses.append(customBonus)
        bonuses.append(customBonus)

    return hasStyle


def checkAndFillTokens(bonus, alwaysVisibleBonuses, bonuses):
    specialRewardType = ''
    for tokenBonus in bonus:
        allTokens = tokenBonus.getTokens()
        if _isInvisibleTokens(allTokens):
            continue
        for tID in allTokens:
            if getRecruitInfo(tID):
                specialRewardType = LootCongratsTypes.CONGRAT_TYPE_TANKMAN
                break
            if tID == GuestsQuestsTokens.TOKEN_CAT:
                specialRewardType = LootCongratsTypes.CONGRAT_TYPE_GUEST_C
                break

        if specialRewardType == LootCongratsTypes.CONGRAT_TYPE_TANKMAN:
            alwaysVisibleBonuses.append(tokenBonus)
        bonuses.append(tokenBonus)

    return specialRewardType


def formatEliteVehicle(isElite, typeName):
    ubFormattedTypeName = Vehicle.getIconResourceName(typeName)
    return '{}_elite'.format(ubFormattedTypeName) if isElite else ubFormattedTypeName


def splitPremiumDays(days):
    available = (360, 180, 90, 30, 14, 7, 3, 2, 1)

    def nearest(array, value):
        index = 0
        for idx, i in enumerate(array):
            index = idx
            if value >= i:
                break

        return array[index]

    result = []
    while days > 0:
        near = nearest(available, days)
        days -= near
        result.append(near)

    return result


class LootTankmanCongratsRewardPresenter(LootRewardDefModelPresenter):
    __slots__ = ('__recruitInfo', '__sourceID')

    def __init__(self):
        super(LootTankmanCongratsRewardPresenter, self).__init__()
        self.__recruitInfo = None
        self.__sourceID = ''
        return

    def _createModel(self):
        return LootVehicleVideoRendererModel()

    def _getRendererType(self):
        return LootRendererTypes.VEHICLE if self.__recruitInfo is not None else LootRendererTypes.DEF

    def _setReward(self, reward):
        super(LootTankmanCongratsRewardPresenter, self)._setReward(reward=reward)
        specialArgs = self._reward.get('specialArgs')
        if specialArgs:
            tmanTokenName = specialArgs[0]
            self.__recruitInfo = getRecruitInfo(tmanTokenName)
            self.__sourceID = tmanTokenName
        else:
            _logger.error('SpecialArgs for tankman is not specified!')

    def _formatModel(self, model, ttId, showCongrats):
        super(LootTankmanCongratsRewardPresenter, self)._formatModel(model, ttId, showCongrats)
        with model.transaction() as m:
            m.congratsViewModel.setVehicleIsElite(False)
            m.congratsViewModel.setVehicleType('')
            m.congratsViewModel.setVehicleLvl('')
            m.congratsViewModel.setVehicleName(self.__recruitInfo.getFullUserName())
            m.congratsViewModel.setVehicleImage(self.__recruitInfo.getSnapshotIcon() or '')
            m.congratsViewModel.setCongratsType(LootCongratsTypes.CONGRAT_TYPE_TANKMAN)
            m.congratsViewModel.setCongratsSourceId(self.__sourceID)
            m.congratsViewModel.setShowCongrats(True)
            m.congratsViewModel.setShineSwfAlias('')
            m.congratsViewModel.setAdvancedShineName('')
            m.setVideoSrc('')


class LootStyleCongratsRewardPresenter(LootRewardDefModelPresenter):
    __slots__ = ('__vehicle', '__resourceName', '__sourceID')

    def __init__(self):
        super(LootStyleCongratsRewardPresenter, self).__init__()
        self.__vehicle = None
        self.__resourceName = ''
        self.__sourceID = ''
        return

    def _createModel(self):
        return LootVehicleVideoRendererModel()

    def _getRendererType(self):
        return LootRendererTypes.VEHICLE_VIDEO if self.__vehicle is not None and self.__resourceName else LootRendererTypes.DEF

    def _setReward(self, reward):
        super(LootStyleCongratsRewardPresenter, self)._setReward(reward=reward)
        specialArgs = self._reward.get('specialArgs')
        if specialArgs:
            styleIntCD = specialArgs[0]
            if isSpecialStyle(styleIntCD):
                self.__vehicle = getVehByStyleCD(styleIntCD)
                self.__resourceName = Vehicle.getIconResourceName(Vehicle.getNationLessName(self.__vehicle.name))
                self.__sourceID = str(styleIntCD)
            else:
                self.__vehicle = None
        else:
            _logger.error('SpecialArgs for style is not specified!')
        return

    def _formatModel(self, model, ttId, showCongrats):
        super(LootStyleCongratsRewardPresenter, self)._formatModel(model, ttId, showCongrats)
        if self.__vehicle is not None:
            with model.transaction() as m:
                m.congratsViewModel.setVehicleIsElite(self.__vehicle.isElite)
                m.congratsViewModel.setVehicleType(formatEliteVehicle(self.__vehicle.isElite, self.__vehicle.type))
                m.congratsViewModel.setVehicleLvl(formatRomanNumber(self.__vehicle.level))
                m.congratsViewModel.setVehicleName(self.__vehicle.userName)
                m.congratsViewModel.setVehicleImage(self.__getStyleSnapshotImage() or '')
                m.congratsViewModel.setCongratsType(LootCongratsTypes.CONGRAT_TYPE_STYLE)
                m.congratsViewModel.setCongratsSourceId(self.__sourceID)
                m.congratsViewModel.setShowCongrats(True)
                m.congratsViewModel.setShineSwfAlias('')
                m.congratsViewModel.setAdvancedShineName('')
                m.setVideoSrc(self.__resourceName)
        return

    def __getStyleSnapshotImage(self):
        name = 'style_{}'.format(self.__resourceName)
        return RES_ICONS.getSnapshotIcon(name)


class LootVehicleVideoRewardPresenter(LootVehicleRewardPresenter):
    __slots__ = ('__resourceName',)

    def __init__(self):
        super(LootVehicleVideoRewardPresenter, self).__init__()
        self.__resourceName = None
        return

    def _setReward(self, reward):
        super(LootVehicleVideoRewardPresenter, self)._setReward(reward)
        self.__resourceName = None
        if self._vehicle is not None and isVideoVehicle(self._vehicle):
            self.__resourceName = Vehicle.getIconResourceName(Vehicle.getNationLessName(self._vehicle.name))
        return

    def _createModel(self):
        return LootVehicleVideoRendererModel() if self.__isVideoVehicle() else LootDefRendererModel()

    def _getRendererType(self):
        return LootRendererTypes.VEHICLE_VIDEO if self.__isVideoVehicle() else LootRendererTypes.DEF

    def _formatVehicle(self, vehicle, model, showCongrats):
        if self.__isVideoVehicle():
            super(LootVehicleVideoRewardPresenter, self)._formatVehicle(vehicle, model, showCongrats)
            model.setVideoSrc(self.__resourceName or '')

    def _formatModel(self, model, ttId, showCongrats):
        super(LootVehicleVideoRewardPresenter, self)._formatModel(model, ttId, showCongrats)
        if self.__isVideoVehicle():
            with model.congratsViewModel.transaction() as m:
                m.setShineSwfAlias('')
                m.setAdvancedShineName('')

    def __isVideoVehicle(self):
        return self.__resourceName is not None


_DEF_CONGRATS_VALIDATORS = {BlueprintsBonusSubtypes.FINAL_FRAGMENT: BlueprintFinalFragmentModelPresenter.validate,
 BlueprintsBonusSubtypes.VEHICLE_FRAGMENT: BlueprintFragmentRewardPresenter.validate,
 CrewBonusTypes.CREW_BOOK_BONUSES: CrewBookModelPresenter.validate}
_DEF_MODEL_PRESENTER = LootRewardDefModelPresenter()
DEF_MODEL_PRESENTERS = {CrewBonusTypes.CREW_BOOK_BONUSES: CrewBookModelPresenter(),
 BlueprintsBonusSubtypes.FINAL_FRAGMENT: BlueprintFinalFragmentModelPresenter(),
 BlueprintsBonusSubtypes.UNIVERSAL_FRAGMENT: LootRewardConversionModelPresenter(R.images.gui.maps.icons.blueprints.fragment.big.vehicle(), R.sounds.gui_blueprint_fragment_convert()),
 BlueprintsBonusSubtypes.NATION_FRAGMENT: LootRewardConversionModelPresenter(R.images.gui.maps.icons.blueprints.fragment.big.vehicle(), R.sounds.gui_blueprint_fragment_convert()),
 BlueprintsBonusSubtypes.VEHICLE_FRAGMENT: BlueprintFragmentRewardPresenter()}
RANKED_MODEL_PRESENTERS = {'vehicles': RankedLootVehicleRewardPresenter()}

@dependency.replace_none_kwargs(battlePass=IBattlePassController)
def setRewards(model, chapterID, battlePass=None):
    freeArray = model.getFreeFinalRewards()
    freeArray.clear()
    for freeReward in battlePass.getFreeFinalRewardTypes(chapterID):
        freeArray.addString(freeReward)

    freeArray.invalidate()
    paidArray = model.getPaidFinalRewards()
    paidArray.clear()
    for paidReward in battlePass.getPaidFinalRewardTypes(chapterID):
        paidArray.addString(paidReward)

    paidArray.invalidate()


def getRewardsBonuses(rewards, size='big', awardsCount=_DEFAULT_DISPLAYED_AWARDS_COUNT):
    formatter = BonusNameQuestsBonusComposer(awardsCount, getPackRentVehiclesAwardPacker())
    bonuses = []
    if rewards:
        for bonusType, bonusValue in rewards.iteritems():
            if bonusType == 'vehicles' and isinstance(bonusValue, list):
                for vehicleData in bonusValue:
                    bonuses.extend(getNonQuestBonuses(bonusType, vehicleData))

            bonus = getNonQuestBonuses(bonusType, bonusValue)
            bonuses.extend(bonus)

    formattedBonuses = formatter.getFormattedBonuses(bonuses, size)
    return formattedBonuses


def getRewardRendererModelPresenter(reward, presenters=None, compensationPresenters=None, defPresenter=_DEF_MODEL_PRESENTER):
    if presenters is None:
        presenters = DEF_MODEL_PRESENTERS
    if compensationPresenters is None:
        compensationPresenters = DEF_COMPENSATION_PRESENTERS
    bonusName = reward.get('bonusName', '')
    hasCompensation = reward.get('hasCompensation', False)
    if hasCompensation:
        compensationReason = reward.get('compensationReason', None)
        if compensationReason:
            return compensationPresenters.get(compensationReason.get('bonusName'), defPresenter)
    return presenters.get(bonusName, defPresenter)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getRewardTooltipContent(event, storedTooltipData=None, itemsCache=None):
    if event.contentID not in _COMPENSATION_TOOLTIP_CONTENT_RES_IDS:
        return
    else:
        tooltipData = {'iconBefore': event.getArgument('iconBefore', ''),
         'labelBefore': event.getArgument('labelBefore', ''),
         'iconAfter': event.getArgument('iconAfter', ''),
         'labelAfter': event.getArgument('labelAfter', ''),
         'bonusName': event.getArgument('bonusName', ''),
         'countBefore': event.getArgument('countBefore', 1),
         'wsFlags': ViewFlags.VIEW,
         'viewModelClazz': LootBoxCompensationTooltipModel}
        if event.contentID == R.views.common.tooltip_window.loot_box_compensation_tooltip.CrewSkinsCompensationTooltipContent():
            if storedTooltipData is None:
                return
            specialArgs = storedTooltipData.specialArgs
            if not specialArgs or not isinstance(specialArgs, (types.ListType, types.TupleType)):
                return
            crewSkin = itemsCache.items.getCrewSkin(specialArgs[0])
            crewSkinCount = specialArgs[1]
            tooltipData.update({'iconBefore': getCrewSkinIconBig(crewSkin.getIconID()),
             'labelBefore': localizedFullName(crewSkin),
             'countBefore': crewSkinCount,
             'layoutID': R.views.common.tooltip_window.loot_box_compensation_tooltip.CrewSkinsCompensationTooltipContent()})
            tooltipType = LootBoxCompensationTooltipTypes.CREW_SKINS
        elif event.contentID == R.views.common.tooltip_window.loot_box_compensation_tooltip.LootBoxVehicleCompensationTooltipContent():
            tooltipType = LootBoxCompensationTooltipTypes.VEHICLE
            specialArgs = storedTooltipData.specialArgs
            if specialArgs and isinstance(specialArgs, types.DictType):
                tooltipData.update(specialArgs)
            else:
                labelAfter = event.getArgument('labelAfter', '')
                if labelAfter.isdigit():
                    labelAfter = text_styles.gold(labelAfter)
                tooltipData.update({'iconBefore': event.getArgument('iconBefore', ''),
                 'labelBefore': event.getArgument('labelBefore', ''),
                 'iconAfter': event.getArgument('iconAfter', ''),
                 'labelAfter': labelAfter,
                 'vehicleName': event.getArgument('vehicleName', ''),
                 'vehicleType': event.getArgument('vehicleType', ''),
                 'isElite': event.getArgument('isElite', True),
                 'vehicleLvl': event.getArgument('vehicleLvl', '')})
            tooltipData.update({'viewModelClazz': LootBoxVehicleCompensationTooltipModel,
             'layoutID': R.views.common.tooltip_window.loot_box_compensation_tooltip.LootBoxVehicleCompensationTooltipContent()})
        else:
            tooltipType = LootBoxCompensationTooltipTypes.BASE
            layoutID = R.views.common.tooltip_window.loot_box_compensation_tooltip.LootBoxCompensationTooltipContent()
            tooltipData.update({'layoutID': layoutID})
        tooltipData['tooltipType'] = tooltipType
        settings = ViewSettings(tooltipData.get('layoutID', R.invalid()))
        settings.flags = tooltipData.get('wsFlags')
        settings.model = tooltipData.get('viewModelClazz')()
        settings.kwargs = tooltipData
        return _COMPENSATION_TOOLTIP_CONTENT_CLASSES[tooltipType](settings)


def getSeniorityAwardsVehicles(vehiclesRewards, sortKey=None):
    vehicles = [ vehCD for vehiclesDict in vehiclesRewards for vehCD in vehiclesDict if vehiclesDict[vehCD].get('compensatedNumber', 0) < 1 ]
    if sortKey:
        vehicles = sorted(vehicles, key=sortKey)
    return vehicles


def getSeniorityAwardsBonuses(rewards, excluded=(), sortKey=None):
    preparationRewardsCurrency(rewards)
    packer = getSeniorityAwardsBonusPacker()
    bonuses = []
    currencies = {}
    if rewards:
        for rewardType, rewardValue in rewards.items():
            if rewardType in excluded:
                continue
            if rewardType == 'currencies':
                currencies = {name:value['count'] for name, value in rewardValue.items()}
            nonQuestBonuses = getNonQuestBonuses(rewardType, rewardValue)
            for bonus in nonQuestBonuses:
                bonuses.extend(zip(packer.pack(bonus), packer.getToolTip(bonus)))

    if sortKey:
        bonuses = sorted(bonuses, key=sortKey)
    return SeniorityAwards(bonuses, currencies)


def getAdventAwardsBonuses(rewards, excluded=(), excludedCls=(), sortKey=None):
    from gui.impl.lobby.advent_calendar_v2.advent_calendar_v2_bonus_packer import getAdventCalendarV2BonusPacker
    packer = getAdventCalendarV2BonusPacker()
    bonuses = []
    if rewards:
        for bonus in rewards:
            if bonus.getName() in excluded or type(bonus) in excludedCls:
                continue
            bonuses.extend(izip_longest(packer.pack(bonus), packer.getToolTip(bonus), fillvalue=''))

    if sortKey:
        bonuses = sorted(bonuses, key=sortKey)
    return bonuses


def getProgressiveRewardBonuses(rewards, size='big', maxAwardCount=_DEFAULT_DISPLAYED_AWARDS_COUNT, packBlueprints=False, ctx=None):
    preparationRewardsCurrency(rewards)
    if packBlueprints:
        _packBlueprints(rewards)
    specialRewardType = ''
    formatter = LootBoxBonusComposer(maxAwardCount, getPostBattleAwardsPacker())
    bonuses = []
    alwaysVisibleBonuses = []
    if rewards:
        for bonusType, bonusValue in rewards.iteritems():
            if bonusType == 'blueprints':
                bonus = getNonQuestBonuses(bonusType, bonusValue, ctx={'isPacked': packBlueprints})
                blueprintCongrats = _checkAndFillBlueprints(bonus, alwaysVisibleBonuses, bonuses)
                if blueprintCongrats:
                    specialRewardType = blueprintCongrats
            if bonusType == 'premium' or bonusType == 'premium_plus':
                splitDays = splitPremiumDays(bonusValue)
                for day in splitDays:
                    bonus = getNonQuestBonuses(bonusType, day)
                    bonuses.extend(bonus)

            if bonusType in (CrewBonusTypes.CREW_SKIN_BONUSES, 'vehicles'):
                alwaysVisibleBonuses.extend(getNonQuestBonuses(bonusType, bonusValue))
            if bonusType == 'items':
                bonus = getNonQuestBonuses(bonusType, bonusValue)
                checkAndFillItems(bonus, alwaysVisibleBonuses, bonuses)
            bonus = getNonQuestBonuses(bonusType, bonusValue, ctx)
            bonuses.extend(bonus)

        bonuses.sort(key=bonusSortOrder)
        alwaysVisibleBonuses.sort(key=bonusSortOrder)
    formattedBonuses = formatter.getVisibleFormattedBonuses(bonuses, alwaysVisibleBonuses, size)
    return (formattedBonuses, specialRewardType)


def getRoyaleBonuses(bonuses, size='big'):
    bonuses.sort(key=_keySortOrder)
    alwaysVisibleBonuses = []
    commonBonuses = []
    for b in bonuses:
        commonBonuses.append(b)

    formatter = LootBoxBonusComposer(ROYALE_POSTBATTLE_REWARDS_COUNT, getRoyaleAwardsPacker())
    formattedBonuses = formatter.getVisibleFormattedBonuses(commonBonuses, alwaysVisibleBonuses, size)
    return formattedBonuses


def getRoyaleBonusesFromDict(rewards, size='big'):
    alwaysVisibleBonuses = []
    commonBonuses = []
    for bonusType, bonusValue in rewards.iteritems():
        commonBonuses.extend(getNonQuestBonuses(bonusType, bonusValue))

    commonBonuses.sort(key=_keySortOrder)
    alwaysVisibleBonuses.sort(key=_keySortOrder)
    formatter = LootBoxBonusComposer(ROYALE_POSTBATTLE_REWARDS_COUNT, getRoyaleAwardsPacker())
    formattedBonuses = formatter.getVisibleFormattedBonuses(commonBonuses, alwaysVisibleBonuses, size)
    return formattedBonuses


def fillStepsModel(currentStep, probability, maxSteps, hasCompleted, stepsModel):
    steps = _getProgressiveSteps(currentStep, probability, maxSteps, hasCompleted)
    for ind, (stepState, rewardType) in enumerate(steps):
        rendererModel = ProgressiveRewardStepModel()
        if ind == 0:
            rendererModel.setHasPreviousStep(False)
        rendererModel.setRewardType(rewardType)
        rendererModel.setStepState(stepState)
        stepsModel.addViewModel(rendererModel)


def getProgressiveRewardVO(currentStep, probability, maxSteps, descText='', isEnabled=True, showBg=False, align=prConst.WIDGET_LAYOUT_V, isHighTitle=False, hasCompleted=False):
    stepsVO = _getProgressiveStepsVO(currentStep, probability, maxSteps, hasCompleted)
    titleFormatter = text_styles.highlightText if isHighTitle else text_styles.middleTitle
    titleText = R.strings.menu.progressiveReward.widget.title()
    result = {'steps': stepsVO,
     'stepIdx': currentStep,
     'widgetAlign': align,
     'titleText': titleFormatter(backport.text(titleText)),
     'descText': descText,
     'btnTooltip': makeTooltip(body=TOOLTIPS.PROGRESSIVEREWARD_WIDGET_LINKBTN),
     'rewardTooltip': TOOLTIPS.PROGRESSIVEREWARD_WIDGET,
     'showBg': showBg,
     'isEnabled': isEnabled}
    return result


def getLastCongratsIndex(bonuses, rewardType):
    lastIndex = -1
    for index, reward in enumerate(bonuses):
        bonusName = reward.get('bonusName', '')
        if bonusName in _DEF_CONGRATS_VALIDATORS:
            congratsValidator = _DEF_CONGRATS_VALIDATORS.get(bonusName, None)
            if congratsValidator is None or congratsValidator(reward, rewardType):
                lastIndex = index

    return lastIndex


def _getProgressiveSteps(currentStep, probability, maxSteps, hasCompleted=False):
    steps = []
    for step in xrange(maxSteps):
        if step == maxSteps - 1:
            rewardType = prConst.REWARD_TYPE_BIG if hasCompleted else prConst.REWARD_TYPE_BIG_HIDDEN
        else:
            rewardType = prConst.REWARD_TYPE_SMALL if hasCompleted else prConst.REWARD_TYPE_SMALL_HIDDEN
        if currentStep > step:
            steps.append((prConst.STATE_OPENED, rewardType))
        if currentStep == step:
            pState = prConst.STATE_RECEIVED if hasCompleted else (prConst.STATE_PROB_MIN if probability < _MIN_PROBABILITY else (prConst.STATE_PROB_MAX if probability >= _MAX_PROBABILITY else prConst.STATE_PROB_MED))
            steps.append((pState, rewardType))
        steps.append((prConst.STATE_NOT_RECEIVED, rewardType))

    return steps


def _getProgressiveStepsVO(currentStep, probability, maxSteps, hasCompleted=False):

    def _getStepVO(state, rewardType):
        return {'stepState': state,
         'rewardType': rewardType}

    steps = _getProgressiveSteps(currentStep, probability, maxSteps, hasCompleted)
    return [ _getStepVO(state, rewardType) for state, rewardType in steps ]


def preparationRewardsCurrency(rewards):
    money = _getCompensationMoney(rewards)
    for currency in Currency.ALL:
        if currency in rewards:
            rewards[currency] -= money.get(currency, 0)
            if rewards[currency] <= 0:
                del rewards[currency]


def isVideoVehicle(vehicle):
    return True if _hasSpecialTag(vehicle, VIDEO_TAGS) else False


def _getStyleCDByVehCD(vehCD):
    itemsCache = dependency.instance(IItemsCache)
    items = itemsCache.items
    vehicle = items.getItemByCD(vehCD)
    if _hasSpecialTag(vehicle, STYLES_TAGS):
        criteria = REQ_CRITERIA.CUSTOMIZATION.FOR_VEHICLE(vehicle) | REQ_CRITERIA.CUSTOMIZATION.HAS_TAGS(STYLES_TAGS)
        styles = items.getItems(GUI_ITEM_TYPE.STYLE, criteria)
        if styles:
            return first(styles.iterkeys())
    return None


def _getVehiclesWithStyle(styleTags):
    itemsCache = dependency.instance(IItemsCache)
    items = itemsCache.items
    criteria = REQ_CRITERIA.VEHICLE.HAS_TAGS(styleTags)
    vehicles = items.getVehicles(criteria)
    return vehicles


def _hasSpecialTag(entity, tags):
    for styleTag in tags:
        if styleTag in entity.tags:
            return True

    return False


def isSpecialStyle(styleIntCD):
    itemsCache = dependency.instance(IItemsCache)
    style = itemsCache.items.getItemByCD(styleIntCD)
    if _hasSpecialTag(style, STYLES_TAGS):
        vehiclesList = _getVehiclesWithStyle(STYLES_TAGS)
        for vehicle in vehiclesList.values():
            if style.mayInstall(vehicle):
                return True

    return False


def getMergedLootBoxBonuses(bonusesList):
    result = {}
    for bonuses in bonusesList:
        for bonusName, bonusValue in bonuses.iteritems():
            if bonusName in BONUS_MERGERS:
                BONUS_MERGERS[bonusName](result, bonusName, bonusValue, False, 1, None)
            _logger.warning('BONUS_MERGERS has not bonus %s', bonusName)

    return result


def bonusSortOrder(bonus):
    return _BONUSES_ORDER.index(bonus.getName()) if bonus.getName() in _BONUSES_ORDER else len(_BONUSES_ORDER)


def _checkAndFillBlueprints(blueprintsList, alwaysVisibleBonuses, bonuses):
    congratsType = ''
    for blueprintBonus in blueprintsList:
        blueprintName = blueprintBonus.getBlueprintName()
        if blueprintName in BlueprintsBonusSubtypes.USE_CONGRATS:
            alwaysVisibleBonuses.append(blueprintBonus)
            congratsType = blueprintName if blueprintName in BLUEPRINTS_CONGRAT_TYPES else ''
        bonuses.append(blueprintBonus)

    return congratsType


def checkAndFillItems(itemsList, alwaysVisibleBonuses, bonuses):
    congratsType = ''
    for itemsBonus in itemsList:
        itemName = itemsBonus.getName()
        if itemName == CrewBonusTypes.CREW_BOOK_BONUSES:
            alwaysVisibleBonuses.append(itemsBonus)
        bonuses.append(itemsBonus)
        if any([ item.isModernized for item in itemsBonus.getItems().keys() if item.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE ]):
            congratsType = LootCongratsTypes.CONGRAT_TYPE_MODERNIZED_EQUIPMENT

    return congratsType


def validateVehicleCD(value):
    try:
        vehicleCD = int(value)
    except ValueError:
        _logger.warning('Wrong vehicle compact descriptor: %s!', value)
        return None

    return vehicleCD
    return None


def getBackportTooltipData(event, localDataStorage):
    tooltipId = event.getArgument('tooltipId')
    if tooltipId is None:
        return
    elif tooltipId in localDataStorage:
        return localDataStorage[tooltipId]
    else:
        if tooltipId == BlueprintScreenTooltips.TOOLTIP_BLUEPRINT:
            vehicleCD = validateVehicleCD(event.getArgument('vehicleCD'))
            if vehicleCD is not None:
                return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.BLUEPRINT_INFO, specialArgs=(vehicleCD, True))
        elif tooltipId == BlueprintScreenTooltips.TOOLTIP_BLUEPRINT_CONVERT_COUNT:
            vehicleCD = validateVehicleCD(event.getArgument('vehicleCD'))
            if vehicleCD is not None:
                return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.BLUEPRINT_CONVERT_INFO, specialArgs=[vehicleCD])
        return


def _getCompensationMoney(bonuses):
    money = ZERO_MONEY
    for bonusName, bonusValue in bonuses.iteritems():
        if bonusName == 'vehicles':
            vehicles = itertools.chain.from_iterable([ vehBonus.itervalues() for vehBonus in bonusValue ])
            for vehData in vehicles:
                if 'customCompensation' in vehData:
                    money += Money.makeFromMoneyTuple(vehData['customCompensation'])

    return money


def _keySortOrder(bonus):
    return _BONUSES_ORDER.index(bonus.getName()) if bonus.getName() in _BONUSES_ORDER else len(_BONUSES_ORDER)


def _getVehicleFromReward(reward):
    itemsCache = dependency.instance(IItemsCache)
    vehicle = None
    specialArgs = reward.get('specialArgs', None)
    if specialArgs and isinstance(specialArgs, (types.ListType, types.TupleType)):
        compactDescr = specialArgs[0]
        vehicle = itemsCache.items.getItemByCD(compactDescr)
    else:
        _logger.error('Can not find vehicle compactDescr in specialArgs!')
    return vehicle


def _fillVehicleBlueprintCongratsModel(vehicle, model, itemsCache, congratsType, showCongrats):
    if vehicle.level < _MIN_VEHICLE_LVL_BLUEPRINT_AWARD:
        return
    else:
        blueprintData = itemsCache.items.blueprints.getBlueprintData(vehicle.intCD, vehicle.level)
        if blueprintData is None:
            return
        filledCount, totalCount, canConvert = blueprintData
        with model.congratsViewModel.transaction() as tx:
            vehicleType = formatEliteVehicle(vehicle.isElite, vehicle.type)
            image = vehicle.getShopIcon()
            tx.setShowCongrats(showCongrats)
            tx.setVehicleIsElite(vehicle.isElite)
            tx.setVehicleType(vehicleType)
            tx.setVehicleLvl(int2roman(vehicle.level))
            tx.setVehicleName(vehicle.userName)
            tx.setVehicleImage(image)
            tx.setCongratsType(congratsType)
            tx.setCongratsSourceId(str(vehicle.intCD))
            tx.setFragments(filledCount)
            tx.setFragmentsTotal(totalCount)
            tx.setCanConvert(canConvert)
            tx.setShineSwfAlias(CongratsViewModel.SHINE_BLUE_ALIAS)
            tx.setAdvancedShineName(CongratsViewModel.ADVANCED_SHINE_BLUE)
        return


def _fillCrewBookCongratsModel(model, congratsType, showCongrats):
    with model.congratsViewModel.transaction() as tx:
        tx.setShowCongrats(showCongrats)
        tx.setCongratsType(congratsType)


def _packBlueprints(rewards):
    rawBlueprints = rewards.get('blueprints', {})
    if not rawBlueprints:
        return
    fragments, nationFragments, universalFragments = getUniqueBlueprints(rawBlueprints, isFullNationCD=True)
    fragments.update(nationFragments)
    if universalFragments > 0:
        fragments[BlueprintTypes.INTELLIGENCE_DATA] = universalFragments
    rewards['blueprints'] = fragments


def _isInvisibleTokens(tokens):
    return all((tID.startswith(LOOTBOX_TOKEN_PREFIX) and rec.count <= 0 for tID, rec in tokens.iteritems()))
