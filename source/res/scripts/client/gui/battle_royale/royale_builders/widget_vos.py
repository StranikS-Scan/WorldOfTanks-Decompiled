# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_royale/royale_builders/widget_vos.py
import logging
import typing
from collections import namedtuple
from gui.impl.gen import R
from gui.impl import backport
from gui.Scaleform.genConsts.BATTLEROYALE_ALIASES import BATTLEROYALE_ALIASES
from gui.shared.formatters import text_styles
from shared_utils import CONST_CONTAINER
StateBlock = namedtuple('StateBlock', 'state, lastID, currentID')
WidgetPreferences = namedtuple('WidgetPreferences', 'minPossibleTitleID, maxPossibleTitleID, isHuge')
if typing.TYPE_CHECKING:
    from gui.battle_royale.royale_models import Title
_logger = logging.getLogger(__name__)

class StepsStatesCollector(object):
    __slots__ = ()

    @staticmethod
    def isReverseOrder(steps):
        for step in steps:
            if step in BATTLEROYALE_ALIASES.STEP_LOST_STATES:
                return True

        return False

    def getStates(self, title):
        result = []
        if title is not None:
            progress = title.getProgress()
            if progress is not None:
                for step in progress.getSteps():
                    baseState = self.__getBaseState(title, step)
                    specializedState = self._getSpecializedState(baseState)
                    result.append(specializedState)

        return result

    def _getSpecializedState(self, state):
        return state

    def __getBaseState(self, title, step):
        if step.isAcquired():
            stepState = BATTLEROYALE_ALIASES.STEP_RECEIVED_STATE
            if step.isNewForPlayer():
                stepState = BATTLEROYALE_ALIASES.STEP_JUST_RECEIVED_STATE
                if title.isNewForPlayer():
                    stepState = BATTLEROYALE_ALIASES.STEP_JUST_RECEIVED_SHORT_STATE
        elif step.isLost() and step.isNewForPlayer():
            stepState = BATTLEROYALE_ALIASES.STEP_JUST_LOST_STATE
        else:
            stepState = BATTLEROYALE_ALIASES.STEP_NOT_RECEIVED_STATE
        return stepState


class CustomStepsStatesCollector(StepsStatesCollector):
    __slots__ = ('_resultState',)

    def __init__(self, resultState):
        super(CustomStepsStatesCollector, self).__init__()
        self._resultState = resultState

    def _getSpecializedState(self, state):
        return self._resultState


class AcquiredStepsStatesCollector(CustomStepsStatesCollector):

    def _getSpecializedState(self, state):
        if state in (BATTLEROYALE_ALIASES.STEP_JUST_RECEIVED_STATE, BATTLEROYALE_ALIASES.STEP_JUST_RECEIVED_SHORT_STATE):
            state = self._resultState
        return state


class LostStepsStatesCollector(CustomStepsStatesCollector):

    def _getSpecializedState(self, state):
        if state == BATTLEROYALE_ALIASES.STEP_JUST_LOST_STATE:
            state = self._resultState
        return state


class _SequencePart(CONST_CONTAINER):
    NOT_IN_CHAIN = 0
    CHAIN_HEAD = 1
    CHAIN_MIDDLE = 2
    CHAIN_TAIL = 3


_NEUTRAL_SEQUENCE_STEPS = {_SequencePart.NOT_IN_CHAIN: StepsStatesCollector(),
 _SequencePart.CHAIN_HEAD: StepsStatesCollector(),
 _SequencePart.CHAIN_MIDDLE: StepsStatesCollector(),
 _SequencePart.CHAIN_TAIL: StepsStatesCollector()}
_INCREASE_SEQUENCE_STEPS = {_SequencePart.NOT_IN_CHAIN: StepsStatesCollector(),
 _SequencePart.CHAIN_HEAD: StepsStatesCollector(),
 _SequencePart.CHAIN_MIDDLE: CustomStepsStatesCollector(BATTLEROYALE_ALIASES.STEP_RECEIVED_POSITIVE_STATE),
 _SequencePart.CHAIN_TAIL: CustomStepsStatesCollector(BATTLEROYALE_ALIASES.STEP_RECEIVED_POSITIVE_STATE)}
_INCREASE_SEQUENCE_NEW_STEPS = {_SequencePart.NOT_IN_CHAIN: AcquiredStepsStatesCollector(BATTLEROYALE_ALIASES.STEP_RECEIVED_BLINK_STATE),
 _SequencePart.CHAIN_HEAD: CustomStepsStatesCollector(BATTLEROYALE_ALIASES.STEP_RECEIVED_BLINK_STATE),
 _SequencePart.CHAIN_MIDDLE: CustomStepsStatesCollector(BATTLEROYALE_ALIASES.STEP_RECEIVED_BLINK_STATE),
 _SequencePart.CHAIN_TAIL: AcquiredStepsStatesCollector(BATTLEROYALE_ALIASES.STEP_RECEIVED_BLINK_STATE)}
_DECREASE_SEQUENCE_STEPS = {_SequencePart.NOT_IN_CHAIN: LostStepsStatesCollector(BATTLEROYALE_ALIASES.STEP_JUST_LOST_SHORT_STATE),
 _SequencePart.CHAIN_HEAD: LostStepsStatesCollector(BATTLEROYALE_ALIASES.STEP_JUST_LOST_SHORT_STATE),
 _SequencePart.CHAIN_MIDDLE: CustomStepsStatesCollector(BATTLEROYALE_ALIASES.STEP_NOT_RECEIVED_STATE),
 _SequencePart.CHAIN_TAIL: CustomStepsStatesCollector(BATTLEROYALE_ALIASES.STEP_NOT_RECEIVED_STATE)}
_DECREASE_SEQUENCE_NEW_STEPS = {_SequencePart.NOT_IN_CHAIN: LostStepsStatesCollector(BATTLEROYALE_ALIASES.STEP_LOST_BLINK_STATE),
 _SequencePart.CHAIN_HEAD: CustomStepsStatesCollector(BATTLEROYALE_ALIASES.STEP_LOST_BLINK_STATE),
 _SequencePart.CHAIN_MIDDLE: CustomStepsStatesCollector(BATTLEROYALE_ALIASES.STEP_LOST_BLINK_STATE),
 _SequencePart.CHAIN_TAIL: LostStepsStatesCollector(BATTLEROYALE_ALIASES.STEP_LOST_BLINK_STATE)}

def getVOsSequence(preferences, stateBlocks, titles):
    result = []
    sequenceStates = [_SequencePart.NOT_IN_CHAIN]
    if len(stateBlocks) > 1:
        sequenceStates = [ _SequencePart.CHAIN_MIDDLE for _ in stateBlocks ]
        sequenceStates[0] = _SequencePart.CHAIN_HEAD
        sequenceStates[-1] = _SequencePart.CHAIN_TAIL
    for index, block in enumerate(stateBlocks):
        builder = _BLOCKS_VOS_BUILDERS.get(block.state)
        if builder is not None:
            result.append(builder(preferences, block, sequenceStates[index], titles))
        _logger.error('Can not find builder for state = %s', block.state)

    return result


def _buildInitTitleVO(preferences, stateBlock, sequenceState, titles):
    currentTitle = titles[stateBlock.currentID]
    nextTitle = titles[stateBlock.currentID + 1]
    stepsOverrider = _NEUTRAL_SEQUENCE_STEPS[sequenceState]
    steps = _getStepsVO(preferences, nextTitle, stepsOverrider)
    infoText, nextInfoText = _getInfoTexts(preferences, stateBlock.state, currentTitle, nextTitle)
    titleRightVO = _getTitleVO(preferences, nextTitle)
    return _getBlockVO(preferences, stateBlock.state, titleRightVO=titleRightVO, steps=steps, infoText=infoText, nextInfoText=nextInfoText)


def _buildFiniTitleVO(preferences, stateBlock, sequenceState, titles):
    currentTitle = titles[stateBlock.currentID]
    titleRightVO = _getTitleVO(preferences, currentTitle, True)
    return _getBlockVO(preferences, stateBlock.state, titleRightVO=titleRightVO)


def _buildIdleTitleVO(preferences, stateBlock, sequenceState, titles):
    currentTitle = titles[stateBlock.currentID]
    nextTitle = titles[stateBlock.currentID + 1]
    stepsOverrider = _NEUTRAL_SEQUENCE_STEPS[sequenceState]
    steps = _getStepsVO(preferences, nextTitle, stepsOverrider)
    titleLeftVO = _getTitleVO(preferences, currentTitle, True)
    titleRightVO = _getTitleVO(preferences, nextTitle)
    return _getBlockVO(preferences, stateBlock.state, titleLeftVO=titleLeftVO, titleRightVO=titleRightVO, steps=steps)


def _buildDecreaseTitleVO(preferences, stateBlock, sequenceState, titles):
    lastTitle = titles[stateBlock.lastID]
    currentTitle = titles[stateBlock.currentID]
    nextTitle = titles[stateBlock.lastID + 1]
    stepsOverrider = _DECREASE_SEQUENCE_STEPS[sequenceState]
    steps = _getStepsVO(preferences, nextTitle, stepsOverrider)
    newStepsOverrider = _DECREASE_SEQUENCE_NEW_STEPS[sequenceState]
    newSteps = _getStepsVO(preferences, lastTitle, newStepsOverrider)
    infoText, nextInfoText = _getInfoTexts(preferences, stateBlock.state, lastTitle, currentTitle)
    if stateBlock.state == BATTLEROYALE_ALIASES.FIRST_TITLE_LOST_STATE:
        currentTitle = None
    titleLeftVO = _getTitleVO(preferences, lastTitle, True)
    titleRightVO = _getTitleVO(preferences, nextTitle)
    newTitleVO = _getTitleVO(preferences, currentTitle, True)
    return _getBlockVO(preferences, stateBlock.state, titleLeftVO=titleLeftVO, titleRightVO=titleRightVO, newTitleVO=newTitleVO, steps=steps, newSteps=newSteps, infoText=infoText, nextInfoText=nextInfoText)


def _buildIncreaseTitleVO(preferences, stateBlock, sequenceState, titles):
    lastTitle = titles[stateBlock.lastID]
    currentTitle = titles[stateBlock.currentID]
    nextTitle = titles[stateBlock.currentID + 1] if stateBlock.currentID != preferences.maxPossibleTitleID else None
    stepsOverrider = _INCREASE_SEQUENCE_STEPS[sequenceState]
    steps = _getStepsVO(preferences, currentTitle, stepsOverrider)
    newStepsOverrider = _INCREASE_SEQUENCE_NEW_STEPS[sequenceState]
    newSteps = _getStepsVO(preferences, nextTitle, newStepsOverrider)
    infoText, nextInfoText = _getInfoTexts(preferences, stateBlock.state, lastTitle, currentTitle)
    lastTitle = None if lastTitle.getID() == preferences.minPossibleTitleID else lastTitle
    titleLeftVO = _getTitleVO(preferences, lastTitle, True)
    titleRightVO = _getTitleVO(preferences, currentTitle)
    newTitleVO = _getTitleVO(preferences, nextTitle)
    return _getBlockVO(preferences, stateBlock.state, titleLeftVO=titleLeftVO, titleRightVO=titleRightVO, newTitleVO=newTitleVO, steps=steps, newSteps=newSteps, infoText=infoText, nextInfoText=nextInfoText)


_BLOCKS_VOS_BUILDERS = {BATTLEROYALE_ALIASES.TITLE_IDLE_STATE: _buildIdleTitleVO,
 BATTLEROYALE_ALIASES.TITLE_INIT_STATE: _buildInitTitleVO,
 BATTLEROYALE_ALIASES.TITLE_FINI_STATE: _buildFiniTitleVO,
 BATTLEROYALE_ALIASES.TITLE_RECEIVE_STATE: _buildIncreaseTitleVO,
 BATTLEROYALE_ALIASES.TITLE_REACHIVE_STATE: _buildIncreaseTitleVO,
 BATTLEROYALE_ALIASES.TITLE_LOST_STATE: _buildDecreaseTitleVO,
 BATTLEROYALE_ALIASES.FIRST_TITLE_RECEIVE_STATE: _buildIncreaseTitleVO,
 BATTLEROYALE_ALIASES.FIRST_TITLE_REACHIVE_STATE: _buildIncreaseTitleVO,
 BATTLEROYALE_ALIASES.FIRST_TITLE_LOST_STATE: _buildDecreaseTitleVO,
 BATTLEROYALE_ALIASES.LAST_TITLE_RECEIVE_STATE: _buildIncreaseTitleVO,
 BATTLEROYALE_ALIASES.LAST_TITLE_REACHIVE_STATE: _buildIncreaseTitleVO,
 BATTLEROYALE_ALIASES.LAST_TITLE_LOST_STATE: None}

def _getStepsVO(preferences, title, statesCollector=StepsStatesCollector()):
    steps = statesCollector.getStates(title)
    isReverseOrder = statesCollector.isReverseOrder(steps)
    return {'steps': steps if steps else (),
     'infoText': '',
     'hasTooltip': not preferences.isHuge,
     'isReverseOrder': isReverseOrder}


def _getDefaultStepsVO(preferences):
    return {'steps': (),
     'infoText': '',
     'hasTooltip': bool(not preferences.isHuge),
     'isReverseOrder': False}


def _getTitleVO(preferences, title, isEnabled=False):
    if title is not None:
        imageSrcSize = BATTLEROYALE_ALIASES.TITLE_HUGE if preferences.isHuge else BATTLEROYALE_ALIASES.TITLE_MEDIUM
        return {'imageSrc': title.getIcon(imageSrcSize),
         'smallImageSrc': title.getIcon(BATTLEROYALE_ALIASES.TITLE_SMALL),
         'isEnabled': isEnabled,
         'titleID': str(title.getID()),
         'hasTooltip': not preferences.isHuge}
    else:
        return


def _getBlockVO(preferences, state, infoText='', nextInfoText='', titleLeftVO=None, titleRightVO=None, newTitleVO=None, steps=None, newSteps=None):
    return {'state': state,
     'titleLeftVO': titleLeftVO,
     'titleRightVO': titleRightVO,
     'newTitleVO': newTitleVO,
     'stepsContainerVO': steps or _getDefaultStepsVO(preferences),
     'newStepsContainerVO': newSteps or _getDefaultStepsVO(preferences),
     'infoText': infoText,
     'nextInfoText': nextInfoText,
     'isHuge': preferences.isHuge}


def _getInfoTexts(preferences, state, lastTitle, currentTitle):
    infoText = ''
    newInfoText = ''
    if lastTitle.getID() == preferences.minPossibleTitleID and not preferences.isHuge:
        infoText = text_styles.hightlight(backport.text(R.strings.battle_royale.battleRoyaleWidget.initText(), steps=_getNotAcquiredAmount(_getStepsVO(preferences, currentTitle).get('steps'))))
    if currentTitle.getID() == preferences.minPossibleTitleID and not preferences.isHuge:
        newInfoText = text_styles.hightlight(backport.text(R.strings.battle_royale.battleRoyaleWidget.initText(), steps=_getNotAcquiredAmount(_getStepsVO(preferences, lastTitle).get('steps'))))
    if state in (BATTLEROYALE_ALIASES.FIRST_TITLE_RECEIVE_STATE, BATTLEROYALE_ALIASES.TITLE_RECEIVE_STATE, BATTLEROYALE_ALIASES.LAST_TITLE_RECEIVE_STATE):
        newInfoText = text_styles.hightlight(backport.text(R.strings.battle_royale.battleRoyaleWidget.newTitleCongrat()))
    return (infoText, newInfoText)


def _getNotAcquiredAmount(steps):
    return sum([ 1 for step in steps if step in BATTLEROYALE_ALIASES.STEP_NOT_RECEIVED_STATES ])
