# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/LootBoxReader.py
import ResMgr
from debug_utils import LOG_ERROR
from helpers.EffectsList import effectsFromSection
from collections import namedtuple
_StateEntry = namedtuple('StateEntry', ['enable',
 'visible',
 'animation',
 'effects',
 'sound',
 'transitions'])
_AnimationEntry = namedtuple('AnimationEntry', ['action', 'trigger'])
_EffectsEntry = namedtuple('EffectsEntry', ['effect', 'keep'])
_EffectsEntry.__new__.__defaults__ = (None, [])

def getRoot(config):
    root = ResMgr.openSection(config)
    if not root:
        LOG_ERROR('Missing LootBox config {}'.format(config))
    return root


def readEntity(root):
    dataSec = root['entity']
    if not dataSec:
        LOG_ERROR("Missing section 'entity' in {}".format(root.name))
        return (None, None)
    else:
        position = dataSec.readVector3('position', (0, 0, 0))
        direction = dataSec.readVector3('direction', (0, 0, 0))
        modelName = dataSec.readString('modelName', '')
        anchorName = dataSec.readString('anchorName', '')
        selectionId = dataSec.readString('selectionId', '')
        return (position,
         direction,
         modelName,
         anchorName,
         selectionId)


def readStates(root):
    dataSec = root['states']
    if not dataSec:
        LOG_ERROR("Missing section 'states' in {}".format(root.name))
        return {}
    else:
        states = {}
        for stateSec in dataSec.values():
            state = stateSec.readString('tag', '')
            if state is None:
                continue
            enable = stateSec.readBool('enable', False)
            visible = stateSec.readBool('visible', False)
            sound = stateSec.readString('sound', '')
            transitions = stateSec.readString('transitions', '').split()
            animation = __readAnimation(stateSec['animationSequence'])
            effects = __readEffects(stateSec['effects'])
            states[state] = _StateEntry(enable, visible, animation, effects, sound, transitions)

        return states


def readEffects(root):
    dataSec = root['effects']
    if not dataSec:
        LOG_ERROR("Missing section 'effects' in {}".format(root.name))
        return {}
    effectsTimeLine = {}
    for value in dataSec.values():
        name = value.name
        effectsTimeLine[name] = effectsFromSection(value)

    return effectsTimeLine


def __readAnimation(dataSec):
    if not dataSec:
        return None
    else:
        animation = []
        for entry in dataSec.values():
            action = entry.readString('action', '')
            trigger = entry.readString('trigger', '')
            animation.append(_AnimationEntry(action, trigger))

        return animation


def __readEffects(dataSec):
    if not dataSec:
        return _EffectsEntry()
    start = dataSec.readString('start', '')
    keep = dataSec.readString('keep', '').split()
    return _EffectsEntry(start, keep)
