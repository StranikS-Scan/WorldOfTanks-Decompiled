# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/fade_in_out.py
import logging
from functools import wraps
from BWUtil import AsyncReturn
from gui.impl.common.fade_manager import UseFading
from gui.shared.close_confiramtor_helper import CloseConfirmatorsHelper
from helpers import dependency
from story_mode.skeletons.story_mode_fading_controller import IStoryModeFadingController
from wg_async import wg_await, wg_async, forwardAsFuture
_logger = logging.getLogger(__name__)

class UseStoryModeFading(UseFading):
    _fadeManager = dependency.descriptor(IStoryModeFadingController)


class UseHeaderNavigationImpossible(object):

    def __call__(self, func):

        @wraps(func)
        @wg_async
        def wrapper(*args, **kwargs):

            @wg_async
            def confirmation():
                raise AsyncReturn(False)

            confirmationHelper = CloseConfirmatorsHelper()
            confirmationHelper.start(confirmation)
            yield wg_await(forwardAsFuture(func(*args, **kwargs)))
            confirmationHelper.stop()

        return wrapper
