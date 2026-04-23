# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: open_bundle/scripts/client/open_bundle/gui/impl/lobby/main_view.py
from enum import Enum
from adisp import adisp_process
from functools import partial
from frameworks.wulf import ViewFlags, ViewSettings
from frameworks.wulf.gui_constants import ViewStatus
from gui.Scaleform.daapi.view.lobby.storage.storage_helpers import getVehicleCDForStyle
from gui.impl.gen import R
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared.event_dispatcher import selectVehicleInHangar, showHangar, showStylePreview, showVehicleHubOverview
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.money import Currency, Money
from gui.shop import showBuyGoldForBundle
from helpers import dependency, time_utils
from messenger.proto.events import g_messengerEvents
from open_bundle.gui.impl.gen.view_models.views.lobby.cell_model import CellModel
from open_bundle.gui.impl.gen.view_models.views.lobby.main_view_model import MainViewModel
from open_bundle.gui.impl.lobby.decorators import createTooltipContentDecorator
from open_bundle.gui.impl.lobby.sounds import OPEN_BUNDLE_SOUND_SPACE
from open_bundle.gui.impl.lobby.tooltips.fixed_rewards_tooltip import FixedRewardsTooltip
from open_bundle.gui.shared.event_dispatcher import showIntro, showAttachmentsPreview
from open_bundle.gui.shared.gui_items.processors.processors import ProcessNextStepProcessor
from open_bundle.helpers.account_settings import isIntroShown
from open_bundle.helpers.bonuses.bonus_packers import composeBonuses, hideInvisible, packBonusModelAndTooltipData, sortBonuses
from open_bundle.skeletons.open_bundle_controller import IOpenBundleController
from shared_utils import first
from skeletons.gui.game_control import IAchievements20EarningController, ISoundEventChecker
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared import IItemsCache

class _CellState(str, Enum):
    AVAILABLE = 'available'
    NEWLY_RECEIVED = 'newlyReceived'
    RECEIVED = 'received'


class MainView(ViewImpl):
    _COMMON_SOUND_SPACE = OPEN_BUNDLE_SOUND_SPACE
    __achievements = dependency.descriptor(IAchievements20EarningController)
    __customization = dependency.descriptor(ICustomizationService)
    __itemsCache = dependency.descriptor(IItemsCache)
    __openBundle = dependency.descriptor(IOpenBundleController)
    __soundEventChecker = dependency.descriptor(ISoundEventChecker)

    def __init__(self, layoutID=R.views.open_bundle.mono.lobby.main(), *args, **kwargs):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = MainViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(MainView, self).__init__(settings)
        self.__bundle = None
        self.__receivedCells = set()
        self.__newlyReceivedCells = set()
        self.__tooltipItems = {}
        return

    @property
    def viewModel(self):
        return super(MainView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(MainView, self).createToolTip(event)

    @createTooltipContentDecorator()
    def createToolTipContent(self, event, contentID):
        return FixedRewardsTooltip(self.__bundle) if contentID == R.views.open_bundle.mono.lobby.tooltips.fixed_rewards() else super(MainView, self).createToolTipContent(event, contentID)

    def getTooltipData(self, event):
        return self.__tooltipItems.get(event.getArgument('tooltipId', 0))

    def _onLoading(self, bundleID):
        super(MainView, self)._onLoading()
        self.__bundle = self.__openBundle.config.getBundle(bundleID)
        self.__receivedCells = set(self.__openBundle.getReceivedCells(bundleID))
        self.__updateModel()

    def _onLoaded(self, *args, **kwargs):
        if not isIntroShown(self.__bundle.id):
            showIntro(self.__bundle.id)

    def _finalize(self):
        self.__unlockSpoilers()
        self.__achievements.resume()
        super(MainView, self)._finalize()

    def _getEvents(self):
        return ((self.__openBundle.onStatusChanged, self.__onSettingsChanged),
         (self.__openBundle.onSettingsChanged, self.__onSettingsChanged),
         (self.viewModel.play, self.__processNextStep),
         (self.viewModel.onItemShown, self.__onItemShown),
         (self.viewModel.showPreview, self.__showPreview),
         (self.viewModel.resetInterruption, self.__setInterruption))

    def _getCallbacks(self):
        return (('stats.{}'.format(c), self.__fillPrice) for c in Currency.ALL)

    def __onSettingsChanged(self, *_):
        if self.__openBundle.isBundleActive(self.__bundle.id):
            self.__updateModel()
        else:
            showHangar()

    @replaceNoneKwargsModel
    def __updateModel(self, model=None):
        self.__fillMainInfo(model=model)
        self.__fillCells(model=model)

    def __fillMainInfo(self, model):
        model.setBundleType(self.__bundle.type)
        model.setStartTime(round(time_utils.makeLocalServerTime(self.__bundle.start), -1))
        model.setFinishTime(round(time_utils.makeLocalServerTime(self.__bundle.finish), -1))
        self.__fillPrice(model=model)
        self.__fillFixedReward(model=model)

    @replaceNoneKwargsModel
    def __fillPrice(self, value=None, model=None):
        step = self.__getCurrentStep()
        if step is None:
            return
        else:
            currency, value = first(step.price.items())
            model.stepPrice.setName(currency)
            model.stepPrice.setValue(value)
            model.stepPrice.setIsEnough(self.__isEnoughMoney({currency: value}))
            return

    @replaceNoneKwargsModel
    def __fillCells(self, model=None):
        cells = model.getCells()
        cells.clear()
        for cell in self.__bundle.cells.itervalues():
            cellModel = CellModel()
            cellName = cell.name
            cellModel.setName(cellName)
            cellModel.setTemplate(cell.template)
            cellModel.setIsRare(self.__openBundle.isRareCell(self.__bundle.id, cellName))
            cellModel.setState(self.__getCellState(cellName))
            self.__fillCellBonusInfo(cellModel, cellName)
            self.__fillCellCoordinates(cellModel, cell)
            cells.addViewModel(cellModel)

        cells.invalidate()

    def __fillCellCoordinates(self, cellModel, cell):
        coordinates = cell.coordinates
        startX, startY = coordinates.start
        cellModel.coordinates.start.setX(startX)
        cellModel.coordinates.start.setY(startY)
        endX, endY = coordinates.end
        cellModel.coordinates.end.setX(endX)
        cellModel.coordinates.end.setY(endY)

    def __fillCellBonusInfo(self, cellModel, cellName):
        cellBonusInfo = self.__openBundle.getCellBonusInfo(self.__bundle.id, cellName) or {}
        defaultProbability = cellBonusInfo['probability']
        cellModel.setProbability(self.__calculateProbability(cellName, defaultProbability))
        self.__fillBonuses(cellModel, cellBonusInfo)

    def __fillBonuses(self, cellModel, cellBonusInfo):
        bonuses = hideInvisible(sortBonuses(cellBonusInfo['bonuses']))
        bonusModels = cellModel.getBonuses()
        bonusModels.clear()
        packBonusModelAndTooltipData(bonuses, bonusModels, self.__tooltipItems, showAttachmentSet=True)
        cellModel.setBonuses(bonusModels)

    @replaceNoneKwargsModel
    def __fillFixedReward(self, model=None):
        step = self.__getCurrentStep()
        if step is None:
            return
        else:
            bonuses = composeBonuses([step.fixedBonus])
            bonusModels = model.getFixedReward()
            bonusModels.clear()
            packBonusModelAndTooltipData(bonuses, bonusModels, self.__tooltipItems)
            return

    def __calculateProbability(self, cellName, defaultProbability):
        if cellName in self.__receivedCells or cellName in self.__newlyReceivedCells:
            return -1
        receivedProbabilitiesSum = sum(((self.__openBundle.getCellBonusInfo(self.__bundle.id, cell) or {})['probability'] for cell in self.__receivedCells.union(self.__newlyReceivedCells)))
        if receivedProbabilitiesSum == 1:
            return -1
        probability = defaultProbability / (1 - receivedProbabilitiesSum)
        return int(probability * 10000 + 1e-06) / 100.0

    @adisp_process
    def __processNextStep(self):
        step = self.__getCurrentStep()
        if step is None:
            return
        else:
            currency, value = first(step.price.items())
            if currency == Currency.GOLD and not self.__isEnoughMoney({currency: value}):
                showBuyGoldForBundle(value, {})
                return
            self.__lockSpoilerMessages()
            self.__soundEventChecker.lockPlayingSounds()
            processor = ProcessNextStepProcessor(bundleID=self.__bundle.id, stepNumber=self.__getNextStepNumber())
            result = yield processor.request()
            if self.viewStatus not in (ViewStatus.DESTROYING, ViewStatus.DESTROYED):
                if result.success:
                    self.__newlyReceivedCells.add(result.auxData.get('receivedCell'))
                    self.__updateModel()
                    return
                self.__setInterruption(True)
                self.__unlockSpoilers()
                self.__achievements.resume()
            return

    def __unlockSpoilers(self):
        self.__unlockMessages()
        self.__soundEventChecker.unlockPlayingSounds()

    def __getNextStepNumber(self):
        return len(self.__receivedCells.union(self.__newlyReceivedCells)) + 1

    def __getCurrentStep(self):
        return self.__bundle.steps.get(self.__getNextStepNumber())

    @args2params(str)
    def __onItemShown(self, cellName):
        self.__unlockSpoilers()
        self.__achievements.resume()
        self.__receivedCells.add(cellName)
        if cellName in self.__newlyReceivedCells:
            self.__newlyReceivedCells.remove(cellName)
        self.__fillCells()

    @args2params(str, int, int, str)
    def __showPreview(self, bonusType, bonusId, styleID, attachmentsToken):
        if bonusType == 'vehicles':
            vehicle = self.__itemsCache.items.getItemByCD(bonusId)
            if vehicle.isInInventory:
                self.__selectVehicle(bonusId)
            else:
                style = self.__customization.getItemByID(GUI_ITEM_TYPE.STYLE, styleID) if styleID else None
                showVehicleHubOverview(bonusId, style=style)
        elif bonusType == 'customizations':
            style = self.__customization.getItemByID(GUI_ITEM_TYPE.STYLE, bonusId)
            vehicleCD = getVehicleCDForStyle(style)
            showStylePreview(vehicleCD, style)
        elif bonusType == 'attachmentsSet':
            showAttachmentsPreview(self.__bundle.id, attachmentsToken)
        return

    def __selectVehicle(self, vehicleCD):
        if self.__openBundle.isRandomPrb():
            selectVehicleInHangar(vehicleCD, loadHangar=True)
        else:
            self.__openBundle.selectRandomBattle(partial(selectVehicleInHangar, vehicleCD, loadHangar=False))

    def __getCellState(self, cellName):
        if cellName in self.__receivedCells:
            return _CellState.RECEIVED.value
        return _CellState.NEWLY_RECEIVED.value if cellName in self.__newlyReceivedCells else _CellState.AVAILABLE.value

    def __setInterruption(self, isInterruption=False):
        self.viewModel.setIsInterrupted(isInterruption)

    def __isEnoughMoney(self, stepPrice):
        price = Money(**stepPrice)
        return not self.__itemsCache.items.stats.money.getShortage(price).isDefined()

    def __makeNotificationLockKey(self):
        return '_'.join(('OpenBundleMainView', str(self.uniqueID)))

    def __lockSpoilerMessages(self):
        g_messengerEvents.onLockPopUpMessages(self.__makeNotificationLockKey(), lockHigh=True, useQueue=True)

    def __unlockMessages(self):
        g_messengerEvents.onUnlockPopUpMessages(self.__makeNotificationLockKey())
