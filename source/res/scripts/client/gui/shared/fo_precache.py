# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/fo_precache.py
import BigWorld
from debug_utils import LOG_ERROR, LOG_DEBUG
_IS_ENABLED = True
if _IS_ENABLED:

    def add(path, forced=False):
        result = True
        try:
            result = BigWorld.precacheScaleformResource(path, forced)
            if result:
                LOG_DEBUG('Resource is added to precache', path)
        except AttributeError:
            LOG_ERROR('BigWorld package does not include function precacheScaleformResource')

        return result


    def clear(path=''):
        try:
            BigWorld.eraseScaleformResFromCache(path)
            LOG_DEBUG('Resource(s) is(are) cleared from precache', path)
        except AttributeError:
            LOG_ERROR('BigWorld package does not include function eraseScaleformResFromCache')


else:

    def add(path, forced=False):
        return True


    def clear(path=''):
        pass
