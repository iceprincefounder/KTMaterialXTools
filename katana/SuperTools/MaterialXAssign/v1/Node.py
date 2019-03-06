import logging
import textwrap
log = logging.getLogger('MaterialXAssignNode')

from Katana import NodegraphAPI, Nodes3DAPI, AssetAPI
from Katana import QtCore, QtGui
import ScriptActions as SA
from Katana import DrawingModule

class MaterialXAssignNode(NodegraphAPI.SuperTool):
    def __init__(self):
        self.hideNodegraphGroupControls()
        self.setContentLocked(True)

        self.addInputPort("input")

        self.addOutputPort("out")

        ######################################################################
        # Create parameters specific to our SuperTool.
        #
        # See _ExtraHints at the bottom of this file to see how we specify how
        # these parameters should be displayed in the UI by specifying built-in
        # widgets.
        ######################################################################
        self.getParameters().createChildString('name', 'NM_materialx')
        self.getParameters().createChildGroup('arnoldOperator', 4)
        self.getParameter('arnoldOperator').createChildString('selection', '*')
        self.getParameter('arnoldOperator').createChildString('look', 'default')
        self.getParameter('arnoldOperator').createChildString('filename', '')
        self.getParameter('arnoldOperator').createChildString('search_path', '')

        # ArnoldShadingNode materialx
        self.arnold_shading_node = NodegraphAPI.CreateNode('ArnoldShadingNode', self)
        self.arnold_shading_node.getParameter('name').setValue("materialx", 0)
        self.arnold_shading_node.getParameter('nodeType').setValue("materialx", 0)
        self.arnold_shading_node.checkDynamicParameters()
        selection_param = self.arnold_shading_node.getParameter('parameters.selection')
        look_param = self.arnold_shading_node.getParameter('parameters.look')
        filename_param = self.arnold_shading_node.getParameter('parameters.filename')
        search_param = self.arnold_shading_node.getParameter('parameters.search_path')
        hints_list = {
            "selection":{'dstName':'selection', 'dstPage':''},
            "look":{'dstName':'look', 'dstPage':''},
            "filename":{'dstName':'filename', 'dstPage':''},
            "search_path":{'dstName':'search_path', 'dstPage':''},
        }
        for param_name in hints_list:
            param = self.arnold_shading_node.\
                getParameter('parameters.%s'%param_name)
            hintsParam = param.getChild('hints')
            if hintsParam:
                hintsParam.setValue('', 0)
                param.deleteChild(hintsParam)
            hints = hints_list[param_name]
            hintsParam = param.createChildString('hints', '')
            hintsParam.setValue(repr(hints), 0)
        # NetworkMaterial Node
        self.network_material_node = NodegraphAPI.CreateNode('NetworkMaterial', self)
        self.network_material_node.getParameter('name').setValue("NM_materialx", 0)
        self.network_material_node.getParameter('namespace').setValue("materialx", 0)
        self.network_material_node.addInputPort("arnoldOperator")

        self.dot_node = NodegraphAPI.CreateNode('Dot', self)

        self.merge_node = NodegraphAPI.CreateNode('Merge', self)
        self.merge_node.addInputPort('in')
        self.merge_node.addInputPort('operator')
        self.merge_node.setName('MergeArnoldOperator')

        self.ags_node = NodegraphAPI.CreateNode('ArnoldGlobalSettings', self)
        self.ags_node.setName("MaterialXSetAttr")

        self.opScript_node = NodegraphAPI.CreateNode('OpScript', self)
        self.opScript_node.setName("OpScriptArnoldOperatorSet")
        self.opScript_node.getParameter('CEL').setExpression("""'/root/materials/materialx'""")
        self.opScript_node.getParameter('script.lua').setValue(self.__getMaterialAssignedOpScript(), 0)


        # We don't expose the parameters in the SuperTool's UI but you can
        # see them if you were to run something similar to:
        #
        # NodegraphAPI.GetNode('<SuperToolNodeName>').getParameters().getXML()
        SA.AddNodeReferenceParam(self, 'node_arnoldGlobalSettings', self.ags_node)
        SA.AddNodeReferenceParam(self, 'node_opScript', self.opScript_node)
        SA.AddNodeReferenceParam(self, 'node_networkMaterial', self.network_material_node)
        SA.AddNodeReferenceParam(self, 'node_materialx', self.arnold_shading_node)

        # Connect the internal node network together and then connect it to the
        # output port of the SuperTool.
        supertools_send = self.getSendPort("input")
        dot_input = self.dot_node.getInputPort("input")
        dot_input.connect(supertools_send)

        dot_output = self.dot_node.getOutputPortByIndex(0)
        merge_node_input = self.merge_node.getInputPort("in")
        merge_node_input.connect(dot_output)

        arnold_shading_node_output = self.arnold_shading_node.getOutputPortByIndex(0)
        network_material_input = self.network_material_node.getInputPort("arnoldOperator")
        network_material_input.connect(arnold_shading_node_output)

        network_material_output = self.network_material_node.getOutputPortByIndex(0)
        merge_node_operator = self.merge_node.getInputPort("operator")
        merge_node_operator.connect(network_material_output)

        merge_node_output = self.merge_node.getOutputPortByIndex(0)
        ags_node_input = self.ags_node.getInputPortByIndex(0)
        ags_node_input.connect(merge_node_output)

        ags_node_output = self.ags_node.getOutputPortByIndex(0)
        opScript_node_input = self.opScript_node.getInputPortByIndex(0)
        opScript_node_input.connect(ags_node_output)

        opScript_node_output = self.opScript_node.getOutputPortByIndex(0)
        supertools_return = self.getReturnPort("out")
        supertools_return.connect(opScript_node_output)

        # Position the nodes in the internal node network so it looks a bit
        # more organised.
        NodegraphAPI.SetNodePosition(self.arnold_shading_node, (100, 0))
        NodegraphAPI.SetNodePosition(self.network_material_node, (100, -50))
        NodegraphAPI.SetNodePosition(self.dot_node, (-100, -50))
        NodegraphAPI.SetNodePosition(self.merge_node, (0, -100))
        NodegraphAPI.SetNodePosition(self.ags_node, (0, -150))
        NodegraphAPI.SetNodePosition(self.opScript_node, (30, -200))

    def addParameterHints(self, attrName, inputDict):
        """
        This function will be called by Katana to allow you to provide hints
        to the UI to change how parameters are displayed.
        """
        inputDict.update(_ExtraHints.get(attrName, {}))

    @classmethod
    def __getMaterialAssignedOpScript(self):
        return textwrap.dedent(
            """
            -- MaterialXAssigned
            -- Copy attribute from "materialAssgin" to 
            -- "geometry.arbitrary.materialAssigned.value"
            Interface.SetAttr("arnoldMaterialX.name", StringAttribute("Arnold Operator MaterialX"))
            Interface.SetAttr("arnoldMaterialX.version", StringAttribute("v1.36.1"))
            Interface.SetAttr("arnoldMaterialX.toolsets", StringAttribute("KTMaterialXTools"))
            """).strip()

    def widget(self):

        layoutsMenus = [x for x in QtGui.qApp.topLevelWidgets() if type(x).__name__ == 'LayoutsMenu']
        KatanaWindow = layoutsMenus[0].parent().parent()

        saveTo = self.getParameter('saveTo').getValue(0)


        widget  = QtGui.QDialog(parent=KatanaWindow)
        title_layout = QtGui.QVBoxLayout()
        button_layout = QtGui.QHBoxLayout()
        title = QtGui.QLabel()
        button = QtGui.QPushButton()
        font = QtGui.QFont()
        font.setPixelSize(16)

        if saveTo:
            title.setText("MaterialX baking succeeded!")
        else:
            title.setText("Please enter the saving path!")
        title.setFont(font)
        title.setAlignment(QtCore.Qt.AlignHCenter)
        button.setText("Confirm!")
        button.clicked.connect(widget.close)
        button.setFixedHeight(30)

        title_layout.addStretch()
        title_layout.addWidget(title)
        title_layout.addStretch()
        button_layout.addStretch()
        button_layout.addWidget(button)
        button_layout.addStretch()

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addLayout(title_layout)
        mainLayout.addLayout(button_layout)

        widget.setWindowTitle("MaterialXAssign")
        widget.setLayout(mainLayout)
        widget.setFixedHeight(130)
        widget.show()

    def bake(self):
        import ScriptMaterialX as MateX
        reload(MateX)
        switch_node = SA.GetRefNode(self, 'switch')
        merge_node = SA.GetRefNode(self, 'merge')
        def walkProducer(producer, callback, location_types=[]):
           child = producer.getFirstChild()
           while child:
               walkProducer(child, callback, location_types)
               child = child.getNextSibling()
           if producer.getType() in location_types:
               fullLocation = producer.getFullName()
               callback.append(fullLocation)
        def makeCollctions(producer, callback, collations):
            for path in callback:
                proc = producer.getProducerByPath(path)
                attr=proc.getAttribute("geometry.arbitrary.materialAssigned.value")
                temp_map = {}
                temp_map["material"] = attr.getValue()
                temp_map["collction"] = path
                collations.append(temp_map)


        # Get attribute rootLocations.
        rootLocationsParameters = self.getParameter('rootLocations').getChildren()
        rootLocations = []
        for rootLocationsParameter in rootLocationsParameters:
            rootLocations.append(rootLocationsParameter.getValue(0))
        rootLocations = sorted(rootLocations , key = len)


        # Get attribute saveTo.
        saveToParameter = self.getParameter('saveTo')
        saveTo = saveToParameter.getValue(0)

        # If saveTo is None, stop at first time here
        if not saveTo:
            log.warning("Parameter saveTo is empty, please enter the specify path!")
            return 


        children = self.getParameter('passes').getChildren()
        look_set = {}
        for child in children:
            look_name = child.getValue(0)

            index = switch_node.getInputPort(child.getName()).getIndex()
            switch_node.getParameter('in').setValue(index, 0)
            producer = Nodes3DAPI.GetRenderProducer(merge_node, 0, False, 0)

            callback = []
            collations = []
            location_types = ["subdmesh", "polymesh"]
            walkProducer(producer, callback, location_types)
            makeCollctions(producer, callback, collations)
            assignment_set = []
            for MC in collations:
                material_name = MC["material"]
                collation_path = MC["collction"]
                collation_name = collation_path
                for prefix in rootLocations:
                    if collation_path.startswith(prefix):
                        collation_name = collation_path[len(prefix):]
                assignment_set.append( (collation_name, material_name) )

            if assignment_set:
                look_set[look_name] = assignment_set

        MateX.export(look_set,saveTo)
        log.info("MaterialX file save to %s"%saveTo)
        # Set Switch back
        switch_node.getParameter('in').setValue(0, 0)

_ExtraHints = {
    'MaterialXAssign.name': {
        'help':
            """
            The root of scene graph location that MaterialX collation would ignore 
            and mark the rest location.
            """,
    },
    'MaterialXAssign.arnoldOperator': {
        'widget': 'group',
        'open': 'True',
        'help':
            """
            """,
    },
    'MaterialXAssign.arnoldOperator.selection': {
        'help':
            """
            Specify path to save MaterialX file.
            """,
    },
    'MaterialXAssign.arnoldOperator.look': {
        'help':
            """
            """,
    },
    'MaterialXAssign.arnoldOperator.filename': {
        'widget': 'assetIdInput',
        'sequenceListing' : False,
        'fileTypes':'mtlx',
        'help':
            """
            Specify path to save MaterialX file.
            """,
    },
    'MaterialXAssign.arnoldOperator.search_path': {
        'help':
            """
            """,
    },
}