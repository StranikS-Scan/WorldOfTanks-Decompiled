# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_reserves/personal_reserves_intro.py
from typing import Dict, Any
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen.view_models.views.lobby.personal_reserves.reserves_intro_view_model import ReservesIntroViewModel
from gui.impl.lobby.personal_reserves.reserves_constants import PERSONAL_RESERVES_SOUND_SPACE
from gui.impl.lobby.personal_reserves.view_utils.reserves_view_monitor import ReservesViewMonitor
from gui.shared.event_dispatcher import showPersonalReservesConversion, closeViewsExceptReservesActivationView
from helpers import dependency
from skeletons.gui.impl import IGuiLoader
from uilogging.personal_reserves.loggers import PersonalReservesMetricsLogger
from uilogging.personal_reserves.logging_constants import PersonalReservesLogKeys
INTRO_UI_LOGGING_KEY = 'UILoggingParent'
INTRO_CALLBACK_ON_CLOSE_KEY = 'callbackOnClose'

class PersonalReservesIntro(ReservesViewMonitor):
    __slots__ = ('__callbackOnClose',)
    _COMMON_SOUND_SPACE = PERSONAL_RESERVES_SOUND_SPACE
    _uiLoader = dependency.descriptor(IGuiLoader)

    def __init__(self, layoutID, ctx=None):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_TOP_SUB_VIEW
        settings.model = ReservesIntroViewModel()
        self.__callbackOnClose = ctx[INTRO_CALLBACK_ON_CLOSE_KEY]
        super(PersonalReservesIntro, self).__init__(settings)
        self._uiLogger = PersonalReservesMetricsLogger(parent=ctx.get(INTRO_UI_LOGGING_KEY) or PersonalReservesLogKeys.HANGAR, item=PersonalReservesLogKeys.INTRO_WINDOW)

    @property
    def viewModel(self):
        return super(PersonalReservesIntro, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(PersonalReservesIntro, self)._initialize()
        self.viewModel.onClose += self.close
        self.viewModel.onConversionInfoClicked += self.onConversionInfoClicked
        self._uiLogger.onViewInitialize()

    def _finalize(self):
        self.viewModel.onClose -= self.close
        self.viewModel.onConversionInfoClicked -= self.onConversionInfoClicked
        super(PersonalReservesIntro, self)._finalize()
        self._uiLogger.onViewFinalize()

    def onConversionInfoClicked(self):
        showPersonalReservesConversion()

    def close(self):
        if self.__callbackOnClose and callable(self.__callbackOnClose):
            self.__callbackOnClose()
        closeViewsExceptReservesActivationView()
