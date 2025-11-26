# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/user_missions/constants/event_banner_state.py
from frameworks.wulf import ViewModel

class EventBannerState(ViewModel):
    __slots__ = ()
    ANNOUNCE = 'announce'
    INTRO = 'intro'
    IN_PROGRESS = 'inProgress'
    INACTIVE = 'inactive'
    FINISHED = 'finished'

    def __init__(self, properties=0, commands=0):
        super(EventBannerState, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(EventBannerState, self)._initialize()
