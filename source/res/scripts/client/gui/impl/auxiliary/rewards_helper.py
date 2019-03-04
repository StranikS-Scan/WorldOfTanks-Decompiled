# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/auxiliary/rewards_helper.py
import logging
import types
import itertools
from frameworks.wulf import ViewFlags
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.Scaleform.genConsts.PROGRESSIVEREWARD_CONSTANTS import PROGRESSIVEREWARD_CONSTANTS as prConst
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.impl import backport
from gui.impl.auxiliary.tooltips.compensation_tooltip import CompensationTooltipContent
from gui.impl.auxiliary.tooltips.compensation_tooltip import CrewSkinsCompensationTooltipContent
from gui.impl.auxiliary.tooltips.compensation_tooltip import VehicleCompensationTooltipContent
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.progressive_reward.progressive_reward_step_model import ProgressiveRewardStepModel
from gui.impl.gen.view_models.views.loot_box_compensation_tooltip_model import LootBoxCompensationTooltipModel
from gui.impl.gen.view_models.views.loot_box_compensation_tooltip_types import LootBoxCompensationTooltipTypes
from gui.impl.gen.view_models.views.loot_box_vehicle_compensation_tooltip_model import LootBoxVehicleCompensationTooltipModel
from gui.impl.gen.view_models.views.loot_box_view.blueprint_final_fragment_renderer_model import BlueprintFinalFragmentRendererModel
from gui.impl.gen.view_models.views.loot_box_view.blueprint_fragment_renderer_model import BlueprintFragmentRendererModel
from gui.impl.gen.view_models.views.loot_box_view.congrats_view_model import CongratsViewModel
from gui.impl.gen.view_models.views.loot_box_view.loot_compensation_renderer_model import LootCompensationRendererModel
from gui.impl.gen.view_models.views.loot_box_view.loot_congrats_types import LootCongratsTypes
from gui.impl.gen.view_models.views.loot_box_view.loot_def_renderer_model import LootDefRendererModel
from gui.impl.gen.view_models.views.loot_box_view.loot_animated_renderer_model import LootAnimatedRendererModel
from gui.impl.gen.view_models.views.loot_box_view.loot_vehicle_compensation_renderer_model import LootVehicleCompensationRendererModel
from gui.impl.gen.view_models.views.loot_box_view.loot_conversion_renderer_model import LootConversionRendererModel
from gui.impl.gen.view_models.views.loot_box_view.loot_renderer_types import LootRendererTypes
from gui.server_events.awards_formatters import getPackRentVehiclesAwardPacker, getLootboxesAwardsPacker
from gui.server_events.bonuses import getNonQuestBonuses, BlueprintsBonusSubtypes
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import BonusNameQuestsBonusComposer
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import LootBoxBonusComposer
from gui.server_events.recruit_helper import getRecruitInfo
from gui.shared.formatters import text_styles
from gui.shared.gui_items import Vehicle, GUI_ITEM_TYPE
from gui.shared.gui_items.Tankman import getCrewSkinIconBig
from gui.shared.gui_items.crew_skin import localizedFullName
from gui.shared.money import ZERO_MONEY, Money, Currency
from gui.shared.utils.functions import makeTooltip
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency, int2roman
from helpers.func_utils import makeFlashPath
from shared_utils import first
from skeletons.gui.shared import IItemsCache
STYLES_TAGS = []
VIDEO_TAGS = []
_logger = logging.getLogger(__name__)
_DEFAULT_ALIGN = 'center'
_DEFAULT_DISPLAYED_AWARDS_COUNT = 6
_BONUSES_ORDER = (Currency.CREDITS,
 'premium',
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
 'crewSkins',
 'blueprints')
BLUEPRINTS_CONGRAT_TYPES = (LootCongratsTypes.CONGRAT_TYPE_BLUEPRINT, LootCongratsTypes.CONGRAT_TYPE_BLUEPRINT_PART)
_COMPENSATION_TOOLTIP_CONTENT_RES_IDS = (R.views.lootBoxCompensationTooltipContent(), R.views.crewSkinsCompensationTooltipContent(), R.views.lootBoxVehicleCompensationTooltipContent())
_COMPENSATION_TOOLTIP_CONTENT_CLASSES = {LootBoxCompensationTooltipTypes.CREW_SKINS: CrewSkinsCompensationTooltipContent,
 LootBoxCompensationTooltipTypes.BASE: CompensationTooltipContent,
 LootBoxCompensationTooltipTypes.VEHICLE: VehicleCompensationTooltipContent}
_MIN_PROBABILITY = 33
_MAX_PROBABILITY = 66
_MIN_VEHICLE_LVL_BLUEPRINT_AWARD = 8

class LootRewardDefModelPresenter(object):
    __slots__ = ('_reward',)

    def __init__(self):
        super(LootRewardDefModelPresenter, self).__init__()
        self._reward = None
        return

    def getModel(self, reward, ttId, isSmall=False):
        self._setReward(reward)
        model = self._createModel()
        with model.transaction() as m:
            self._formatModel(m, ttId)
            m.setRendererType(self._getRendererType())
            m.setIsSmall(isSmall)
        return model

    def _setReward(self, reward):
        self._reward = reward

    def _createModel(self):
        return LootDefRendererModel()

    def _getRendererType(self):
        return LootRendererTypes.DEF

    def _formatModel(self, model, ttId):
        with model.transaction() as m:
            m.setIcon(self._reward.get('imgSource') or '')
            m.setLabelStr(self._reward.get('label') or '')
            m.setTooltipId(ttId)
            m.setHasCompensation(bool(self._reward.get('hasCompensation', False)))
            m.setLabelAlign(self._reward.get('align', _DEFAULT_ALIGN) or _DEFAULT_ALIGN)
            m.setHighlightType(self._reward.get('highlightIcon') or '')
            m.setOverlayType(self._reward.get('overlayIcon') or '')


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

    def _formatModel(self, model, ttId):
        super(LootRewardAnimatedModelPresenter, self)._formatModel(model, ttId)
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

    def _formatModel(self, model, ttId):
        super(LootRewardConversionModelPresenter, self)._formatModel(model, ttId)
        model.setIconFrom(self.__iconFrom)


class CompensationModelPresenter(LootRewardAnimatedModelPresenter):
    __slots__ = ()

    def __init__(self, soundId=R.invalid()):
        super(CompensationModelPresenter, self).__init__(LootAnimatedRendererModel.SWF_ANIMATION, R.animations.rewards.conversion_money(), soundId)

    def _createModel(self):
        return LootCompensationRendererModel()

    def _getRendererType(self):
        return LootRendererTypes.COMPENSATION

    def _formatModel(self, model, ttId):
        super(CompensationModelPresenter, self)._formatModel(model, ttId)
        compensationReason = self._reward.get('compensationReason', None)
        with model.transaction() as tx:
            tx.setIconFrom(compensationReason.get('imgSource', ''))
            tx.setLabelBeforeStr(compensationReason.get('label', ''))
            tx.setBonusName(self._reward.get('bonusName', ''))
            tx.setLabelBefore(compensationReason.get('label', ''))
            tx.setIconBefore(compensationReason.get('imgSource', ''))
            tx.setLabelAfter(self._reward.get('label', ''))
            tx.setIconAfter(self._reward.get('imgSource', ''))
            tx.setLabelAlign(compensationReason.get('align', _DEFAULT_ALIGN) or _DEFAULT_ALIGN)
            tx.setLabelAlignAfter(self._reward.get('align', _DEFAULT_ALIGN) or _DEFAULT_ALIGN)
            specialArgs = compensationReason.get('specialArgs', None)
            if specialArgs and isinstance(specialArgs, (types.ListType, types.TupleType)):
                if len(specialArgs) > 1:
                    tx.setCountBefore(specialArgs[1])
        return


class CrewSkinsCompensationModelPresenter(CompensationModelPresenter):
    __slots__ = ()

    def _getRendererType(self):
        return LootRendererTypes.CREWSKINS_COMPENSATION


class VehicleCompensationModelPresenter(CompensationModelPresenter):
    __slots__ = ()
    itemsCache = dependency.descriptor(IItemsCache)

    def _createModel(self):
        return LootVehicleCompensationRendererModel()

    def _getRendererType(self):
        return LootRendererTypes.VEHICLE_COMPENSATION

    def _formatModel(self, model, ttId):
        super(VehicleCompensationModelPresenter, self)._formatModel(model, ttId)
        compensationReason = self._reward.get('compensationReason', None)
        specialArgs = compensationReason.get('specialArgs', None)
        if specialArgs and isinstance(specialArgs, (types.ListType, types.TupleType)):
            compactDescr = specialArgs[0]
            vehicle = self.itemsCache.items.getItemByCD(compactDescr)
            if vehicle is not None:
                shortName = vehicle.shortUserName
                vehicleType = _formatEliteVehicle(vehicle.isElite, vehicle.type)
                vehicleLevel = int2roman(vehicle.level)
                with model.transaction() as tx:
                    tx.setIconFrom(compensationReason.get('imgSource', ''))
                    tx.setLabelBeforeStr(compensationReason.get('label', ''))
                    tx.setBonusName(self._reward.get('bonusName', ''))
                    tx.setLabelBefore('')
                    tx.setIconBefore(vehicle.getShopIcon(size=STORE_CONSTANTS.ICON_SIZE_SMALL))
                    tx.setLabelAfter(self._reward.get('label', ''))
                    tx.setIconAfter(self._reward.get('imgSource', ''))
                    tx.setVehicleType(vehicleType)
                    tx.setVehicleLvl(vehicleLevel)
                    tx.setVehicleName(shortName)
                    tx.setIsElite(vehicle.isElite)
        return


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

    def _formatModel(self, model, ttId):
        super(BlueprintFinalFragmentModelPresenter, self)._formatModel(model, ttId)
        if self.__vehicle is not None:
            self._formatVehicle(self.__vehicle, model)
        return

    def _formatVehicle(self, vehicle, model):
        _fillVehicleBlueprintCongratsModel(vehicle, model, self.__itemsCache, LootCongratsTypes.CONGRAT_TYPE_BLUEPRINT)


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

    def _formatModel(self, model, ttId):
        super(BlueprintFragmentRewardPresenter, self)._formatModel(model, ttId)
        if self._vehicle is not None:
            self._formatVehicle(self._vehicle, model)
        return

    def _formatVehicle(self, vehicle, model):
        _fillVehicleBlueprintCongratsModel(vehicle, model, self.__itemsCache, LootCongratsTypes.CONGRAT_TYPE_BLUEPRINT_PART)


_DEF_MODEL_PRESENTER = LootRewardDefModelPresenter()
_DEF_COMPENSATION_PRESENTERS = {'vehicles': VehicleCompensationModelPresenter(),
 'crewSkins': CrewSkinsCompensationModelPresenter()}
_DEF_MODEL_PRESENTERS = {BlueprintsBonusSubtypes.FINAL_FRAGMENT: BlueprintFinalFragmentModelPresenter(),
 BlueprintsBonusSubtypes.UNIVERSAL_FRAGMENT: LootRewardConversionModelPresenter(R.images.gui.maps.icons.blueprints.fragment.big.vehicle(), R.sounds.gui_blueprint_fragment_convert()),
 BlueprintsBonusSubtypes.NATION_FRAGMENT: LootRewardConversionModelPresenter(R.images.gui.maps.icons.blueprints.fragment.big.vehicle(), R.sounds.gui_blueprint_fragment_convert()),
 BlueprintsBonusSubtypes.VEHICLE_FRAGMENT: BlueprintFragmentRewardPresenter()}

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
        presenters = _DEF_MODEL_PRESENTERS
    if compensationPresenters is None:
        compensationPresenters = _DEF_COMPENSATION_PRESENTERS
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
        if event.contentID == R.views.crewSkinsCompensationTooltipContent():
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
             'layoutID': R.views.crewSkinsCompensationTooltipContent()})
            tooltipType = LootBoxCompensationTooltipTypes.CREW_SKINS
        elif event.contentID == R.views.lootBoxVehicleCompensationTooltipContent():
            tooltipType = LootBoxCompensationTooltipTypes.VEHICLE
            tooltipData.update({'iconBefore': event.getArgument('iconBefore', ''),
             'labelBefore': event.getArgument('labelBefore', ''),
             'iconAfter': event.getArgument('iconAfter', ''),
             'labelAfter': event.getArgument('labelAfter', ''),
             'vehicleName': event.getArgument('vehicleName', ''),
             'vehicleType': event.getArgument('vehicleType', ''),
             'isElite': event.getArgument('isElite', True),
             'vehicleLvl': event.getArgument('vehicleLvl', ''),
             'viewModelClazz': LootBoxVehicleCompensationTooltipModel,
             'layoutID': R.views.lootBoxVehicleCompensationTooltipContent()})
        else:
            tooltipType = LootBoxCompensationTooltipTypes.BASE
            tooltipData.update({'layoutID': R.views.lootBoxCompensationTooltipContent()})
        tooltipData['tooltipType'] = tooltipType
        return _COMPENSATION_TOOLTIP_CONTENT_CLASSES[tooltipType](**tooltipData)


def getProgressiveRewardBonuses(rewards, size='big', maxAwardCount=_DEFAULT_DISPLAYED_AWARDS_COUNT):
    _preparationRewardsCurrency(rewards)
    specialRewardType = ''
    formatter = LootBoxBonusComposer(maxAwardCount, getLootboxesAwardsPacker())
    bonuses = []
    alwaysVisibleBonuses = []
    if rewards:
        for bonusType, bonusValue in rewards.iteritems():
            if bonusType == 'blueprints':
                bonus = getNonQuestBonuses(bonusType, bonusValue)
                blueprintCongrats = _checkAndFillBlueprints(bonus, alwaysVisibleBonuses, bonuses)
                if blueprintCongrats:
                    specialRewardType = blueprintCongrats
            if bonusType == 'premium':
                splitDays = _splitPremiumDays(bonusValue)
                for day in splitDays:
                    bonus = getNonQuestBonuses(bonusType, day)
                    bonuses.extend(bonus)

            if bonusType == 'crewSkins':
                alwaysVisibleBonuses.extend(getNonQuestBonuses(bonusType, bonusValue))
            bonus = getNonQuestBonuses(bonusType, bonusValue)
            bonuses.extend(bonus)

        bonuses.sort(key=_keySortOrder)
        alwaysVisibleBonuses.sort(key=_keySortOrder)
    formattedBonuses = formatter.getVisibleFormattedBonuses(bonuses, alwaysVisibleBonuses, size)
    return (formattedBonuses, specialRewardType)


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
    result = {'steps': stepsVO,
     'stepIdx': currentStep,
     'widgetAlign': align,
     'titleText': titleFormatter(backport.text(R.strings.menu.progressiveReward.widget.title())),
     'descText': descText,
     'btnTooltip': makeTooltip(body=TOOLTIPS.PROGRESSIVEREWARD_WIDGET_LINKBTN),
     'rewardTooltip': TOOLTIPS.PROGRESSIVEREWARD_WIDGET,
     'showBg': showBg,
     'isEnabled': isEnabled}
    return result


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


def _preparationRewardsCurrency(rewards):
    money = _getCompensationMoney(rewards)
    for currency in Currency.ALL:
        if currency in rewards:
            rewards[currency] -= money.get(currency, 0)
            if rewards[currency] <= 0:
                del rewards[currency]


def _isVideoVehicle(vehicle):
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


def _getVehByStyleCD(styleIntCD):
    itemsCache = dependency.instance(IItemsCache)
    items = itemsCache.items
    style = items.getItemByCD(styleIntCD)
    vehicles = items.getVehicles(REQ_CRITERIA.CUSTOM(style.mayInstall))
    return first(vehicles.itervalues()) if vehicles else None


def _isSpecialStyle(styleIntCD):
    itemsCache = dependency.instance(IItemsCache)
    style = itemsCache.items.getItemByCD(styleIntCD)
    if _hasSpecialTag(style, STYLES_TAGS):
        vehiclesList = _getVehiclesWithStyle(STYLES_TAGS)
        for vehicle in vehiclesList.values():
            if style.mayInstall(vehicle):
                return True

    return False


def _checkAndFillVehicles(bonus, alwaysVisibleBonuses, bonuses):
    hasVehicle = False
    for vehBonus in bonus:
        for vehicle, _ in vehBonus.getVehicles():
            if _isVideoVehicle(vehicle):
                hasVehicle = True
                break

        if hasVehicle:
            alwaysVisibleBonuses.append(vehBonus)
        bonuses.append(vehBonus)

    return hasVehicle


def _checkAndFillCustomizations(bonus, alwaysVisibleBonuses, bonuses):
    hasStyle = False
    for customBonus in bonus:
        for bonusData in customBonus.getCustomizations():
            bonusType = bonusData.get('custType')
            bonusValue = bonusData.get('value')
            item = customBonus.getC11nItem(bonusData)
            if bonusType and bonusValue and bonusType == 'style' and _isSpecialStyle(item.intCD):
                hasStyle = True
                break

        if hasStyle:
            alwaysVisibleBonuses.append(customBonus)
        bonuses.append(customBonus)

    return hasStyle


def _checkAndFillTokens(bonus, alwaysVisibleBonuses, bonuses):
    hasTman = False
    for tokenBonus in bonus:
        allTokens = tokenBonus.getTokens()
        for tID, _ in allTokens.iteritems():
            if getRecruitInfo(tID):
                hasTman = True
                break

        if hasTman:
            alwaysVisibleBonuses.append(tokenBonus)
        bonuses.append(tokenBonus)

    return hasTman


def _checkAndFillBlueprints(blueprintsList, alwaysVisibleBonuses, bonuses):
    congratsType = ''
    for blueprintBonus in blueprintsList:
        blueprintName = blueprintBonus.getBlueprintName()
        if blueprintName in BlueprintsBonusSubtypes.USE_CONGRATS:
            alwaysVisibleBonuses.append(blueprintBonus)
            congratsType = blueprintName if blueprintName in BLUEPRINTS_CONGRAT_TYPES else ''
        bonuses.append(blueprintBonus)

    return congratsType


def _splitPremiumDays(days):
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


def _formatEliteVehicle(isElite, typeName):
    ubFormattedTypeName = Vehicle.getIconResourceName(typeName)
    return '{}_elite'.format(ubFormattedTypeName) if isElite else ubFormattedTypeName


def _fillVehicleBlueprintCongratsModel(vehicle, model, itemsCache, congratsType):
    if vehicle.level < _MIN_VEHICLE_LVL_BLUEPRINT_AWARD:
        return
    filledCount, totalCount, canConvert = itemsCache.items.blueprints.getBlueprintData(vehicle.intCD, vehicle.level)
    with model.congratsViewModel.transaction() as tx:
        vehicleType = _formatEliteVehicle(vehicle.isElite, vehicle.type)
        image = makeFlashPath(vehicle.getShopIcon())
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
