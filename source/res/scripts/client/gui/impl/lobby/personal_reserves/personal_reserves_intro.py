# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_reserves/personal_reserves_intro.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.framework.entities.View import ViewKeyDynamic
from gui.Scaleform.framework.managers.view_lifecycle_watcher import ViewLifecycleWatcher, IViewLifecycleHandler
from gui.app_loader.loader import AppLoader
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.personal_reserves.reserves_intro_view_model import ReservesIntroViewModel
from gui.impl.pub import ViewImpl
from gui.shared.event_dispatcher import showPersonalReservesConversion
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.impl import IGuiLoader
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import gui

class _ConversionListener(IViewLifecycleHandler):

    def __init__(self):
        super(_ConversionListener, self).__init__((ViewKeyDynamic(R.views.lobby.personal_reserves.ReservesConversionView()),))

    def onViewDestroyed(self, view):
        uiLoader = dependency.instance(IGuiLoader)
        introView = uiLoader.windowsManager.getViewByLayoutID(R.views.lobby.personal_reserves.ReservesIntroView())
        introView.close()


class PersonalReservesIntro(ViewImpl):
    __slots__ = ('__callbackOnClose', '__viewLifecycleWatcher')
    __appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, layoutID, ctx=None):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_TOP_SUB_VIEW
        settings.model = ReservesIntroViewModel()
        self.__callbackOnClose = ctx['callbackOnClose']
        super(PersonalReservesIntro, self).__init__(settings)
        self.__viewLifecycleWatcher = None
        return

    @property
    def viewModel(self):
        return super(PersonalReservesIntro, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(PersonalReservesIntro, self)._initialize()
        self.viewModel.onClose += self.close
        self.viewModel.onConversionInfoClicked += self.onConversionInfoClicked
        self.__viewLifecycleWatcher = ViewLifecycleWatcher()
        self.__viewLifecycleWatcher.start(self.__appLoader.getApp().containerManager, [_ConversionListener()])

    def _onLoaded(self, *args, **kwargs):
        super(PersonalReservesIntro, self)._onLoaded(*args, **kwargs)
        self.soundManager.setState('STATE_hangar_place', 'STATE_hangar_place_personal_reserves')

    def _finalize(self):
        super(PersonalReservesIntro, self)._finalize()
        self.viewModel.onClose -= self.close
        self.viewModel.onConversionInfoClicked -= self.onConversionInfoClicked
        self.__viewLifecycleWatcher.stop()
        self.__viewLifecycleWatcher = None
        return

    def onConversionInfoClicked(self):
        showPersonalReservesConversion()

    def close(self):
        if self.__callbackOnClose and callable(self.__callbackOnClose):
            self.__callbackOnClose()
        self.destroy()
