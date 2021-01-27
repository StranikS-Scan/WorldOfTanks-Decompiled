# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/bob_common.py
from wotdecorators import noexcept
RECORD_SEPARATOR = '#'
PARAMETER_SEPARATOR = '|'

@noexcept
def deserializeActivatedSkill(data):
    skillsByTeams = dict()
    if not data:
        return skillsByTeams
    else:
        for skillRecord in data.split(RECORD_SEPARATOR):
            team, skill, activatedAt, expireAt, countLeft = skillRecord.split(PARAMETER_SEPARATOR)
            expireAt = int(expireAt) if expireAt else None
            activatedAt = int(activatedAt) if activatedAt else None
            skillsByTeams[int(team)] = {'team': int(team),
             'skill': skill,
             'activated_at': activatedAt,
             'expire_at': expireAt,
             'count_left': int(countLeft)}

        return skillsByTeams


@noexcept
def deserializeRecalculate(data):
    records = data.split(RECORD_SEPARATOR)
    if len(records[0].split(PARAMETER_SEPARATOR)) == 2:
        nextRecalculationTimestamp, isRecalculating = records[0].split(PARAMETER_SEPARATOR)
    else:
        nextRecalculationTimestamp, isRecalculating = 0, False
    parsedValues = dict()
    parsedValues['timestamp'] = int(nextRecalculationTimestamp)
    parsedValues['is_recalculating'] = bool(int(isRecalculating))
    parsedValues.setdefault('teams', {})
    for recordByTeam in records[1:]:
        team, score, rank, canJoin, correctingCoefficient = recordByTeam.split(PARAMETER_SEPARATOR)
        correctingCoefficient = float(correctingCoefficient) if correctingCoefficient else None
        parsedValues['teams'][int(team)] = {'team': int(team),
         'rank': int(rank),
         'correcting_coefficient': correctingCoefficient,
         'score': int(score),
         'can_join': bool(int(canJoin))}

    return parsedValues
