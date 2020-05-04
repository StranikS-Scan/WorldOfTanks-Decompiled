# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/secret_event/action_view_impl.py
from gui.impl.pub import ViewImpl
from gui.Scaleform.framework.entities.view_sound import ViewSoundMixin
from gui.impl.lobby.secret_event.sound_constants import ACTION_VIEW_SETTINGS

class ActionViewImpl(ViewImpl, ViewSoundMixin):
    _COMMON_SOUND_SPACE = ACTION_VIEW_SETTINGS

    def __init__(self, settings):
        super(ActionViewImpl, self).__init__(settings)
        self._initSoundManager()

    def _initialize(self):
        super(ActionViewImpl, self)._initialize()
        self._startSoundManager()

    def _finalize(self):
        self._deinitSoundManager()
        super(ActionViewImpl, self)._finalize()
