# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/requesters/bob_requester.py
import zlib
import BigWorld
from adisp import async
from bob_common import deserializeRecalculate, deserializeActivatedSkill
from gui.bob.bob_data_containers import TeamSkillData, TeamData, RecalculationData
from gui.shared.utils.requesters.abstract import AbstractSyncDataRequester

class BobRequester(AbstractSyncDataRequester):

    def getTeams(self):
        return self.getCacheValue('teams', {})

    def getSkills(self):
        return self.getCacheValue('skills', {})

    def getTeamCache(self, teamID):
        return self.getTeams().get(teamID, {})

    def getSkillCache(self, teamID):
        return self.getSkills().get(teamID, {})

    def getNextRecalculationTime(self):
        return self.getCacheValue('next_recalculation_timestamp', 0)

    def isRecalculating(self):
        return self.getCacheValue('is_recalculating', False)

    def getTeamSkillData(self, teamID):
        skillData = self.getSkillCache(teamID)
        return TeamSkillData(**skillData) if isinstance(skillData, dict) and set(skillData.keys()) >= TeamSkillData.requiredFields() else TeamSkillData(team=teamID, expire_at=None)

    def getTeamData(self, teamID):
        teamData = self.getTeamCache(teamID)
        return TeamData(**teamData) if isinstance(teamData, dict) and set(teamData.keys()) >= TeamData.requiredFields() else None

    def getRecalculationData(self):
        return RecalculationData(next_recalculation_timestamp=self.getNextRecalculationTime(), is_recalculating=self.isRecalculating())

    def _preprocessValidData(self, data):
        cache = dict()
        if 'bob' in data:
            bobData = dict(data['bob'])
            teamsStr = bobData.get('teams')
            if teamsStr and isinstance(teamsStr, str):
                newValues = deserializeRecalculate(zlib.decompress(teamsStr))
                cache['teams'] = newValues.get('teams', {})
                cache['next_recalculation_timestamp'] = newValues.get('timestamp', 0)
                cache['is_recalculating'] = newValues.get('is_recalculating', False)
            skillsStr = bobData.get('skills')
            if skillsStr and isinstance(skillsStr, str):
                cache['skills'] = deserializeActivatedSkill(zlib.decompress(skillsStr))
        return cache

    @async
    def _requestCache(self, callback):
        BigWorld.player().bob.getCache(lambda resID, value: self._response(resID, value, callback))
