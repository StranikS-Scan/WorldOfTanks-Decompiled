# Embedded file name: scripts/client/PostProcessing/Effects/__init__.py
"""PostProcessing.Effects python module
This module imports all Effects for ease-of-use by script programmers.
"""
s_effectFactories = {}

class implementEffectFactory:

    def __init__(self, name, desc, *defaultArgs):
        self.name = name
        self.desc = desc
        self.defaultArgs = defaultArgs

    def __call__(self, f):

        def callFn(*args):
            if len(args) > 0:
                return f(*args)
            else:
                return f(*self.defaultArgs)

        fn = callFn
        s_effectFactories[self.name] = [self.desc, fn]
        return fn


def getEffectNames():
    """
            This method returns a list of effect (names, descriptions)
            used by the World Editor.
    """
    ret = []
    for key in sorted(s_effectFactories.iterkeys()):
        desc = s_effectFactories[key][0]
        ret.append((key, desc))

    return ret


def effectFactory(name):
    """
            This method builds a effect, given the corresponding factory name.
    """
    return s_effectFactories[name][1]()


@implementEffectFactory('<new empty effect>', 'Create a new, empty effect.')
def empty():
    e = Effect()
    e.name = 'unnamed effect'
    e.phases = []
    return e


from Bloom import *
from ColourCorrect import *
from DownSample import *
from Sharpen import *
from EdgeDetect import *
from Emboss import *
from Shimmer import *
from Posterise import *
from Rainbow import *
from DepthOfField import *
from PlayerFader import *
from RegistrationTest import *
from ScotopicVision import *
from DistortionTransfer import *
from FilmGrain import *
from Hatching import *
from MultiBlur import *
from FXAA import *
