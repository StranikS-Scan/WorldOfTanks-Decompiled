# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/battle/enums.py
from enum import Enum

class BanState(Enum):
    PREPICK = 'prepick'
    VOTING = 'voting'
    FINISHED = 'finished'
    NONE = 'none'


class CandidateState(Enum):
    NOSELECTED = 'noSelected'
    DONTBANSELECTED = 'dontBanSelected'
    SINGLECANDIDATE = 'singleCandidate'
    MULTIPLECANDIDATES = 'multipleCandidates'
