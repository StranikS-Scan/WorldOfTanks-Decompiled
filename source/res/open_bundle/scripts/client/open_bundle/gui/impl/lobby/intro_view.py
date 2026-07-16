# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: open_bundle/scripts/client/open_bundle/gui/impl/lobby/intro_view.py
from __future__ import absolute_import
from frameworks.wulf import ViewSettings, WindowLayer, WindowFlags
from gui.shared import g_eventBus, events
from open_bundle.helpers.account_settings import setIntroShown
from open_bundle.gui.impl.gen.view_models.views.lobby.intro_view_model import IntroViewModel
from open_bundle.skeletons.open_bundle_controller import IOpenBundleController
from gui.impl.gen import R
from gui.impl.pub import ViewImpl, WindowImpl
from helpers import dependency

class Intro(ViewImpl):
    __openBundle = dependency.descriptor(IOpenBundleController)

    def __init__(self, layoutID, model, bundleID):
        settings = ViewSettings(layoutID)
        settings.model = model()
        self.__bundleID = bundleID
        super(Intro, self).__init__(settings)

    @property
    def viewModel(self):
        return super(Intro, self).getViewModel()

    @property
    def _bundle(self):
        return self.__openBundle.config.getBundle(self.__bundleID)

    def _onLoading(self, *arg, **kwargs):
        super(Intro, self)._onLoading()
        with self.getViewModel().transaction() as model:
            model.setBundleType(self._bundle.type)
            model.setTimeLeft(self.__openBundle.getBundleTimeLeft(self.__bundleID))
        setIntroShown(self.__bundleID)

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose), (self.viewModel.onExternalLink, self.__onExternalLink))

    def __onClose(self):
        self.destroyWindow()

    def __onExternalLink(self):
        g_eventBus.handleEvent(events.OpenLinkEvent(events.OpenLinkEvent.OPEN_BUNDLE_STEPS))


class IntroWindow(WindowImpl):

    def __init__(self, bundleID):
        super(IntroWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, layer=WindowLayer.TOP_WINDOW, content=Intro(layoutID=R.views.open_bundle.mono.lobby.intro(), model=IntroViewModel, bundleID=bundleID))
