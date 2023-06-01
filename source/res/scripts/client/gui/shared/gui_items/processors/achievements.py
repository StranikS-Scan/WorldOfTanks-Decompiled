# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/processors/achievements.py
import logging
import BigWorld
from gui import SystemMessages
from gui.SystemMessages import SM_TYPE
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.gui_items.processors import Processor
from gui.Scaleform.Waiting import Waiting
_logger = logging.getLogger(__name__)

class SetAchievementsLayout(Processor):
    __WAITING_TEXT = 'achivements20'

    def __init__(self, layout):
        super(SetAchievementsLayout, self).__init__()
        self.__layout = layout

    def _errorHandler(self, code, errStr='', ctx=None):
        res = super(SetAchievementsLayout, self)._errorHandler(code, errStr, ctx)
        Waiting.hide(self.__WAITING_TEXT)
        SystemMessages.pushMessage(backport.text(R.strings.system_messages.achievements.server_error()), type=SM_TYPE.Error)
        return res

    def _request(self, callback):
        _logger.debug('Make server request to set achievements layout: %s', self.__layout)
        Waiting.show(self.__WAITING_TEXT)
        BigWorld.player().achievements20.setAchievementsLayout(self.__layout, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))

    def _successHandler(self, code, ctx=None):
        res = super(SetAchievementsLayout, self)._successHandler(code, ctx)
        Waiting.hide(self.__WAITING_TEXT)
        return res
