# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/FilterUtilities.py
import BigWorld

def enableVisualiseAvatarFilter(entity):
    if hasattr(entity.filter, 'debugMatrixes') and callable(entity.filter.debugMatrixes):
        disableVisualiseAvatarFilter(entity)
        entity._filterCubeModels = []
        for matrixProvider in entity.filter.debugMatrixes():
            cubeModel = BigWorld.Model('helpers/models/unit_cube.model')
            servo = BigWorld.Servo(matrixProvider)
            cubeModel.addMotor(servo)
            entity.addModel(cubeModel)
            entity._filterCubeModels.append(cubeModel)


def disableVisualiseAvatarFilter(entity):
    if hasattr(entity, '_filterCubeModels'):
        for cube in entity._filterCubeModels:
            entity.delModel(cube)

        del entity._filterCubeModels


def enableVisualiseAllAvatarFilters():
    for entity in BigWorld.entities.values():
        enableVisualiseAvatarFilter(entity)


def disableVisualiseAllAvatarFilters():
    for entity in BigWorld.entities.values():
        disableVisualiseAvatarFilter(entity)
