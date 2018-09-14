# Python 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/FX/Joints/HardPoint.py
from FX import s_sectionProcessors
from FX import typeCheck
from FX.Joint import Joint
from bwdebug import *
import BigWorld

class HardPoint(Joint):
    """
    This class implements a Joint that attaches an actor to a HardPoint.
    
    The actor may be any PyAttachment, for example a model or a
    particle system.  If the actor is a model, that model must have
    the corresponding HardPoint in order to align them.  If not, you
    should use the Node Joint instead.
    """

    def load(self, pSection, prereqs = None):
        """
        This method loads the HardPoint Joint from a data section.  The hard-
        point name is read from the section name.
        """
        self.hpName = pSection.asString
        return self

    def attach(self, actor, source, target = None):
        if actor.attached:
            ERROR_MSG('actor is already attached!', actor, self.hpName)
            return 0
        try:
            setattr(source.model, self.hpName, actor)
        except AttributeError:
            try:
                setattr(source, self.hpName, actor)
            except AttributeError:
                ERROR_MSG('Missing hardpoint', source, 'HP_' + self.hpName)

        except:
            try:
                setattr(source, self.hpName, actor)
            except:
                ERROR_MSG('Unknown error', source, self.hpName)

    def detach(self, actor, source, target = None):
        if not actor.attached:
            return
        try:
            source.model.node('HP_' + self.hpName).detach(actor)
        except AttributeError:
            try:
                source.node('HP_' + self.hpName).detach(actor)
            except:
                ERROR_MSG('Unknown error', source, self.hpName)


s_sectionProcessors['HardPoint'] = HardPoint
s_sectionProcessors['Hardpoint'] = HardPoint
