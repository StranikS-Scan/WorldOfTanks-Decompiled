# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_reserves/reserves_conversion_view.py
from frameworks.wulf import ViewFlags, ViewSettings, Array
from gui.goodies.goodie_items import Booster
from gui.goodies.pr2_conversion_result import getConversionDataProvider
from gui.impl import backport
from gui.impl.gen.view_models.views.lobby.personal_reserves.reserves_conversion_view_model import ReservesConversionViewModel
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.shared import IItemsCache
from gui.impl.gen.view_models.views.lobby.personal_reserves.converted_booster_model import ConvertedBoosterModel
from soft_exception import SoftException

class ReservesConversionView(ViewImpl):
    __slots__ = ('__goodiesCache', '__itemsCache')
    __goodiesCache = dependency.instance(IGoodiesCache)
    __itemsCache = dependency.instance(IItemsCache)

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_TOP_SUB_VIEW
        settings.model = ReservesConversionViewModel()
        super(ReservesConversionView, self).__init__(settings)

    @property
    def _viewModel(self):
        return super(ReservesConversionView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(ReservesConversionView, self)._initialize(args, kwargs)
        self._viewModel.onClose += self._onClose

    def _finalize(self):
        self._viewModel.onClose -= self._onClose
        super(ReservesConversionView, self)._finalize()

    def _getBoosterDescr(self, boosterID):
        booster = self.__goodiesCache.getBooster(boosterID)
        value = booster.getFormattedValue()
        effectiveTime = booster.getEffectTimeStr(hoursOnly=True)
        return backport.text(R.strings.personal_reserves.conversionView.boosterDescription(), value=value, effectTime=effectiveTime)

    def _onLoading(self, *args, **kwargs):
        super(ReservesConversionView, self)._onLoading(*args, **kwargs)
        self._fillViewModel()

    def _setBoosterModel(self, model, convertedData, boosterGUIType):
        if boosterGUIType == 'booster_crew_xp':
            model.setCrewXPConverted(convertedData)
        elif boosterGUIType == 'booster_credits':
            model.setCreditsConverted(convertedData)
        elif boosterGUIType == 'booster_free_xp':
            model.setFreeXPConverted(convertedData)
        elif boosterGUIType == 'booster_xp':
            model.setBattleXPConverted(convertedData)
        else:
            raise SoftException('Not expected booster type {}'.format(boosterGUIType))

    def _fillViewModel(self):
        devTest = False
        if devTest:
            result = ((5020, 3),
             (5026, 2),
             (5042, 4),
             (5049, 5),
             (5035, 11),
             (5036, 2),
             (9029, 4),
             (9030, 2),
             (5028, 3),
             (5034, 4))
        else:
            result = self.__itemsCache.items.goodies.pr2ConversionResult
        with self._viewModel.transaction() as model:
            provider = getConversionDataProvider(result)
            prConversionResult = provider.getResult()
            appliedNewIDs = set([])
            for bGuiType in ('booster_crew_xp', 'booster_free_xp'):
                resultByGUIType = prConversionResult.get(bGuiType)
                prConversionResultSum = provider.getResultSum()
                if resultByGUIType:
                    convertedData = Array()
                    for oldId, _, oldCount, newId, newCount in resultByGUIType:
                        boosterModel = ConvertedBoosterModel()
                        boosterModel.setOldCount(oldCount)
                        oldDescr = self._getBoosterDescr(oldId)
                        boosterModel.setOldDescription(oldDescr)
                        if newId not in appliedNewIDs:
                            appliedNewIDs.add(newId)
                            newCount = prConversionResultSum[newId]
                            newDescr = self._getBoosterDescr(newId)
                        else:
                            newCount = 0
                            newDescr = '----'
                        boosterModel.setNewCount(newCount)
                        boosterModel.setNewDescription(newDescr)
                        convertedData.addViewModel(boosterModel)

                    self._setBoosterModel(model, convertedData, bGuiType)
                    del prConversionResult[bGuiType]

            for boosterGUIType, converted in prConversionResult.iteritems():
                convertedData = Array()
                for oldId, _, oldCount, newId, newCount in converted:
                    boosterModel = ConvertedBoosterModel()
                    boosterModel.setOldCount(oldCount)
                    boosterModel.setNewCount(newCount)
                    oldDescr = self._getBoosterDescr(oldId)
                    newDescr = self._getBoosterDescr(newId)
                    boosterModel.setOldDescription(oldDescr)
                    boosterModel.setNewDescription(newDescr)
                    convertedData.addViewModel(boosterModel)

                self._setBoosterModel(model, convertedData, boosterGUIType)

    def _onClose(self):
        self.destroyWindow()
