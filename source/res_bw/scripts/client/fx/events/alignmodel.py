# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/FX/Events/AlignModel.py
from FX.Event import Event
from FX import s_sectionProcessors
from bwdebug import *

class AlignModel(Event):
    """
    This class implements an Event that sets the basis vectors for a PyModel.
    """

    def go(self, effect, actor, source, target, **kargs):
        """
        This method initiates the AlignModel event.  It requires a "Basis"
        parameter to be passed into the variable arguments dictionary, which
        is a tuple of (dir,pos).
        """
        try:
            if kargs.has_key('ModelAlignment'):
                dir, pos = kargs['ModelAlignment']
            elif kargs.has_key('Basis'):
                dir, pos = kargs['Basis']
            actor.position = pos
            actor.yaw = math.atan2(dir.x, dir.z)
        except:
            WARNING_MSG('No basis was passed into the argument list', self, actor, source, target, kargs)


s_sectionProcessors['AlignModel'] = AlignModel
