# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/color_components.py
from __future__ import absolute_import
import CGF
import GenericComponents
import Math
from cgf_script.registration import registerComponent, ComponentProperty

@registerComponent
class ColorComponent(object):
    group = 'UI'
    editorTitle = 'Color Component'
    domain = CGF.Domain.ClientEditor
    model = ComponentProperty(type=CGF.PropertyType.Link, editorName='model', value=GenericComponents.DynamicModelComponent)
    colorParamName = ComponentProperty(type=CGF.PropertyType.String, editorName='colorParamName', value='g_color')
    color = ComponentProperty(type=CGF.PropertyType.Vector4, value=Math.Vector4(1, 0, 0, 0), editorName='color')

    def __init__(self):
        super(ColorComponent, self).__init__()
        self.currentColor = self.color
        self.currentColorParamName = self.colorParamName
        self.currentModel = self.model


class ColorSystem(CGF.System):
    ColorActivated = CGF.ActivateReaction(CGF.ReactRw(ColorComponent))
    ColorIterate = CGF.IterateReaction(CGF.ActiveOnly, CGF.Rw(ColorComponent))
    ModelAccess = CGF.AccessReaction(CGF.Rw(GenericComponents.DynamicModelComponent))
    Reactions = CGF.Reactions(ColorIterate, ColorActivated, ModelAccess)

    def update(self):
        modelAccess = self.reaction(self.ModelAccess)
        for colorComponent in self.reaction(self.ColorActivated):
            self.handleColorComponentAdded(colorComponent, modelAccess)

        for colorComponent in self.reaction(self.ColorIterate):
            self.processingHandler(colorComponent, modelAccess)

    def handleColorComponentAdded(self, colorComponent, modelAccess):
        model = modelAccess.find(colorComponent.model)
        model.setMaterialParameterVector4(colorComponent.colorParamName, colorComponent.color)
        colorComponent.currentColor = colorComponent.color
        colorComponent.currentColorParamName = colorComponent.currentColorParamName
        colorComponent.currentModel = colorComponent.model

    def processingHandler(self, colorComponent, modelAccess):
        if colorComponent.currentColor != colorComponent.color or colorComponent.currentModel != colorComponent.model or colorComponent.currentColorParamName != colorComponent.colorParamName:
            model = modelAccess.find(colorComponent.model)
            model.setMaterialParameterVector4(colorComponent.colorParamName, colorComponent.color)
            colorComponent.currentColor = colorComponent.color
            colorComponent.currentColorParamName = colorComponent.colorParamName
            colorComponent.currentModel = colorComponent.model


def rgbaColorToHexARGB(color):
    r = int(color[0])
    g = int(color[1])
    b = int(color[2])
    a = int(color[3])
    return a << 24 | r << 16 | g << 8 | b
