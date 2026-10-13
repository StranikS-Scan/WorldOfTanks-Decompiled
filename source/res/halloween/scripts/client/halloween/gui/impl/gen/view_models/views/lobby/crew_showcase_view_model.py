# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/crew_showcase_view_model.py
from frameworks.wulf import Array, ViewModel
from halloween.gui.impl.gen.view_models.views.lobby.crew_member_view_model import CrewMemberViewModel

class CrewShowcaseViewModel(ViewModel):
    __slots__ = ('onClose', 'onClaim', 'onShop', 'onPlaySound')

    def __init__(self, properties=3, commands=4):
        super(CrewShowcaseViewModel, self).__init__(properties=properties, commands=commands)

    def getCrewMembers(self):
        return self._getArray(0)

    def setCrewMembers(self, value):
        self._setArray(0, value)

    @staticmethod
    def getCrewMembersType():
        return CrewMemberViewModel

    def getSkills(self):
        return self._getArray(1)

    def setSkills(self, value):
        self._setArray(1, value)

    @staticmethod
    def getSkillsType():
        return unicode

    def getGroupVoiceover(self):
        return self._getString(2)

    def setGroupVoiceover(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(CrewShowcaseViewModel, self)._initialize()
        self._addArrayProperty('crewMembers', Array())
        self._addArrayProperty('skills', Array())
        self._addStringProperty('groupVoiceover', '')
        self.onClose = self._addCommand('onClose')
        self.onClaim = self._addCommand('onClaim')
        self.onShop = self._addCommand('onShop')
        self.onPlaySound = self._addCommand('onPlaySound')
