# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/FX/Joints/PPScreen.py
# Compiled at: 2010-08-25 17:58:21
from FX import s_sectionProcessors
from FX import typeCheck
from FX.Joint import Joint
from bwdebug import *
import BigWorld
import PostProcessing

class PPScreen(Joint):
    """
    This class implements a Joint that attaches a PostProcessing chain to the 
    screen.
    
    The actor must be a PPChain.
    """

    def load(self, pSection, prereqs=None):
        return self

    def attach(self, actor, source, target=None):
        ch = PostProcessing.chain()
        ch += actor
        PostProcessing.chain(ch)

    def detach(self, actor, source, target=None):
        ch = PostProcessing.chain()
        for effect in actor:
            try:
                ch.remove(effect)
            except ValueError:
                pass

        PostProcessing.chain(ch)


s_sectionProcessors['PPScreen'] = PPScreen
