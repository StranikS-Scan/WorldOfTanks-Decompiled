# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/example.py
from component import Component, InputSlot, OutputSlot, SLOT_TYPE

class HelloFromPython(Component):

    @classmethod
    def componentCategory(cls):
        pass

    def slotDefinitions(self):
        return [InputSlot('project_name', SLOT_TYPE.STR, None), OutputSlot('result', SLOT_TYPE.STR, HelloFromPython._execute)]

    def _execute(self, projectName):
        res = ' '.join(('Hello', projectName, 'from python vse...'))
        return res


class GetProjectName(Component):

    @classmethod
    def componentCategory(cls):
        pass

    def slotDefinitions(self):
        return [OutputSlot('result', SLOT_TYPE.STR, GetProjectName._execute)]

    def _execute(self):
        pass
