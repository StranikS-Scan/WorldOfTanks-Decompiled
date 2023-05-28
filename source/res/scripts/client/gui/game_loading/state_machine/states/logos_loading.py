# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_loading/state_machine/states/logos_loading.py
import typing
from frameworks.state_machine import StringEvent, StateFlags
import game_loading_bindings
from gui.game_loading import loggers
from gui.game_loading.state_machine.const import GameLoadingStates, GameLoadingStatesEvents
from gui.game_loading.state_machine.states.base import BaseViewResourcesTickingState
from gui.impl import backport
from gui.impl.gen import R
from helpers import getFullClientVersion
if typing.TYPE_CHECKING:
    from gui.game_loading.resources.models import LogoModel
    from gui.game_loading.resources.local.base import LocalResources
_logger = loggers.getStatesLogger()

class LogosLoadingState(BaseViewResourcesTickingState):
    __slots__ = ('_ageRatingPath',)

    def __init__(self, logos, ageRatingPath):
        super(LogosLoadingState, self).__init__(stateID=GameLoadingStates.LOADING_LOGOS.value, resources=logos, flags=StateFlags.INITIAL, isSelfTicking=False, onCompleteEvent=StringEvent(GameLoadingStatesEvents.LOGOS_SHOWN.value))
        self._ageRatingPath = ageRatingPath

    def _view(self, resource):
        if not game_loading_bindings.isViewOpened():
            _logger.debug('[%s] opening GF view.', self)
            game_loading_bindings.createLoadingView()
        data = {'version': getFullClientVersion() if resource.showVersion else '',
         'copyright': backport.text(R.strings.menu.copy()) if resource.showCopyright else '',
         'logoType': resource.type,
         'transitionTime': resource.transition,
         'info': resource.info,
         'infoStyle': resource.infoStyle.value,
         'ageRatingPath': self._ageRatingPath}
        game_loading_bindings.setViewData(data)
        _logger.debug('[%s] image [%s] shown.', self, resource)
