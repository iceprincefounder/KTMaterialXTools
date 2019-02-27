import logging
import textwrap
log = logging.getLogger('MaterialXBakeNode')

from Katana import NodegraphAPI, Nodes3DAPI, AssetAPI
from Katana import QtCore, QtGui
import ScriptActions as SA
from Katana import DrawingModule

class MaterialXBakeNode(NodegraphAPI.SuperTool):
    def __init__(self):
        self.hideNodegraphGroupControls()
        # self.setContentLocked(True)

        self.addInputPort("original")
        self.addInputPort("default")

        self.addOutputPort("output")

        ######################################################################
        # Create parameters specific to our SuperTool.
        #
        # See _ExtraHints at the bottom of this file to see how we specify how
        # these parameters should be displayed in the UI by specifying built-in
        # widgets.
        ######################################################################
        self.getParameters().createChildStringArray("rootLocations",1)
        self.getParameters().createChildGroup('passes', 1)
        self.getParameters().createChildString('saveTo', '')
        self.getParameters().createChildString('writeMaterialxOut', '')

        # Switch Node
        self.switch_node = NodegraphAPI.CreateNode('Switch', self)
        self.switch_node.setName("LookSwitch")
        self.switch_node.addInputPort("original")
        self.switch_node.addInputPort("default")

        self.opScript_node = NodegraphAPI.CreateNode('OpScript', self)
        self.opScript_node.setName("MaterialAssignedAttr")
        self.opScript_node.getParameter('CEL').setExpression(
            """'/root/world//*{ attr( "type" ) == "subdmesh"  or attr( "type" ) == "polymesh"}'""")
        self.opScript_node.getParameter('script.lua').setValue(self.__getMaterialAssignedOpScript(), 0)

        self.merge_node = NodegraphAPI.CreateNode('Merge', self)
        self.merge_node.addInputPort('in')
        self.merge_node.setName('MaterialXOutput')

        # We don't expose the parameters in the SuperTool's UI but you can
        # see them if you were to run something similar to:
        #
        # NodegraphAPI.GetNode('<SuperToolNodeName>').getParameters().getXML()
        SA.AddNodeReferenceParam(self, 'node_switch', self.switch_node)
        SA.AddNodeReferenceParam(self, 'node_opScript', self.opScript_node)
        SA.AddNodeReferenceParam(self, 'node_merge', self.merge_node)

        # Connect the internal node network together and then connect it to the
        # output port of the SuperTool.
        supertools_inputport1 = self.getSendPort("original")
        supertools_inputport2 = self.getSendPort("default")
        switch_node_input1 = self.switch_node.getInputPort("original")
        switch_node_input2 = self.switch_node.getInputPort("default")
        switch_node_input1.connect(supertools_inputport1)
        switch_node_input2.connect(supertools_inputport2)


        switch_node_output = self.switch_node.getOutputPortByIndex(0)
        opScript_node_input = self.opScript_node.getInputPortByIndex(0)
        switch_node_output.connect(opScript_node_input)

        opScript_node_output = self.opScript_node.getOutputPortByIndex(0)
        merge_node_input = self.merge_node.getInputPortByIndex(0)
        opScript_node_output.connect(merge_node_input)

        supertools_return = self.getReturnPort("output")
        merge_node_output = self.merge_node.getOutputPortByIndex(0)
        supertools_return.connect(merge_node_output)

        # Position the nodes in the internal node network so it looks a bit
        # more organised.
        NodegraphAPI.SetNodePosition(self.switch_node, (0, 0))
        NodegraphAPI.SetNodePosition(self.opScript_node, (0, -50))
        NodegraphAPI.SetNodePosition(self.merge_node, (0, -120))

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
            -- MaterialAssigned
            -- Copy attribute from "materialAssgin" to 
            -- "geometry.arbitrary.materialAssigned.value"
            local materialAssign=Interface.GetGlobalAttr("materialAssign")
            local materialAssignValue = nil
            if materialAssign then
                materialAssignValue=materialAssign:getValue()
            end
            local attributeScope= "geometry.arbitrary.materialAssigned.scope"
            local attributeIT = "geometry.arbitrary.materialAssigned.inputType"
            local attributeOT = "geometry.arbitrary.materialAssigned.outputType"
            local attributeName = "geometry.arbitrary.materialAssigned.value"
            local attributeValue = StringAttribute("")
            if materialAssignValue then
                attributeValue = StringAttribute(materialAssignValue:match("^.+/(.+)$"))
            end
            Interface.SetAttr(attributeScope, StringAttribute("primitive"))
            Interface.SetAttr(attributeIT, StringAttribute("string"))
            Interface.SetAttr(attributeOT, StringAttribute("string"))
            Interface.SetAttr(attributeName, attributeValue)
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

        widget.setWindowTitle("MaterialXBake")
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
    'MaterialXBake.rootLocations': {
        'widget': 'scenegraphLocationArray',
        'help':
            """
            The root of scene graph location that MaterialX collation would ignore 
            and mark the rest location.
            """,
    },
    'MaterialXBake.passes': {
        'widget': 'group',
        'open': 'True',
        'help':
            """
            Different look passes name.
            """,
    },
    'MaterialXBake.saveTo': {
        'widget': 'assetIdOutput',
        'sequenceListing' : False,
        'fileTypes':'mtlx',
        'help':
            """
            Specify path to save MaterialX file.
            """,
    },
    'MaterialXBake.writeMaterialxOut': {
        'widget': 'scriptButton',
        'scriptText': 'node.bake();node.widget()',
        'buttonText': 'Write MaterialX Out',
        'help':
            """
            Write MaterialX out,
            Call MaterialXBake.bake() to run it with script!.
            """,
    },
}