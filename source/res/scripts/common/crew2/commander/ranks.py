# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/crew2/commander/ranks.py
from collections import namedtuple
import typing
import ResMgr
from items import _xml
import nations
RankRecord = namedtuple('RankRecord', ('name', 'icon', 'index'))

class CommanderRanks(object):

    def __init__(self, configPath):
        self._nationalRanks = {}
        self._load(configPath)

    def getRankRecord(self, nationID, rank):
        return self._nationalRanks.get(rank, {}).get(nationID)

    def isValidRank(self, rank):
        return rank in self._nationalRanks

    def _load(self, path):
        section = ResMgr.openSection(path)
        if section is None:
            _xml.raiseWrongXml(None, path, 'can not open or read')
        xmlCtx = (None, path)
        self._nationalRanks = self._loadNationalRanks(xmlCtx, section, 'nation_ranks')
        self._validateNationalRanks(xmlCtx)
        ResMgr.purge(path, True)
        return

    @staticmethod
    def _loadNationalRanks(xmlCtx, section, subsectionName):
        nationalRanksSection = _xml.getSubsection(xmlCtx, section, subsectionName)
        nationalRanks = {}
        for nationSection in nationalRanksSection.values():
            nationName = _xml.readString(xmlCtx, nationSection, 'name')
            nationCtx = (xmlCtx, 'nation[name={}]'.format(nationName))
            if nationName not in nations.NAMES:
                _xml.raiseWrongXml(nationCtx, '', 'Invalid nation')
            nationID = nations.INDICES.get(nationName)
            index = 0
            for rankSection in nationSection['ranks'].values():
                ID = _xml.readString(nationCtx, rankSection, 'id')
                name = _xml.readString(nationCtx, rankSection, 'name')
                icon = _xml.readString(nationCtx, rankSection, 'icon')
                rankNations = nationalRanks.setdefault(ID, {})
                index += 1
                rankNations[nationID] = RankRecord(name, icon, index)

        return nationalRanks

    def _validateNationalRanks(self, xmlCtx):
        for rankNations in self._nationalRanks.itervalues():
            missingIDs = set(nations.INDICES.values()) - set(rankNations.keys())
            if missingIDs:
                missingNations = [ nations.NAMES[nationID] for nationID in missingIDs ]
                _xml.raiseWrongXml(xmlCtx, '', 'Missing nations {}'.format(missingNations))
