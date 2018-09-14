# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/logitech/LogitechComponentMeta.py
"""
Hand-made!
We imitate DAAPI hierarchy for AS2 flash used in Logitech Monitor
"""

class LogitechMonitorComponentMeta(object):

    def __init__(self):
        super(LogitechMonitorComponentMeta, self).__init__()
        self._flashObject = None
        return

    def _populate(self, flashObject):
        assert flashObject is not None
        self._flashObject = flashObject
        return True

    def _dispose(self):
        if self._flashObject is not None:
            self._flashObject = None
        return
