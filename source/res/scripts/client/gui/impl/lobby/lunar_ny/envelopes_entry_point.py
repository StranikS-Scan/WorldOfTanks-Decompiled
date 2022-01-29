# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/lunar_ny/envelopes_entry_point.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import LUNAR_NY_ENTITLEMENTS_VIEWED
from frameworks.wulf import ViewSettings
from frameworks.wulf.gui_constants import ViewFlags
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.lunar_ny.envelopes_entry_point_model import EnvelopesEntryPointModel
from gui.impl.lobby.lunar_ny.popovers.entry_point_popover import EnvelopesPopover
from gui.impl.lobby.lunar_ny.tooltips.envelopes_entry_tooltip import EnvelopesEntryTooltip
from gui.impl.pub import ViewImpl
from helpers import dependency
from lunar_ny import ILunarNYController

class EnvelopesEntrancePointInjectWidget(InjectComponentAdaptor):

    def _makeInjectView(self):
        return EnvelopesEntrancePointWidget()


class EnvelopesEntrancePointWidget(ViewImpl):
    __lunarNYController = dependency.descriptor(ILunarNYController)
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(R.views.lobby.lunar_ny.envelopes.EnvelopesEntryView())
        settings.flags = ViewFlags.COMPONENT
        settings.model = EnvelopesEntryPointModel()
        super(EnvelopesEntrancePointWidget, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(EnvelopesEntrancePointWidget, self)._onLoading()
        self.__lunarNYController.giftSystem.onEnvelopesEntitlementUpdated += self.__onEnvelopesEntitlementUpdated
        self.__update()

    def _finalize(self):
        self.__lunarNYController.giftSystem.onEnvelopesEntitlementUpdated -= self.__onEnvelopesEntitlementUpdated
        super(EnvelopesEntrancePointWidget, self)._finalize()

    def createPopOverContent(self, _):
        notSendedEnvelopesCount = self.__lunarNYController.giftSystem.getEnvelopesEntitlementCount()
        AccountSettings.setSettings(LUNAR_NY_ENTITLEMENTS_VIEWED, notSendedEnvelopesCount)
        self.viewModel.setHasNew(False)
        return EnvelopesPopover()

    def createToolTipContent(self, _, __):
        return EnvelopesEntryTooltip()

    def __update(self):
        countNotSendedEnvelopes = self.__lunarNYController.giftSystem.getEnvelopesEntitlementCount()
        countViewedEntitlements = AccountSettings.getSettings(LUNAR_NY_ENTITLEMENTS_VIEWED)
        with self.viewModel.transaction() as model:
            model.setEnvelopesCount(countNotSendedEnvelopes)
            model.setHasNew(countNotSendedEnvelopes > countViewedEntitlements)

    def __onEnvelopesEntitlementUpdated(self):
        self.__update()
