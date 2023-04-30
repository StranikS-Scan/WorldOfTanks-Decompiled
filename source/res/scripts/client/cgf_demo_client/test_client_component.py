# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_demo_client/test_client_component.py
import logging
import GenericComponents
import CGF
from cgf_demo.demo_category import DEMO_CATEGORY
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerComponent
_logger = logging.getLogger(__name__)

@registerComponent
class ClientTestComponent(object):
    category = DEMO_CATEGORY
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    stringList = ComponentProperty(type=CGFMetaTypes.STRING_LIST, editorName='String List', value=('Test1', 'Test2'))
    intList = ComponentProperty(type=CGFMetaTypes.INT_LIST, editorName='Int List', value=(1, 2, 3))
    floatList = ComponentProperty(type=CGFMetaTypes.FLOAT_LIST, editorName='Float List', value=(4.0, 5.0, 6.0, 7.0))
    double = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='Double', value=55.0)
    integer = ComponentProperty(type=CGFMetaTypes.INT, editorName='Integer', value=777)
    string = ComponentProperty(type=CGFMetaTypes.STRING, editorName='String', value='Tiger')
    transformLink = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Link to Transform', value=GenericComponents.TransformComponent)

    def __init__(self):
        super(ClientTestComponent, self).__init__()
        _logger.debug('ClientTestComponent stringList = %s', self.stringList)
        _logger.debug('ClientTestComponent double = %f', self.double)
        _logger.debug('ClientTestComponent integer = %d', self.integer)
        _logger.debug('ClientTestComponent string = %s', self.string)
        if self.transformLink is not None:
            _logger.debug('ClientTestComponent transform from link =\n%s', self.transformLink().worldTransform)
        return
