# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/FX/Joints/ModelRoot.py
# Compiled at: 2010-05-25 20:46:16
from FX import s_sectionProcessors
from FX import typeCheck
from FX.Joint import Joint
from bwdebug import *
import BigWorld

class ModelRoot(Joint):
    """
    This class implements a Joint that attaches an actor to a model's root
    node.
    
    The actor may be any PyAttachment, for example a model or a
    particle system.
    """

    def attach(self, actor, source, target=None):
        if actor.attached:
            ERROR_MSG('actor is already attached!', self, actor, source)
            return 0
        try:
            source.root.attach(actor)
        except:
            try:
                source.model.root.attach(actor)
            except:
                ERROR_MSG('error in addModel to modelRoot', self, actor, source)

    def detach(self, actor, source, target=None):
        if not actor.attached:
            ERROR_MSG('actor is not attached!', self, actor, source)
            return 0
        try:
            source.root.detach(actor)
        except:
            try:
                source.model.root.detach(actor)
            except:
                ERROR_MSG('error in detach from modelRoot', self, actor, source)


s_sectionProcessors['ModelRoot'] = ModelRoot
