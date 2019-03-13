import logging
import textwrap
log = logging.getLogger('MaterialXEditNode')

from Katana import NodegraphAPI, Nodes3DAPI, AssetAPI
from Katana import QtCore, QtGui
import ScriptActions as SA
from Katana import DrawingModule

class MaterialXEditNode(NodegraphAPI.SuperTool):
    def __init__(self):
        self.hideNodegraphGroupControls()
        # self.setContentLocked(True)

        self.addInputPort("input")

        self.addOutputPort("out")

        ######################################################################
        # Create parameters specific to our SuperTool.
        #
        # See _ExtraHints at the bottom of this file to see how we specify how
        # these parameters should be displayed in the UI by specifying built-in
        # widgets.
        ######################################################################
        self.getParameters().createChildString('saveAs', '')
        self.getParameters().createChildString('material', '')
        self.getParameters().createChildString('save', '')

        # Material Node
        self.material_node = NodegraphAPI.CreateNode('Material', self)
        self.material_node.getParameter('name').setValue("MaterialXEditNode", 0)
        self.material_node.getParameter('action').setValue("edit material",0)

        # We don't expose the parameters in the SuperTool's UI but you can
        # see them if you were to run something similar to:
        #
        # NodegraphAPI.GetNode('<SuperToolNodeName>').getParameters().getXML()
        SA.AddNodeReferenceParam(self, 'node_material', self.material_node)

        # Connect the internal node network together and then connect it to the
        # output port of the SuperTool.
        supertools_send = self.getSendPort("input")
        material_input = self.material_node.getInputPort("in")
        material_input.connect(supertools_send)

        material_output = self.material_node.getOutputPortByIndex(0)
        supertools_return = self.getReturnPort("out")
        supertools_return.connect(material_output)

        # Position the nodes in the internal node network so it looks a bit
        # more organised.
        NodegraphAPI.SetNodePosition(self.material_node, (100, 0))

    def addParameterHints(self, attrName, inputDict):
        """
        This function will be called by Katana to allow you to provide hints
        to the UI to change how parameters are displayed.
        """
        inputDict.update(_ExtraHints.get(attrName, {}))

    def save(self):
        pass

_ExtraHints = {
    'MaterialXEdit.saveAs': {
        'help':
            """
            The path we copy origin mtlx file to and edit.
            """,
    },
    'MaterialXEdit.material': {
        'widget': 'scenegraphLocation',
        'help':
            """
            Arnold operator materialx node scenegraphLocation.
            """,
    },
    'MaterialXEdit.save': {
        'widget': 'scriptButton',
        'scriptText': 'node.save()',
        'buttonText': 'Save',
        'help':
            """
            Save edit metarialx file!
            Call MaterialXEdit.save() to run it with script!.
            """,
    },
}