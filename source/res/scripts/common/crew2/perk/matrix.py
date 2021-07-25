# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/crew2/perk/matrix.py
from collections import Counter, defaultdict
import typing
import ResMgr
from crew2.perk.matrix_branch import PerkMatrixBranch
from crew2.perk.matrix_perk import PerkMatrixPerk
from items import _xml, perks
MAX_ULTIMATES_PER_BRANCH = 2

class PerkMatrix(object):
    __slots__ = ('_id', '_perks', '_branches', '_perkMinThreshold')

    def __init__(self, perkMatrixID):
        self._id = perkMatrixID
        self._perks = {}
        self._branches = {}
        self._perkMinThreshold = 0

    @property
    def id(self):
        return self._id

    @property
    def perks(self):
        return self._perks

    @property
    def branches(self):
        return self._branches

    @property
    def perkMinThreshold(self):
        return self._perkMinThreshold

    def hasPerk(self, perkID):
        return perkID in self._perks

    def getUltimatePerksInBranch(self, branchID):
        return [ perk.id for i, perk in self.perks.items() if perk.branch == branchID and perk.ultimate is True ]

    def getNonUltimatePerksInBranch(self, branchID):
        return [ perk.id for i, perk in self.perks.items() if perk.branch == branchID and perk.ultimate is False ]

    def loadFromDataSection(self, xmlContext, perkMatrixSection):
        maxPointInBranches = defaultdict(int)
        for _, subsection in _xml.getChildren(xmlContext, perkMatrixSection, 'perks'):
            perkMatrixPerk = PerkMatrixPerk(xmlContext, subsection)
            isValid, vMessage = perks.g_cache.perks().validatePerk(perkMatrixPerk.id, isUltimative=perkMatrixPerk.ultimate)
            if not isValid:
                _xml.raiseWrongXml(xmlContext, '', 'Perk matrix #{}. Perk with ID {} error: {}'.format(self.id, perkMatrixPerk.id, vMessage))
            self.perks[perkMatrixPerk.id] = perkMatrixPerk
            maxPointInBranches[perkMatrixPerk.branch] += perkMatrixPerk.max_points

        for _, subsection in _xml.getChildren(xmlContext, perkMatrixSection, 'branches'):
            perkMatrixBranch = PerkMatrixBranch(xmlContext, subsection, maxPointInBranches)
            self.branches[perkMatrixBranch.id] = perkMatrixBranch

        self._perkMinThreshold = _xml.readPositiveInt(xmlContext, perkMatrixSection, 'perkMinThreshold')
        self.__validatePerkBranches(xmlContext)
        self.__validateMaxUltimatesPerBranch(xmlContext)

    def __validatePerkBranches(self, xmlCtx):
        for perk in self.perks.itervalues():
            if perk.branch not in self.branches:
                _xml.raiseWrongXml(xmlCtx, '', 'Perk matrix #{} has perk {} which specifies non-existing branch'.format(self.id, perk.id))

    def __validateMaxUltimatesPerBranch(self, xmlCtx):
        counter = Counter()
        for perk in self.perks.itervalues():
            if perk.ultimate:
                counter[perk.branch] += 1
                if counter[perk.branch] > MAX_ULTIMATES_PER_BRANCH:
                    _xml.raiseWrongXml(xmlCtx, '', 'Perk matrix #{} has branch {} with more than {} ultimate perks'.format(self.id, perk.branch, MAX_ULTIMATES_PER_BRANCH))
