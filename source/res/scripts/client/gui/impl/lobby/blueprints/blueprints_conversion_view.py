# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/blueprints/blueprints_conversion_view.py
import BigWorld
from gui import SystemMessages
from gui.SystemMessages import SM_TYPE
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.impl.gen import R
from gui.impl.gen.view_models.constants.dialog_presets import DialogPresets
from gui.impl.gen.view_models.windows.simple_dialog_window_model import SimpleDialogWindowModel
from gui.impl.wrappers.user_format_string_arg_model import UserFormatStringArgModel as FmtArg
from gui.impl.lobby.blueprints.fragments_balance_content import FragmentsBalanceContent
from gui.impl.lobby.dialogs.contents.prices_content import DialogPricesContent
from gui.impl.pub.dialog_window import DialogContent, DialogButtons, DialogWindow
from gui.shared import event_dispatcher
from gui.ClientUpdateManager import g_clientUpdateManager
from helpers import dependency
from skeletons.gui.shared import IItemsCache
_ONE_PERCENT = 0.01
_MIN_COUNT_FRAGMENTS = 1

class BlueprintsConversionView(DialogWindow):
    __itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('__vehicle', '__countFragments')

    def __init__(self, vehicleCD, countFragments, parent):
        content = DialogContent(R.views.common.dialog_view.simple_dialog_content.SimpleDialogContent(), SimpleDialogWindowModel) if countFragments > _MIN_COUNT_FRAGMENTS else None
        super(BlueprintsConversionView, self).__init__(content=content, bottomContent=DialogPricesContent(), parent=parent, balanceContent=FragmentsBalanceContent(vehicleCD), enableBlur=True)
        self.__vehicle = self.__itemsCache.items.getItemByCD(vehicleCD)
        self.__countFragments = countFragments
        return

    def _initialize(self):
        super(BlueprintsConversionView, self)._initialize()
        g_clientUpdateManager.addCallbacks({'serverSettings.blueprints_config.levels': self.__onBlueprintsSettingsChanged,
         'serverSettings.blueprints_config.isEnabled': self.__onBlueprintsModeChanged,
         'serverSettings.blueprints_config.useBlueprintsForUnlock': self.__onBlueprintsModeChanged})
        with self.viewModel.transaction() as model:
            if self.__countFragments > _MIN_COUNT_FRAGMENTS:
                model.setTitle(R.strings.menu.blueprints.conversionView.multiConversion.title())
                self.contentViewModel.setMessage(R.strings.menu.blueprints.conversionView.multiConversion.description())
                messageArgs = self.contentViewModel.getMessageFmtArgs()
                messageArgs.addViewModel(FmtArg(str(self.__countFragments), 'fragCount'))
                messageArgs.invalidate()
            else:
                model.setTitle(R.strings.menu.blueprints.conversionView.title())
            titleArgs = model.getTitleFmtArgs()
            titleArgs.addViewModel(FmtArg(self.__vehicle.shortUserName, 'vehName'))
            titleArgs.invalidate()
            self.__createUniversalFragmentsBlock(self.__countFragments)
            self._setPreset(DialogPresets.BLUEPRINTS_CONVERSION)
            self._addButton(DialogButtons.RESEARCH, R.strings.menu.blueprints.conversionView.btnConvert(), isFocused=True)
            self._addButton(DialogButtons.CANCEL, R.strings.menu.blueprints.conversionView.btnCancel(), invalidateAll=True)

    def _finalize(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(BlueprintsConversionView, self)._finalize()

    def __onBlueprintsSettingsChanged(self, _):
        if self.__itemsCache.items.blueprints.canConvertToVehicleFragment(self.__vehicle.intCD, self.__vehicle.level):
            self.__updateUniversalFragmentsBlock()
        else:
            SystemMessages.pushI18nMessage(SYSTEM_MESSAGES.BLUEPRINTS_CONVERSION_DISABLE, type=SM_TYPE.Error)
            self.destroy()

    def __onBlueprintsModeChanged(self, _):
        if not self.__itemsCache.items.blueprints.isBlueprintsAvailable():
            event_dispatcher.showHangar()
            self.destroy()

    def __createUniversalFragmentsBlock(self, countFragments):
        nationValue, intelligenceValue = self.__itemsCache.items.blueprints.getRequiredIntelligenceAndNational(self.__vehicle.level)
        with self.bottomContentViewModel.transaction() as model:
            model.setValueMainCost(BigWorld.wg_getIntegralFormat(countFragments * intelligenceValue))
            model.setIconMainCost(R.images.gui.maps.icons.blueprints.fragment.small.intelligence())
            model.setValueAdditionalCost(BigWorld.wg_getIntegralFormat(countFragments * nationValue))
            model.setIconAdditionalCost(R.images.gui.maps.icons.blueprints.fragment.small.dyn(self.__vehicle.nationName)())

    def __updateUniversalFragmentsBlock(self):
        nationValue, intelligenceValue = self.__itemsCache.items.blueprints.getRequiredIntelligenceAndNational(self.__vehicle.level)
        with self.bottomContentViewModel.transaction() as model:
            model.setValueMainCost(BigWorld.wg_getIntegralFormat(nationValue))
            model.setValueAdditionalCost(BigWorld.wg_getIntegralFormat(intelligenceValue))
