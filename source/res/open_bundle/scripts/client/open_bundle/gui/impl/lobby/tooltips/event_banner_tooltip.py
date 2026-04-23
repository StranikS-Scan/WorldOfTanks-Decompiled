# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: open_bundle/scripts/client/open_bundle/gui/impl/lobby/tooltips/event_banner_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import dependency
from open_bundle.gui.impl.gen.view_models.views.lobby.tooltips.event_banner_tooltip_model import EventBannerTooltipModel
from open_bundle.skeletons.open_bundle_controller import IOpenBundleController

class EventBannerTooltip(ViewImpl):
    __openBundle = dependency.descriptor(IOpenBundleController)

    def __init__(self, bundleID):
        settings = ViewSettings(R.views.open_bundle.mono.lobby.tooltips.event_banner())
        settings.model = EventBannerTooltipModel()
        super(EventBannerTooltip, self).__init__(settings)
        self.__bundleID = bundleID

    @property
    def viewModel(self):
        return super(EventBannerTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(EventBannerTooltip, self)._onLoading(*args, **kwargs)
        bundle = self.__openBundle.config.getBundle(self.__bundleID)
        with self.getViewModel().transaction() as model:
            model.setBundleType(bundle.type)
            model.setTimeLeft(self.__openBundle.getBundleTimeLeft(self.__bundleID))
