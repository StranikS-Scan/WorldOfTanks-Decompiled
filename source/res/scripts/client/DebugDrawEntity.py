# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/DebugDrawEntity.py
from collections import defaultdict
import BigWorld
import GUI
from Math import Vector3, Matrix
import math_utils
from helpers.CallbackDelayer import CallbackDelayer

class DebugDrawEntity(BigWorld.Entity):
    CUBE_MODEL = 'helpers/models/unit_cube.model'
    SPHERE_MODEL = 'helpers/models/unit_sphere.model'

    def __init__(self):
        super(DebugDrawEntity, self).__init__()
        self.objectStates = defaultdict(lambda : {'version': 0,
         'models': [],
         '3Dtexts': []})
        self.reuseModels = defaultdict(list)
        self.reuse3DTexts = []
        self.timer = CallbackDelayer()

    def set_drawObjects(self, prev):
        self.__update()

    def onEnterWorld(self, prereqs):
        self.__update()

    def onLeaveWorld(self):
        for _, state in self.objectStates.iteritems():
            for _, model, _ in state['models']:
                BigWorld.delModel(model)

            for model, _, _ in state['3Dtexts']:
                BigWorld.delModel(model)

        for listOfModels in self.reuseModels.itervalues():
            for model, _ in listOfModels:
                BigWorld.delModel(model)

        for model, _, _ in self.reuse3DTexts:
            BigWorld.delModel(model)

        self.timer.destroy()
        self.timer = None
        return

    def __update(self):
        objectsToUpdate = []
        objectsPresent = []
        for drawObject in self.drawObjects:
            name = drawObject['name']
            objectsPresent.append(name)
            state = self.objectStates[name]
            if state['version'] != drawObject['version']:
                for modelName, model, motor in state['models']:
                    self.reuseModels[modelName].append((model, motor))

                for textObj in state['3Dtexts']:
                    self.reuse3DTexts.append(textObj)

                state['models'][:] = []
                state['3Dtexts'][:] = []
                state['version'] = drawObject['version']
                objectsToUpdate.append((state, drawObject))

        for key in self.objectStates.keys():
            if key not in objectsPresent:
                state = self.objectStates.pop(key)
                for modelName, model, motor in state['models']:
                    self.reuseModels[modelName].append((model, motor))

                for textObj in state['3Dtexts']:
                    self.reuse3DTexts.append(textObj)

        for state, draw in objectsToUpdate:
            for line in draw['lines']:
                points = line['points']
                width = line['width']
                for segment in [ (points[i - 1], points[i]) for i in xrange(1, len(points)) ]:
                    obj = self.__createDirectedLine(segment[0], segment[1], width)
                    state['models'].append(obj)

                for point in points[1:-1]:
                    obj = self.__createSphere(point, (width * 1.25,) * 3)
                    state['models'].append(obj)

            for cube in draw['cubes']:
                obj = self.__createCube(cube['position'], cube['size'])
                state['models'].append(obj)

            for sphere in draw['spheres']:
                obj = self.__createSphere(sphere['position'], sphere['radius'])
                state['models'].append(obj)

            for text in draw['texts']:
                obj = self.__create3DText(text['position'], text['text'], text['color'], text['textSize'])
                state['3Dtexts'].append(obj)

        for listOfModels in self.reuseModels.itervalues():
            for model, _ in listOfModels:
                BigWorld.delModel(model)

        for model, _, _ in self.reuse3DTexts:
            BigWorld.delModel(model)

        self.reuseModels.clear()
        self.reuse3DTexts[:] = []

    def __createDirectedLine(self, pointA, pointB, width):
        modelName = self.CUBE_MODEL
        model, motor = self.__getModel(modelName)
        direction = pointB - pointA
        scale = (width, width, direction.length)
        rotation = (direction.yaw, direction.pitch, 0)
        translation = pointA + direction * 0.5
        m = math_utils.createSRTMatrix(scale, rotation, translation)
        m.preMultiply(math_utils.createTranslationMatrix(Vector3(0.0, -0.5, 0.0)))
        motor.signal = m
        return (modelName, model, motor)

    def __createCube(self, position, size):
        modelName = self.CUBE_MODEL
        model, motor = self.__getModel(modelName)
        m = math_utils.createSRTMatrix(size, (0, 0, 0), position)
        m.preMultiply(math_utils.createTranslationMatrix(Vector3(0.0, -0.5, 0.0)))
        motor.signal = m
        return (modelName, model, motor)

    def __createSphere(self, position, radius):
        modelName = self.SPHERE_MODEL
        model, motor = self.__getModel(modelName)
        motor.signal = math_utils.createSRTMatrix(radius, (0, 0, 0), position)
        return (modelName, model, motor)

    def __getModel(self, modelName):
        if self.reuseModels[modelName]:
            model, motor = self.reuseModels[modelName].pop()
        else:
            model = BigWorld.Model(modelName)
            motor = BigWorld.Servo(Matrix())
            model.addMotor(motor)
            BigWorld.addModel(model, self.spaceID)
        return (model, motor)

    def __create3DText(self, position, text, color, textSize):
        if self.reuse3DTexts:
            model, motor, component = self.reuse3DTexts.pop()
        else:
            attachment = GUI.Attachment()
            component = GUI.Text(text)
            attachment.component = component
            attachment.faceCamera = True
            motor = BigWorld.Servo(math_utils.createTranslationMatrix(position))
            model = BigWorld.Model('')
            model.addMotor(motor)
            BigWorld.addModel(model, self.spaceID)
            model.root.attach(attachment)
            component.visible = True
            component.multiline = True
            component.explicitSize = True
            component.filterType = GUI.Simple.eFilterType.LINEAR
            component.verticalAnchor = GUI.Simple.eVAnchor.BOTTOM
        component.text = text
        component.size = (0, textSize)
        component.colour = color
        motor.signal = math_utils.createTranslationMatrix(position)
        return (model, motor, component)
