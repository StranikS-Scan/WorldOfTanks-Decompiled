# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/FX/Effects/_Effect.py
import ResMgr
from FX import s_sectionProcessors
from bwdebug import *

def prerequisites(filename):
    """Discover the prerequisites for the given effect file. Returns
    a tuple that can be passed directly to BigWorld.loadResourceListBG"""
    if filename == '':
        return ()
    fx = Effect(filename)
    fx._prerequisites()
    return tuple(fx.prereqs)


class Effect:
    _debugTimings = 0

    def __init__(self, fileName):
        self.actors = {}
        self.joints = {}
        self.events = []
        self.fileName = fileName

    def _prerequisites(self):
        self.prereqs = set()
        pSection = ResMgr.openSection(self.fileName)
        if not pSection:
            ERROR_MSG('Could not open file', self.fileName)
            return None
        else:
            self._prerequisitesFromSection(pSection)
            self.prereqs.add(self.fileName)
            return None

    def _create(self, prereqs=None):
        try:
            pSection = prereqs[self.fileName]
        except KeyError:
            pSection = ResMgr.openSection(self.fileName)
        except TypeError:
            pSection = ResMgr.openSection(self.fileName)

        if pSection != None:
            self._createFromSection(pSection, prereqs)
        else:
            ERROR_MSG('Could not open file', self.fileName)
            return
        if Effect._debugTimings == 1:
            self.events.append(('', timedEvents.DebugEventTiming()))
        return

    def _parse(self, tag, store, pSection, prereqs=None, gatherPrerequisites=False):
        for sname, ds in pSection.items():
            if sname == tag:
                section = ds.items()[0][1]
                if s_sectionProcessors.has_key(section.name):
                    instance = s_sectionProcessors[section.name]()
                    if not gatherPrerequisites:
                        result = instance.load(section, prereqs)
                        if result != None:
                            try:
                                store[ds.asString] = result
                            except:
                                store.append((ds.asString, result))

                        else:
                            ERROR_MSG('None was returned.  Not adding to this effect : ', section.name, ds.asString)
                    else:
                        self.prereqs.add(section.asString)
                        if hasattr(instance, 'prerequisites'):
                            self.prereqs.update(instance.prerequisites(section))
                else:
                    ERROR_MSG('No section processor matches the tag ', section.name, ds.asString)
                    result = None

        return

    def _modelName(self, visualName):
        if len(visualName) > 7:
            if visualName[-7:] == '.visual':
                return visualName[:-7] + '.model'
        return visualName

    def _prerequisitesFromSection(self, pSection):
        self._parse('Actor', self.actors, pSection, gatherPrerequisites=True)
        self._parse('Event', self.events, pSection, gatherPrerequisites=True)

    def _createFromSection(self, pSection, prereqs=None):
        self._parse('Actor', self.actors, pSection, prereqs)
        self._parse('Joint', self.joints, pSection, prereqs)
        self._parse('Event', self.events, pSection, prereqs)
        for actor in self.joints.keys():
            if not self.actors.has_key(actor):
                ERROR_MSG('Actor not found', actor)
                del self.joints[actor]

        for actor in self.actors.keys():
            if not self.joints.has_key(actor):
                WARNING_MSG('Actor exists, but is not attached anywhere', actor)

    def _extendTime(self, event, duration):
        pass
