# Python 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/FX/Events/PlayAction.py
from FX.Event import Event
from FX.Event import TRANSFORM_DEPENDENT_EVENT
from FX import s_sectionProcessors
import BigWorld
from bwdebug import *

class PlayAction(Event):
    """
    This class implements an event that plays an action or list
    of actions on a model.  Specify the list of actions in xml via
    any number of "Action" tags.  The actions will be played in sequence.
    This class can be created via the name "PlayActions" in addition to the
    standard class factory name of "PlayAction."
    """

    def __init__(self):
        self.actions = []

    def load(self, pSection, prereqs = None):
        """This method loads the PlayAction event from an XML data section.
        It reads in a list of "Action" tags, which are string names of the
        actions to play, in sequence, on the actor, which must be a model."""
        self.actions = pSection.readStrings('Action')
        return self

    def go(self, effect, actor, source, target, **kargs):
        dur = 0.0
        curr = actor
        for i in self.actions:
            try:
                curr = getattr(curr, i)()
                dur += curr.duration
            except EnvironmentError:
                DEBUG_MSG('ActionQueuer op() cannot queue actions when our Model is not in the world', i, actor, source, target)

        return dur

    def duration(self, actor, source, target):
        dur = 0.0
        try:
            for i in self.actions:
                try:
                    dur += actor.action(i).duration
                except:
                    pass

            return dur
        except:
            return 0.0

    def eventTiming(self):
        return TRANSFORM_DEPENDENT_EVENT


s_sectionProcessors['PlayAction'] = PlayAction
s_sectionProcessors['PlayActions'] = PlayAction
