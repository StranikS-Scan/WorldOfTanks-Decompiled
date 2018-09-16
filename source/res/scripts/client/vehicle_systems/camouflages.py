# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/camouflages.py
from collections import namedtuple
import BigWorld
import Math
import items.vehicles
from vehicle_systems.tankStructure import VehiclePartsTuple
from vehicle_systems.tankStructure import TankPartNames, TankPartIndexes
from items.components.c11n_constants import ModificationType, C11N_MASK_REGION
from gui.shared.gui_items import GUI_ITEM_TYPE
RepaintParams = namedtuple('PaintParams', ('enabled', 'baseColor', 'color', 'metallic', 'gloss', 'fading', 'strength'))
RepaintParams.__new__.__defaults__ = (False,
 0,
 (0, 0, 0),
 Math.Vector4(0.0),
 Math.Vector4(0.0),
 0.0,
 0.0)
CamoParams = namedtuple('CamoParams', ('mask', 'excludeMap', 'tiling', 'weights', 'c0', 'c1', 'c2', 'c3'))
CamoParams.__new__.__defaults__ = ('',
 '',
 Math.Vector4(0.0),
 Math.Vector4(0.0),
 0,
 0,
 0,
 0)
_DEFAULT_GLOSS = 0.509
_DEFAULT_METALLIC = 0.23

def prepareFashions(isDamaged):
    if isDamaged:
        fashions = [None,
         None,
         None,
         None]
    else:
        fashions = [BigWorld.WGVehicleFashion(False),
         BigWorld.WGBaseFashion(),
         BigWorld.WGBaseFashion(),
         BigWorld.WGBaseFashion()]
    return VehiclePartsTuple(*fashions)


def updateFashions(fashions, vDesc, isDamaged, outfit):
    fashions = list(fashions)
    for fashionIdx, descId in enumerate(TankPartNames.ALL):
        fashion = fashions[fashionIdx]
        if fashion is None:
            continue
        camo = getCamo(outfit, fashionIdx, vDesc, descId, isDamaged)
        if camo:
            camoHandler = BigWorld.PyCamoHandler()
            fashion.setCamouflage()
            fashion.addMaterialHandler(camoHandler)
            camoHandler.setCamoParams(camo)
        repaint = getRepaint(outfit, fashionIdx, vDesc)
        if repaint:
            repaintHandler = BigWorld.PyRepaintHandler()
            fashion.addMaterialHandler(repaintHandler)
            repaintHandler.setRepaintParams(repaint)

    return


def getCamoPrereqs(outfit, vDesc):
    result = []
    if not outfit:
        return result
    else:
        for partIdx, descId in enumerate(TankPartNames.ALL):
            container = outfit.getContainer(partIdx)
            slot = container.slotFor(GUI_ITEM_TYPE.CAMOUFLAGE)
            if not slot:
                continue
            camouflage = slot.getItem()
            if camouflage:
                result.append(camouflage.texture)
                exclusionMap = vDesc.type.camouflage.exclusionMask
                compDesc = getattr(vDesc, descId, None)
                if compDesc is not None:
                    if compDesc.camouflage.exclusionMask:
                        exclusionMap = compDesc.camouflage.exclusionMask
                result.append(exclusionMap)

        return result


def getCamo(outfit, containerId, vDesc, descId, isDamaged, default=None):
    result = default
    if not outfit:
        return result
    else:
        container = outfit.getContainer(containerId)
        slot = container.slotFor(GUI_ITEM_TYPE.CAMOUFLAGE)
        if not slot:
            return result
        camouflage = slot.getItem()
        component = slot.getComponent()
        if camouflage:
            try:
                palette = camouflage.palettes[component.palette]
            except IndexError:
                palette = camouflage.palettes[0]

            weights = Math.Vector4(*[ (c >> 24) / 255.0 for c in palette ])
            if isDamaged:
                weights *= 0.1
            tiling = camouflage.tiling.get(vDesc.type.compactDescr)
            if tiling is None:
                tiling = vDesc.type.camouflage.tiling
            if tiling:
                try:
                    scale = camouflage.scales[component.patternSize]
                except IndexError:
                    scale = 0

                tiling = (tiling[0] * scale,
                 tiling[1] * scale,
                 tiling[2],
                 tiling[3])
            exclusionMap = vDesc.type.camouflage.exclusionMask
            compDesc = getattr(vDesc, descId, None)
            if compDesc is not None:
                coeff = compDesc.camouflage.tiling
                if coeff is not None:
                    if tiling is not None:
                        tiling = (tiling[0] * coeff[0],
                         tiling[1] * coeff[1],
                         tiling[2] + coeff[2],
                         tiling[3] + coeff[3])
                    else:
                        tiling = coeff
                if compDesc.camouflage.exclusionMask:
                    exclusionMap = compDesc.camouflage.exclusionMask
            result = CamoParams(camouflage.texture, exclusionMap or '', tiling, weights, palette[0], palette[1], palette[2], palette[3])
        return result


def getRepaint(outfit, containerId, vDesc):
    enabled = False
    quality = fading = 0.0
    overlapMetallic = overlapGloss = None
    nationID = vDesc.type.customizationNationID
    colorId = vDesc.type.baseColorID
    defaultColors = items.vehicles.g_cache.customization20().defaultColors
    defaultColor = defaultColors[nationID][colorId]
    mod = outfit.misc.slotFor(GUI_ITEM_TYPE.MODIFICATION).getItem()
    if mod:
        enabled = True
        quality = mod.modValue(ModificationType.PAINT_AGE, quality)
        fading = mod.modValue(ModificationType.PAINT_FADING, fading)
        overlapMetallic = mod.modValue(ModificationType.METALLIC, overlapMetallic)
        overlapGloss = mod.modValue(ModificationType.GLOSS, overlapGloss)
    container = outfit.getContainer(containerId)
    paintSlot = container.slotFor(GUI_ITEM_TYPE.PAINT)
    capacity = paintSlot.capacity()
    colors = [defaultColor] * capacity
    metallics = [overlapMetallic or _DEFAULT_METALLIC] * (capacity + 1)
    glosses = [overlapGloss or _DEFAULT_GLOSS] * (capacity + 1)
    for idx in range(capacity):
        paint = paintSlot.getItem(idx)
        if paint:
            enabled = True
            colors[idx] = paint.color
            metallics[idx] = overlapMetallic or paint.metallic
            glosses[idx] = overlapGloss or paint.gloss
        if not (containerId == TankPartIndexes.GUN and idx == C11N_MASK_REGION):
            colors[idx] = colors[0]
            metallics[idx] = overlapMetallic or metallics[0]
            glosses[idx] = overlapGloss or glosses[0]

    colors = tuple(colors)
    metallics = tuple(metallics)
    glosses = tuple(glosses)
    return RepaintParams(enabled, defaultColor, colors, metallics, glosses, fading, quality) if enabled else RepaintParams(enabled, defaultColor)
