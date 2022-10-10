# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_reserves/personal_reserves_intro.py
from typing import Dict, Any
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.personal_reserves.reserves_intro_view_model import ReservesIntroViewModel
from gui.impl.lobby.personal_reserves.view_utils.reserves_view_monitor import ReservesViewMonitor
from gui.shared.event_dispatcher import showPersonalReservesConversion, closeReservesIntroAndConversionView
from helpers import dependency
from skeletons.gui.impl import IGuiLoader

class PersonalReservesIntro(ReservesViewMonitor):
    __slots__ = ('__callbackOnClose',)
    _uiLoader = dependency.descriptor(IGuiLoader)

    def __init__(self, layoutID, ctx=None):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_TOP_SUB_VIEW
        settings.model = ReservesIntroViewModel()
        self.__callbackOnClose = ctx['callbackOnClose']
        super(PersonalReservesIntro, self).__init__(settings)

    @property
    def viewModel(self):
        return super(PersonalReservesIntro, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(PersonalReservesIntro, self)._initialize()
        self.viewModel.onClose += self.close
        self.viewModel.onConversionInfoClicked += self.onConversionInfoClicked

    def _onLoaded(self, *args, **kwargs):
        super(PersonalReservesIntro, self)._onLoaded(*args, **kwargs)
        self.soundManager.setState('STATE_hangar_place', 'STATE_hangar_place_personal_reserves')

    def _finalize(self):
        self.viewModel.onClose -= self.close
        self.viewModel.onConversionInfoClicked -= self.onConversionInfoClicked
        self.__finalizeSounds()
        super(PersonalReservesIntro, self)._finalize()

    def onConversionInfoClicked(self):
        showPersonalReservesConversion()

    def close(self):
        if self.__callbackOnClose and callable(self.__callbackOnClose):
            self.__callbackOnClose()
        closeReservesIntroAndConversionView()

    def __finalizeSounds(self):
        otherViews = [R.views.lobby.personal_reserves.ReservesConversionView(), R.views.lobby.personal_reserves.ReservesActivationView()]
        isOnlyOne = True
        for viewIdToClose in otherViews:
            introView = self._uiLoader.windowsManager.getViewByLayoutID(viewIdToClose)
            if introView:
                isOnlyOne = False

        if isOnlyOne:
            self.soundManager.setState('STATE_hangar_place', 'STATE_hangar_place_garage')
