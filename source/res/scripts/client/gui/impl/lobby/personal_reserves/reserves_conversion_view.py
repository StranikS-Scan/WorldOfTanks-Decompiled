# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_reserves/reserves_conversion_view.py
import typing
from frameworks.wulf import ViewFlags, ViewSettings
from goodies.goodie_constants import GOODIE_RESOURCE_TYPE
from gui.goodies.goodie_items import Booster, getBoosterGuiType
from gui.goodies.pr2_conversion_result import getConversionDataProvider
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.personal_reserves.converted_booster_list_item import ConvertedBoosterListItem
from gui.impl.gen.view_models.views.lobby.personal_reserves.reserves_conversion_view_model import ReservesConversionViewModel
from gui.impl.lobby.personal_reserves.reserves_constants import PERSONAL_RESERVES_SOUND_SPACE
from gui.impl.lobby.personal_reserves.view_utils.reserves_view_monitor import ReservesViewMonitor
from gui.shared.event_dispatcher import closeViewsExceptReservesActivationView
from helpers import dependency
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.shared import IItemsCache
from soft_exception import SoftException
from uilogging.personal_reserves.loggers import PersonalReservesMetricsLogger
from uilogging.personal_reserves.logging_constants import PersonalReservesLogKeys
if typing.TYPE_CHECKING:
    from typing import Tuple, Optional, List, Any
    from frameworks.wulf import Array

class ReservesConversionView(ReservesViewMonitor):
    __slots__ = ('_uiLogger',)
    _COMMON_SOUND_SPACE = PERSONAL_RESERVES_SOUND_SPACE
    _goodiesCache = dependency.descriptor(IGoodiesCache)
    _itemsCache = dependency.descriptor(IItemsCache)
    _uiLoader = dependency.descriptor(IGuiLoader)
    BOOSTER_TYPE_TO_MODEL_DICT = {'booster_crew_xp': (lambda model: model.crewXPConverted, lambda model: model.crewXPConverted),
     'booster_credits': (lambda model: model.creditsConverted, lambda model: model.creditsConverted),
     'booster_free_xp': (None, lambda model: model.freeXPConverted),
     'booster_xp': (lambda model: model.battleXPConverted, lambda model: model.battleXPConverted)}

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_TOP_SUB_VIEW
        settings.model = ReservesConversionViewModel()
        super(ReservesConversionView, self).__init__(settings)
        self._uiLogger = PersonalReservesMetricsLogger(parent=PersonalReservesLogKeys.HANGAR, item=PersonalReservesLogKeys.RESERVES_CONVERSION_WINDOW)

    @property
    def _viewModel(self):
        return self.getViewModel()

    def _initialize(self, *args, **kwargs):
        super(ReservesConversionView, self)._initialize(*args, **kwargs)
        self._viewModel.onClose += self._onClose
        self._uiLogger.onViewInitialize()

    def _finalize(self):
        self._viewModel.onClose -= self._onClose
        self._uiLogger.onViewFinalize()
        super(ReservesConversionView, self)._finalize()

    def _getBoosterDescr(self, boosterID):
        booster = self._goodiesCache.getBooster(boosterID)
        value = booster.getFormattedValue()
        effectiveTime = booster.getEffectTimeStr(hoursOnly=True)
        return backport.text(R.strings.personal_reserves.conversionView.boosterDescription(), value=value, effectTime=effectiveTime)

    def _onLoading(self, *args, **kwargs):
        super(ReservesConversionView, self)._onLoading(*args, **kwargs)
        self._fillViewModel()

    def _fillViewModel(self):
        with self._viewModel.transaction() as model:
            result = self._itemsCache.items.goodies.pr2ConversionResult
            provider = getConversionDataProvider(result)
            self._buildConversionItemsListSimple(GOODIE_RESOURCE_TYPE.FREE_XP, provider, model)
            self._buildConversionItemsListSpecial(provider, model)
            self._buildConversionItemsListSimple(GOODIE_RESOURCE_TYPE.CREDITS, provider, model)
            self._buildConversionItemsListSimple(GOODIE_RESOURCE_TYPE.XP, provider, model)

    def _buildConversionItemsListSimple(self, boosterType, provider, model):
        prConversionResult = provider.getResult()
        boosterGuiType = getBoosterGuiType(boosterType)
        self._buildConversionItemsLists(model, boosterGuiType, *self._prepareData(prConversionResult.get(boosterGuiType)))

    def _buildConversionItemsListSpecial(self, provider, model):
        prConversionResult = provider.getResult()
        prConversionResultSum = provider.getResultSum()
        boosterGuiType = getBoosterGuiType(GOODIE_RESOURCE_TYPE.FREE_XP)
        freeXPData = prConversionResult.get(boosterGuiType)
        sumIds = set()
        if freeXPData is not None:
            sumIds = {data[3] for data in freeXPData}
        boosterGuiType = getBoosterGuiType(GOODIE_RESOURCE_TYPE.CREW_XP)
        oldIds, oldCounts, newIds, _ = self._prepareData(prConversionResult.get(boosterGuiType), sort=True)
        sumIds.update(newIds)
        newCounts = [ prConversionResultSum[newId] for newId in sumIds ]
        self._buildConversionItemsLists(model, boosterGuiType, oldIds, oldCounts, list(sumIds), newCounts)
        return

    def _buildConversionItemsLists(self, model, boosterGuiType, oldIds, oldCounts, newIds, newCounts):
        conversionListsNew, conversionListsOld = self._getModelByGuiType(boosterGuiType)
        if conversionListsNew is not None:
            self._buildConversionItemList(newIds, newCounts, conversionListsNew(model).getNewBoosters())
        if conversionListsOld is not None:
            self._buildConversionItemList(oldIds, oldCounts, conversionListsOld(model).getOldBoosters())
        return

    def _prepareData(self, resultByGUIType, sort=True):
        if resultByGUIType is None:
            return ([],
             [],
             [],
             [])
        else:
            if sort:
                sortedData = sorted(resultByGUIType, key=lambda value: self._boosterComparisonKey(value[0]), reverse=True)
            else:
                sortedData = resultByGUIType
            oldIds, oldCounts, newIds, newCounts = ([],
             [],
             [],
             [])
            for result in sortedData:
                oldIds.append(result[0])
                oldCounts.append(result[2])
                newIds.append(result[3])
                newCounts.append(result[4])

            return (oldIds,
             oldCounts,
             newIds,
             newCounts)

    def _getModelByGuiType(self, boosterGUIType):
        try:
            return self.BOOSTER_TYPE_TO_MODEL_DICT[boosterGUIType]
        except KeyError:
            raise SoftException('Unexpected booster type {}'.format(boosterGUIType))

    def _boosterComparisonKey(self, boosterId):
        booster = self._goodiesCache.getBooster(boosterId)
        return (booster.effectValue, booster.effectTime)

    def _buildConversionItemList(self, boosterIds, counts, conversionModelArray):
        conversionModelArray.clear()
        conversionModelArray.reserve(len(boosterIds))
        for boosterId, count in zip(boosterIds, counts):
            conversionItem = ConvertedBoosterListItem()
            conversionItem.setCount(count)
            descr = self._getBoosterDescr(boosterId)
            conversionItem.setDescription(descr)
            conversionModelArray.addViewModel(conversionItem)

    def _onClose(self):
        closeViewsExceptReservesActivationView()
