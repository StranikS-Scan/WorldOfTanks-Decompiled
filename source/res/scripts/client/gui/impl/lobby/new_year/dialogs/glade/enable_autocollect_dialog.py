# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/dialogs/glade/enable_autocollect_dialog.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.dialogs.glade.enable_autocollect_dialog_model import EnableAutocollectDialogModel
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogBaseView
from gui.impl.pub.dialog_window import DialogButtons
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared.money import Currency
from helpers import dependency
from new_year.ny_resource_collecting_helper import isManualCollectingAvailable, getAutoCollectingResourcesPrice, getFirstCollectingCooldownTime
from skeletons.gui.shared import IItemsCache

class SetAutoCollectingDialogView(FullScreenDialogBaseView):
    __slots__ = ()
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.dialogs.glade.EnableAutocollectDialog())
        settings.args = args
        settings.kwargs = kwargs
        settings.model = EnableAutocollectDialogModel()
        super(SetAutoCollectingDialogView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(SetAutoCollectingDialogView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(SetAutoCollectingDialogView, self)._onLoading(args, kwargs)
        with self.viewModel.transaction() as model:
            model.setIsManualCollectAvailable(isManualCollectingAvailable())
            model.setPrice(getAutoCollectingResourcesPrice())
            model.setSecondCollectCooldown(getFirstCollectingCooldownTime())
            model.setDayStartTime(0)
            self.__updateBalance(model=model)

    def _getEvents(self):
        return ((self.viewModel.onAccept, self._onAccept), (self.viewModel.onCancel, self._onCancel), (self._itemsCache.onSyncCompleted, self.__onSyncCompleted))

    def _onAccept(self):
        self._setResult(DialogButtons.SUBMIT)

    def _onCancel(self):
        self._setResult(DialogButtons.CANCEL)

    def __onSyncCompleted(self, *_):
        self.__updateBalance()

    @replaceNoneKwargsModel
    def __updateBalance(self, model=None):
        model.setCredits(int(self._itemsCache.items.stats.money.getSignValue(Currency.CREDITS)))
