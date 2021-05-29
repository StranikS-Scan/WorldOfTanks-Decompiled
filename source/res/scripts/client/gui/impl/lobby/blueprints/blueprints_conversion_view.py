# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/blueprints/blueprints_conversion_view.py
from collections import defaultdict
import nations
from blueprints.BlueprintTypes import BlueprintTypes
from frameworks.wulf import ViewSettings, Array
from gui import SystemMessages
from gui.SystemMessages import SM_TYPE
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.impl.backport import BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.blueprints.blueprint_balance_content_model import BlueprintBalanceContentModel
from gui.impl.gen.view_models.views.lobby.blueprints.blueprint_convert_model import BlueprintConvertModel
from gui.impl.gen.view_models.views.lobby.blueprints.blueprint_price import BlueprintPrice
from gui.impl.gen.view_models.views.lobby.blueprints.blueprint_screen_tooltips import BlueprintScreenTooltips
from gui.impl.gen.view_models.views.lobby.blueprints.fragment_item_model import FragmentItemModel
from gui.impl.lobby.blueprints import getBlueprintTooltipData
from gui.impl.lobby.blueprints.blueprints_alliance_tooltip_view import BlueprintsAllianceTooltipView
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogView
from gui.shared import event_dispatcher, sound_helpers
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.shared.utils.requesters.blueprints_requester import getNationalFragmentCD

class BlueprintsConversionView(FullScreenDialogView):

    def __init__(self, vehicleCD, fragmentsCount):
        settings = ViewSettings(layoutID=R.views.lobby.blueprints.Confirm(), model=BlueprintConvertModel())
        super(BlueprintsConversionView, self).__init__(settings)
        self.__vehicle = self._itemsCache.items.getItemByCD(vehicleCD)
        self.__fragmentsCount = fragmentsCount
        self.__allyFragmentsBalance = self.__blueprints.getNationalAllianceFragments(self.__vehicle.intCD, self.__vehicle.level)

    @property
    def viewModel(self):
        return self.getViewModel()

    def createToolTipContent(self, event, contentID):
        return BlueprintsAllianceTooltipView(self.__vehicle.nationName, self.__vehicle.intCD, self.__vehicle.level) if contentID == R.views.lobby.blueprints.tooltips.BlueprintsAlliancesTooltipView() else super(BlueprintsConversionView, self).createToolTipContent(event=event, contentID=contentID)

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            itemCD = event.getArgument('itemCD')
            tooltipData = getBlueprintTooltipData(tooltipId, itemCD)
            if tooltipData is None:
                return
            window = BackportTooltipWindow(tooltipData, self.getParentWindow())
            if window is not None:
                window.load()
            return window
        else:
            return super(BlueprintsConversionView, self).createToolTip(event)

    def _initialize(self):
        super(BlueprintsConversionView, self)._initialize()
        self.viewModel.onSelectItem += self.__onSelectItem
        self.viewModel.onSliderShift += self.__onSliderShift
        g_clientUpdateManager.addCallbacks({'serverSettings.blueprints_config.levels': self.__onBlueprintsSettingsChanged,
         'serverSettings.blueprints_config.isEnabled': self.__onBlueprintsModeChanged,
         'serverSettings.blueprints_config.useBlueprintsForUnlock': self.__onBlueprintsModeChanged,
         'blueprints': self.__onBlueprintsBalanceChanged})

    def _onLoading(self, *args, **kwargs):
        with self.viewModel.transaction() as model:
            if self.__fragmentsCount > 1:
                model.setTitleBody(R.strings.menu.blueprints.conversionView.multiConversion.title())
            else:
                model.setTitleBody(R.strings.menu.blueprints.conversionView.title())
            self._setTitleArgs(model.getTitleArgs(), (('vehName', self.__vehicle.shortUserName.replace(' ', '&nbsp;')),))
            model.setTotalCount(self.__fragmentsCount)
            model.setCount(self.__fragmentsCount)
            allianceName = nations.ALLIANCES_TAGS_ORDER[nations.NATION_TO_ALLIANCE_IDS_MAP[nations.INDICES[self.__vehicle.nationName]]]
            model.setAllianceName(allianceName.replace('-', '_'))
            self.__setUsedFragmentsPrice(model.usedMainPrice, model.getUsedAdditionalPrice())
            self.__setNationalPriceOptions(model.getAdditionalPriceOptions())
            self.__setBalanceBlock(model.fragmentsBalance)
            self.__triggerSyncInitiator(model)
            model.setAcceptButtonText(R.strings.menu.blueprints.conversionView.btnConvert())
            model.setCancelButtonText(R.strings.menu.blueprints.conversionView.btnCancel())

    def _finalize(self):
        self.viewModel.onSelectItem -= self.__onSelectItem
        self.viewModel.onSliderShift -= self.__onSliderShift
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(BlueprintsConversionView, self)._finalize()

    def __onSelectItem(self, args=None):
        selectedItemIdx = int(args.get('selectedItem'))
        with self.viewModel.transaction() as model:
            options = model.getAdditionalPriceOptions()
            usedPrices = model.getUsedAdditionalPrice()
            for idx, usedPrice in enumerate(usedPrices):
                usedPrice.setValue(options[idx].getValue() if idx == selectedItemIdx else 0)

            usedPrices.invalidate()
            self.__triggerSyncInitiator(model)

    def __onSliderShift(self, args=None):
        index = int(args.get('index'))
        newCount = int(args.get('newCount'))
        with self.viewModel.transaction() as model:
            nId = nations.INDICES[model.getAdditionalPriceOptions()[index].getNationName()]
            sliderStep = model.getAdditionalPriceOptions()[index].getValue()
            oldCount = model.getUsedAdditionalPrice()[index].getValue()
            newFragmentsCount = model.getCount() + (newCount - oldCount) / sliderStep
            model.setCount(newFragmentsCount)
            _, intelligenceCost = self.__blueprints.getRequiredIntelligenceAndNational(self.__vehicle.level)
            model.usedMainPrice.setValue(int(newFragmentsCount * intelligenceCost))
            usedAdditionalPriceModel = model.getUsedAdditionalPrice()
            usedAdditionalPriceModel[index].setValue(int(newCount))
            usedAdditionalPriceModel[index].setNotEnough(newCount > self.__allyFragmentsBalance[nId])
            usedAdditionalPriceModel.invalidate()
            sound_helpers.playSliderUpdateSound(oldCount, newCount, sliderStep * self.__fragmentsCount)

    def _getAdditionalData(self):
        additionalPriceModel = self.viewModel.getUsedAdditionalPrice()
        usedNationalFragments = {}
        for price in additionalPriceModel:
            nationId = nations.INDICES[price.getNationName()]
            value = price.getValue()
            if value > 0:
                usedNationalFragments[nationId] = value

        return (usedNationalFragments, self.viewModel.getCount())

    def __setUsedFragmentsPrice(self, mainPriceModel, usedAdditionalPrice):
        _, intelligenceValue = self.__blueprints.getRequiredIntelligenceAndNational(self.__vehicle.level)
        mainPriceModel.setValue(int(self.__fragmentsCount * intelligenceValue))
        mainPriceModel.setIcon(R.images.gui.maps.icons.blueprints.fragment.special.intelligence())
        mainPriceModel.setTooltipId(BlueprintScreenTooltips.TOOLTIP_BLUEPRINT)
        mainPriceModel.setItemCD(BlueprintTypes.INTELLIGENCE_DATA)
        nationUsedDict = self.__getInitialNationalUsageCounts()
        usedAdditionalPrice.clear()
        for nId in self.__allyFragmentsBalance:
            nationName = nations.MAP[nId]
            price = BlueprintPrice()
            price.setNationName(nationName)
            price.setValue(int(nationUsedDict[nId]))
            price.setIcon(R.images.gui.maps.icons.blueprints.fragment.special.dyn(nationName)())
            price.setIconBig(R.images.gui.maps.icons.blueprints.fragment.c_102x102.dyn(nationName)())
            price.setTooltipId(BlueprintScreenTooltips.TOOLTIP_BLUEPRINT)
            price.setItemCD(getNationalFragmentCD(nId))
            usedAdditionalPrice.addViewModel(price)

        usedAdditionalPrice.invalidate()

    def __setNationalPriceOptions(self, optionsArray):
        optionsArray.clear()
        options = self.__blueprints.getNationalRequiredOptions(self.__vehicle.intCD, self.__vehicle.level)
        for nId, cost in options.iteritems():
            nationName = nations.MAP[nId]
            price = BlueprintPrice()
            price.setNationName(nationName)
            price.setValue(int(cost))
            price.setIcon(R.images.gui.maps.icons.blueprints.fragment.special.dyn(nationName)())
            price.setIconBig(R.images.gui.maps.icons.blueprints.fragment.c_102x102.dyn(nationName)())
            price.setNotEnough(self.__allyFragmentsBalance[nId] < cost)
            optionsArray.addViewModel(price)

        optionsArray.invalidate()

    def __setBalanceBlock(self, fragmentsBalance):
        nationName = self.__vehicle.nationName if self.__vehicle is not None else ''
        nationId = nations.INDICES[nationName]
        allianceId = nations.NATION_TO_ALLIANCE_IDS_MAP[nationId]
        fragmentsBalance.setAllianceName(nations.ALLIANCES_TAGS_ORDER[allianceId])
        fragmentCount = self.__blueprints.getIntelligenceCount()
        item = fragmentsBalance.intelligenceBalance
        item.setValue(self.gui.systemLocale.getNumberFormat(fragmentCount))
        item.setIcon(R.images.gui.maps.icons.blueprints.fragment.special.intelligence())
        item.setFragmentCD(BlueprintTypes.INTELLIGENCE_DATA)
        fragmentsBalance.currency.clearItems()
        for nId, fragmentCount in self.__allyFragmentsBalance.iteritems():
            item = FragmentItemModel()
            item.setValue(self.gui.systemLocale.getNumberFormat(fragmentCount))
            nationName = nations.MAP[nId]
            item.setIcon(R.images.gui.maps.icons.blueprints.fragment.special.dyn(nationName)())
            item.setFragmentCD(getNationalFragmentCD(nId))
            fragmentsBalance.currency.addViewModel(item)

        fragmentsBalance.currency.invalidate()
        return

    def __updateBallanceBlock(self, fragmentsBallance):
        with fragmentsBallance.transaction() as model:
            fragmentCount = self.__blueprints.getIntelligenceCount()
            item = fragmentsBallance.intelligenceBalance
            item.setValue(self.gui.systemLocale.getNumberFormat(fragmentCount))
            for index, fragmentCount in enumerate(self.__allyFragmentsBalance.itervalues()):
                item = model.currency.getItem(index)
                item.setValue(self.gui.systemLocale.getNumberFormat(fragmentCount))

            model.currency.invalidate()

    def __updateNotEnoughFields(self, priceOptions, usedPrices):
        for price in priceOptions:
            nId = nations.INDICES[price.getNationName()]
            price.setNotEnough(price.getValue() > self.__allyFragmentsBalance[nId])

        for price in usedPrices:
            nId = nations.INDICES[price.getNationName()]
            price.setNotEnough(price.getValue() > self.__allyFragmentsBalance[nId])

    def __onBlueprintsSettingsChanged(self, _):
        if self.__blueprints.canConvertToVehicleFragment(self.__vehicle.intCD, self.__vehicle.level):
            self.__updateBlocks()
        else:
            SystemMessages.pushI18nMessage(SYSTEM_MESSAGES.BLUEPRINTS_CONVERSION_DISABLE, type=SM_TYPE.Error)
            self.destroy()

    def __onBlueprintsModeChanged(self, _):
        if not self.__blueprints.isBlueprintsAvailable():
            event_dispatcher.showHangar()
            self.destroy()

    def __onBlueprintsBalanceChanged(self, *_):
        self.__allyFragmentsBalance = self.__blueprints.getNationalAllianceFragments(self.__vehicle.intCD, self.__vehicle.level)
        with self.viewModel.transaction() as model:
            self.__updateBallanceBlock(model.fragmentsBalance)
            self.__updateNotEnoughFields(model.getAdditionalPriceOptions(), model.getUsedAdditionalPrice())
            self.__triggerSyncInitiator(model)

    def __updateBlocks(self):
        with self.viewModel.transaction() as model:
            self.__setUsedFragmentsPrice(model.usedMainPrice, model.getUsedAdditionalPrice())
            self.__setNationalPriceOptions(model.getAdditionalPriceOptions())
            self.__setBalanceBlock(model.fragmentsBalance)
            self.__triggerSyncInitiator(model)

    def __triggerSyncInitiator(self, model):
        model.setSyncInitiator((model.getSyncInitiator() + 1) % 1000)

    @property
    def __blueprints(self):
        return self._itemsCache.items.blueprints

    def __getInitialNationalUsageCounts(self):
        options = self.__blueprints.getNationalRequiredOptions(self.__vehicle.intCD, self.__vehicle.level)
        if self.__fragmentsCount == 1:
            priorityOrder = sorted(self.__allyFragmentsBalance.items(), key=lambda (nId, balance): (nId != nations.INDICES[self.__vehicle.nationName], nId))
        else:
            priorityOrder = sorted(self.__allyFragmentsBalance.items(), key=lambda (nId, balance): (nId != nations.INDICES[self.__vehicle.nationName], -balance, nId))
        totalCount = 0
        nationUsedDict = defaultdict(lambda : 0)
        for nId, balance in priorityOrder:
            toFill = self.__fragmentsCount - totalCount
            canCraftFragments = min(int(balance / options[nId]) if options[nId] else 0, toFill)
            nationUsedDict[nId] = int(canCraftFragments * options[nId])
            totalCount += canCraftFragments
            if totalCount == self.__fragmentsCount:
                break

        return nationUsedDict
