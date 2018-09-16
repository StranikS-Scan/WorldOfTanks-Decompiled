# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/extensions/football/client/GoalMarker.py
import BigWorld

class GoalMarker(BigWorld.Entity):

    def __init__(self):
        super(GoalMarker, self).__init__(self)
        self.model = None
        return

    def prerequisites(self):
        return [self.modelName]

    def onEnterWorld(self, prereqs):
        team = BigWorld.player().team
        if self.teamNumber == team:
            self.model = prereqs[self.modelName]
            self.model.addMotor(BigWorld.Servo(self.matrix))

    def onLeaveWorld(self):
        self.model = None
        return
