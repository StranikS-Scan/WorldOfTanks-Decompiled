# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/auxiliary/rewards_helper.py
import logging
import types
from frameworks.wulf import Resource
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.impl.gen.view_models.views.loot_box_view.loot_compensation_renderer_model import LootCompensationRendererModel
from gui.impl.gen.view_models.views.loot_box_view.loot_congrats_types import LootCongratsTypes
from gui.impl.gen.view_models.views.loot_box_view.loot_def_renderer_model import LootDefRendererModel
from gui.impl.gen.view_models.views.loot_box_view.loot_new_year_fragments_renderer_model import LootNewYearFragmentsRendererModel
from gui.impl.gen.view_models.views.loot_box_view.loot_vehicle_renderer_model import LootVehicleRendererModel
from gui.impl.gen.view_models.views.loot_box_view.loot_animated_renderer_model import LootAnimatedRendererModel
from gui.impl.gen.view_models.views.loot_box_view.loot_vehicle_compensation_renderer_model import LootVehicleCompensationRendererModel
from gui.impl.gen.view_models.views.loot_box_view.loot_new_year_toy_renderer_model import LootNewYearToyRendererModel
from gui.impl.gen.view_models.views.loot_box_view.loot_conversion_renderer_model import LootConversionRendererModel
from gui.impl.gen.view_models.views.loot_box_view.loot_renderer_types import LootRendererTypes
from gui.impl.gen.view_models.views.loot_box_view.loot_vehicle_video_renderer_model import LootVehicleVideoRendererModel
from gui.server_events.awards_formatters import getPackRentVehiclesAwardPacker
from gui.server_events.bonuses import getNonQuestBonuses
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import BonusNameQuestsBonusComposer
from gui.server_events.recruit_helper import getRecruitInfo
from gui.shared.gui_items import Vehicle, GUI_ITEM_TYPE
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency, int2roman
from shared_utils import first
from skeletons.gui.shared import IItemsCache
from gui.impl.new_year.views.toy_presenter import RANK_TO_COLOR_IMG
from new_year.ny_toy_info import NewYear19ToyInfo
NY_STYLE = 'NY2019_style'
NY_VIDEO = 'NY2019_video'
_logger = logging.getLogger(__name__)
_DEFAULT_ALIGN = 'center'
_DEFAULT_DISPLAYED_AWARDS_COUNT = 6

def getStyleCDByVehCD(vehCD):
    itemsCache = dependency.instance(IItemsCache)
    items = itemsCache.items
    vehicle = items.getItemByCD(vehCD)
    if _isStyleVehicle(vehicle):
        criteria = REQ_CRITERIA.CUSTOMIZATION.FOR_VEHICLE(vehicle) | REQ_CRITERIA.CUSTOMIZATION.HAS_TAGS([NY_STYLE])
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


def _isStyleVehicle(vehicle):
    return True if NY_STYLE in vehicle.tags else False


def getVehByStyleCD(styleIntCD):
    itemsCache = dependency.instance(IItemsCache)
    items = itemsCache.items
    style = items.getItemByCD(styleIntCD)
    vehicles = items.getVehicles(REQ_CRITERIA.CUSTOM(style.mayInstall))
    return first(vehicles.itervalues()) if vehicles else None


def isSpecialStyle(styleIntCD):
    itemsCache = dependency.instance(IItemsCache)
    style = itemsCache.items.getItemByCD(styleIntCD)
    if NY_STYLE in style.tags:
        vehiclesList = _getVehiclesWithStyle([NY_STYLE])
        for vehicle in vehiclesList.values():
            if style.mayInstall(vehicle):
                return True

    return False


def getVehicleStrID(vehicleName):
    return vehicleName.split(':')[1]


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


class LootVehicleRewardPresenter(LootRewardDefModelPresenter):
    __itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('_vehicle',)

    def __init__(self):
        super(LootVehicleRewardPresenter, self).__init__()
        self._vehicle = None
        return

    def _setReward(self, reward):
        super(LootVehicleRewardPresenter, self)._setReward(reward=reward)
        self._vehicle = None
        specialArgs = self._reward.get('specialArgs', None)
        if specialArgs and isinstance(specialArgs, (types.ListType, types.TupleType)):
            compactDescr = specialArgs[0]
            self._vehicle = self.__itemsCache.items.getItemByCD(compactDescr)
        else:
            _logger.error('Can not find vehicle compactDescr in specialArgs!')
        return

    def _getRendererType(self):
        return LootRendererTypes.VEHICLE if self._vehicle is not None else super(LootVehicleRewardPresenter, self)._getRendererType()

    def _createModel(self):
        return LootVehicleRendererModel() if self._vehicle is not None else super(LootVehicleRewardPresenter, self)._createModel()

    def _formatModel(self, model, ttId):
        super(LootVehicleRewardPresenter, self)._formatModel(model, ttId)
        if self._vehicle is not None:
            self._formatVehicle(self._vehicle, model)
        return

    def _formatVehicle(self, vehicle, model):
        with model.congratsViewModel.transaction() as tx:
            vehicleType = formatEliteVehicle(vehicle.isElite, vehicle.type)
            image = vehicle.getShopIcon()
            tx.setVehicleIsElite(vehicle.isElite)
            tx.setVehicleType(vehicleType)
            tx.setVehicleLvl(int2roman(vehicle.level))
            tx.setVehicleName(vehicle.userName)
            tx.setVehicleImage(image)
            tx.setCongratsType(LootCongratsTypes.CONGRAT_TYPE_VEHICLE)
            tx.setCongratsSourceId(str(vehicle.intCD))


class LootRewardAnimatedModelPresenter(LootRewardDefModelPresenter):
    __slots__ = ('__anmType', '__anmUrl', '__soundId')

    def __init__(self, anmType, anmUrl, soundId=Resource.INVALID):
        super(LootRewardAnimatedModelPresenter, self).__init__()
        self.__anmType = anmType
        self.__anmUrl = anmUrl
        self.__soundId = soundId

    def _createModel(self):
        return LootAnimatedRendererModel()

    def _getRendererType(self):
        return LootRendererTypes.ANIMATED

    def _formatModel(self, model, ttId):
        super(LootRewardAnimatedModelPresenter, self)._formatModel(model, ttId)
        with model.transaction() as tx:
            tx.setAnimationType(self.__anmType)
            tx.setAnimation(self.__anmUrl)
            tx.setAnimationSound(self.__soundId)


class LootRewardConversionModelPresenter(LootRewardAnimatedModelPresenter):
    __slots__ = ('__iconFrom',)

    def __init__(self, iconFrom, soundId=Resource.INVALID):
        super(LootRewardConversionModelPresenter, self).__init__(LootAnimatedRendererModel.SWF_ANIMATION, 'conversion', soundId)
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

    def __init__(self, soundId=Resource.INVALID):
        super(CompensationModelPresenter, self).__init__(LootAnimatedRendererModel.SWF_ANIMATION, 'conversion_money', soundId)

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
            tx.setBonusName(self._reward.get('userName', ''))
            tx.setLabelBefore(compensationReason.get('label', ''))
            tx.setIconBefore(compensationReason.get('imgSource', ''))
            tx.setLabelAfter(self._reward.get('label', ''))
            tx.setIconAfter(self._reward.get('imgSource', ''))
        return


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
                vehicleType = formatEliteVehicle(vehicle.isElite, vehicle.type)
                vehicleLevel = int2roman(vehicle.level)
                with model.transaction() as tx:
                    tx.setIconFrom(compensationReason.get('imgSource', ''))
                    tx.setLabelBeforeStr(compensationReason.get('label', ''))
                    tx.setBonusName(self._reward.get('userName', ''))
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

    def _formatModel(self, model, ttId):
        toyInfo = NewYear19ToyInfo(self.__toyID)
        model.setLabelStr(self._reward.get('label', '') or '')
        model.setToyID(toyInfo.getID())
        model.setDecorationImage(toyInfo.getIcon())
        model.setRankImage(RANK_TO_COLOR_IMG[toyInfo.getRank()])


class LootNewYearFragmentsPresenter(LootRewardDefModelPresenter):
    __slots__ = ('__count',)

    def __init__(self):
        super(LootNewYearFragmentsPresenter, self).__init__()
        self.__count = 0

    def _createModel(self):
        return LootNewYearFragmentsRendererModel()

    def _getRendererType(self):
        return LootRendererTypes.NEW_TEAR_FRAGMENTS

    def _setReward(self, reward):
        super(LootNewYearFragmentsPresenter, self)._setReward(reward=reward)
        specialArgs = self._reward.get('specialArgs')
        if specialArgs:
            self.__count = specialArgs[0]

    def _formatModel(self, model, ttId):
        model.setLabelStr(self._reward.get('label', '') or '')
        model.setIcon(self._reward.get('imgSource') or '')
        model.setCount(self.__count)


class LootVideoWithCongratsRewardPresenter(LootRewardDefModelPresenter):
    __slots__ = ('__videoStrID', '__congratsType', '__congratsData')
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, congratsType):
        super(LootVideoWithCongratsRewardPresenter, self).__init__()
        self.__videoStrID = None
        self.__congratsType = congratsType
        self.__congratsData = None
        return

    def _createModel(self):
        return LootVehicleVideoRendererModel()

    def _getRendererType(self):
        if self.__congratsType == LootCongratsTypes.CONGRAT_TYPE_STYLE and self.__videoStrID is not None:
            return LootRendererTypes.VEHICLE_VIDEO
        else:
            return LootRendererTypes.VEHICLE if self.__congratsType == LootCongratsTypes.CONGRAT_TYPE_TANKMAN else LootRendererTypes.DEF

    def _setReward(self, reward):
        super(LootVideoWithCongratsRewardPresenter, self)._setReward(reward=reward)
        self.__congratsData = {}
        self.__videoStrID = None
        specialArgs = self._reward.get('specialArgs')
        if specialArgs:
            if self.__congratsType == LootCongratsTypes.CONGRAT_TYPE_STYLE:
                styleIntCD = specialArgs[0]
                if isSpecialStyle(styleIntCD):
                    vehicle = getVehByStyleCD(styleIntCD)
                    vehicleStrId = Vehicle.getIconResourceName(getVehicleStrID(vehicle.name))
                    self.__congratsData['isElite'] = vehicle.isElite
                    self.__congratsData['vehicleType'] = formatEliteVehicle(vehicle.isElite, vehicle.type)
                    self.__congratsData['image'] = vehicleStrId
                    self.__congratsData['vehicleLvl'] = int2roman(vehicle.level)
                    self.__congratsData['vehicleName'] = vehicle.userName
                    self.__congratsData['sourceId'] = str(styleIntCD)
                    self.__videoStrID = vehicleStrId
                else:
                    _logger.error('Wrong special style!')
            elif self.__congratsType == LootCongratsTypes.CONGRAT_TYPE_TANKMAN:
                tmanTokenName = specialArgs[0]
                recruitInfo = getRecruitInfo(tmanTokenName)
                self.__congratsData['isElite'] = False
                self.__congratsData['vehicleType'] = ''
                self.__congratsData['image'] = recruitInfo.getSpecialIcon()
                self.__congratsData['vehicleLvl'] = ''
                self.__congratsData['vehicleName'] = self._reward.get('userName', '')
                self.__congratsData['sourceId'] = tmanTokenName
        else:
            _logger.error('SpecialArgs for style or tankman is not specified!')
        return

    def _formatModel(self, model, ttId):
        super(LootVideoWithCongratsRewardPresenter, self)._formatModel(model, ttId)
        with model.transaction() as m:
            m.congratsViewModel.setVehicleIsElite(self.__congratsData.get('isElite', False))
            m.congratsViewModel.setVehicleType(self.__congratsData.get('vehicleType', '') or '')
            m.congratsViewModel.setVehicleLvl(self.__congratsData.get('vehicleLvl', '') or '')
            m.congratsViewModel.setVehicleName(self.__congratsData.get('vehicleName', '') or '')
            m.congratsViewModel.setVehicleImage(self.__congratsData.get('image', '') or '')
            m.congratsViewModel.setCongratsType(self.__congratsType)
            m.congratsViewModel.setCongratsSourceId(self.__congratsData.get('sourceId', ''))
            m.setVideoSrc(self.__videoStrID or '')


_DEF_MODEL_PRESENTER = LootRewardDefModelPresenter()

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


def getRewardRendererModelPresenter(reward, presenters, compensationPresenters, derPresenter=_DEF_MODEL_PRESENTER):
    bonusName = reward.get('bonusName', '')
    hasCompensation = reward.get('hasCompensation', False)
    if hasCompensation:
        compensationReason = reward.get('compensationReason', None)
        if compensationReason:
            return compensationPresenters.get(compensationReason.get('bonusName'), derPresenter)
    return presenters.get(bonusName, derPresenter)


def formatEliteVehicle(isElite, typeName):
    ubFormattedTypeName = Vehicle.getIconResourceName(typeName)
    return '{}_elite'.format(ubFormattedTypeName) if isElite else ubFormattedTypeName
