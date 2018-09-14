# Embedded file name: scripts/client/messenger/proto/notations.py
from debug_utils import LOG_NOTE
from messenger import g_settings
from messenger.m_constants import PROTO_TYPE_NAMES

class _profile(object):

    def __init__(self, protoType, log = True):
        super(_profile, self).__init__()
        self._protoType = protoType
        self._doLog = log

    def __call__(self, func):

        def wrapper(*args, **kwargs):
            if not self.isEnabled():
                if self._doLog:
                    self.log(func.__name__)
            else:
                func(*args, **kwargs)

        return wrapper

    def isEnabled(self):
        raise NotImplementedError

    def log(self, name):
        raise NotImplementedError


class contacts(_profile):

    def isEnabled(self):
        return g_settings.server.useToShowContacts(self._protoType)

    def log(self, name):
        LOG_NOTE('Routine {0} is blocked. Client can not send request on changing contacts by {1} protocol'.format(name, PROTO_TYPE_NAMES[self._protoType]))


def cancel_replay_record(func):

    def wrapper(*args, **kwargs):
        import BattleReplay
        ctrl = BattleReplay.g_replayCtrl
        if ctrl.isRecording:
            ctrl.cancelSaveCurrMessage()
        else:
            func(*args, **kwargs)

    return wrapper
