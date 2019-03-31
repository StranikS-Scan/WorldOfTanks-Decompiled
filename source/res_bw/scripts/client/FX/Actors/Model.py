# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/FX/Actors/Model.py
# Compiled at: 2010-05-25 20:46:16
import BigWorld
from bwdebug import *
from FX.Actor import Actor
from FX import s_sectionProcessors

class Model(Actor):
    """
    This class implements an Actor that is a PyModel.
    """

    def load(self, pSection, prereqs=None):
        """
        This method loads the PyModel Actor from a data section. The
        the model resource ID is read from the section name.            
        """
        try:
            actor = prereqs.pop(pSection.asString)
        except:
            try:
                actor = BigWorld.Model(pSection.asString)
            except:
                ERROR_MSG('Could not create Model', pSection.asString)
                actor = None

        return actor

    def prerequisites(self, pSection):
        return [pSection.asString]


s_sectionProcessors['Model'] = Model
