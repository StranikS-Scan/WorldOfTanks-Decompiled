# Embedded file name: scripts/client/FX/Actors/PPChain.py
import BigWorld
import PostProcessing
from bwdebug import *
from FX.Actor import Actor
from FX import s_sectionProcessors

class PPChain(Actor):
    """
    This class implements an Actor that is a Post Processing Chain.
    """

    def load(self, pSection, prereqs = None):
        """
        This method loads a .ppchain file. You may also specify additional
        properties to set on the chain.
        """
        if PostProcessing.isSupported(pSection.asString):
            actor = PostProcessing.load(pSection.asString)
            if actor == None or len(actor) == 0:
                ERROR_MSG('Could not load PostProcessing chain %s' % (pSection.asString,))
                actor = []
        else:
            actor = []
        for name, section in pSection.items():
            if name == 'Property':
                varName = section.asString
                if section.has_key('Float'):
                    PostProcessing.setMaterialProperty(actor, varName, section.readFloat('Float'))
                elif section.has_key('Vector4'):
                    PostProcessing.setMaterialProperty(actor, varName, section.readVector4('Vector4'))
                elif section.has_key('Colour'):
                    col = section.readVector4('Colour')
                    col[0] /= 255.0
                    col[1] /= 255.0
                    col[2] /= 255.0
                    col[3] /= 255.0
                    PostProcessing.setMaterialProperty(actor, varName, col)
                else:
                    PostProcessing.setMaterialProperty(actor, varName, section.asString)

        return actor

    def prerequisites(self, pSection):
        return PostProcessing.prerequisites(pSection.asString)


s_sectionProcessors['PPChain'] = PPChain
