# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/common/fort_rush_common/battle_feedback.py
from __future__ import absolute_import

def packPersonalScoreFeedback(score, totalScore):
    return (score & 4294967295L) << 32 | totalScore & 4294967295L


def unpackPersonalScoreFeedback(packedData):
    score = packedData >> 32 & 4294967295L
    totalScore = packedData & 4294967295L
    return (score, totalScore)
