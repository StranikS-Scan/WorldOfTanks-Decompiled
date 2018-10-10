# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/scenery/Scenery.py
from missions.mission_1 import Mission1
from missions.mission_2 import Mission2
from missions.mission_3 import Mission3
from missions.mission_4 import Mission4
from missions.mission_5 import Mission5
from missions.mission_6 import Mission6

class Scenery(object):
    missions = {0: Mission1,
     1: Mission2,
     2: Mission3,
     3: Mission4,
     4: Mission5,
     5: Mission6}

    def __init__(self, lessonNum, assistant):
        cls = Scenery.missions.get(lessonNum, None)
        self._mission = cls(assistant) if cls else None
        return

    def destroy(self):
        if self._mission:
            self._mission.destroy()
            self._mission = None
        return

    def start(self):
        if self._mission:
            self._mission.start()

    def stop(self):
        if self._mission:
            self._mission.stop()
