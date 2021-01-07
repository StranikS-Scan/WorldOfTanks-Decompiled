# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/ui/frontline.py
from constants import QUEUE_TYPE
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.shared.event_dispatcher import showHangar
from skeletons.gui.game_control import IEventProgressionController
from helpers import dependency
from web.web_client_api import w2c, W2CSchema

class OpenFrontLinePagesMixin(object):
    __eventProgression = dependency.descriptor(IEventProgressionController)

    @w2c(W2CSchema, 'frontline_hangar')
    def selectMode(self, _):
        result = False
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is not None and self.__eventProgression.isFrontLine:
            isPrbActive = dispatcher.getFunctionalState().isInPreQueue(QUEUE_TYPE.EPIC)
            if not isPrbActive:
                actionName = PREBATTLE_ACTION_NAME.EPIC
                result = yield dispatcher.doSelectAction(PrbAction(actionName))
            else:
                result = isPrbActive
            if result:
                showHangar()
        yield {'success': result}
        return
