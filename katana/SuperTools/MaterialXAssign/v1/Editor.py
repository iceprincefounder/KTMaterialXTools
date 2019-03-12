from Katana import Nodes3DAPI, NodegraphAPI, QtCore, QtGui, UI4, QT4Widgets, QT4FormWidgets

import ScriptActions as SA

import logging
log = logging.getLogger('MaterialXAssignEditor')

# Class Definitions -----------------------------------------------------------

class MaterialXAssignEditor(QtGui.QWidget):
    """
    Example of a Super Tool editing widget that displays:
        - Its own parameters.
        - Parameters from node's in the SuperTool's internal node network.
        - Custom Qt Widgets.
    """

    # Initializer -------------------------------------------------------------

    def __init__(self, parent, node):
        """
        Initializes an instance of the class.
        """
        QtGui.QWidget.__init__(self, parent)

        self.__node = node

        # Get the SuperTool's parameters
        nameParameter = self.__node.getParameter('name')
        arnoldOperatorParameter = self.__node.getParameter('arnoldOperator')
        selectionParameter = self.__node.getParameter('arnoldOperator.selection')
        lookParameter = self.__node.getParameter('arnoldOperator.look')
        filenameParameter = self.__node.getParameter('arnoldOperator.filename')
        searchParameter = self.__node.getParameter('arnoldOperator.search_path')

        CreateParameterPolicy = UI4.FormMaster.CreateParameterPolicy

        self.__nameParameterPolicy = CreateParameterPolicy(
            None, nameParameter)
        self.__arnoldOperatorParameterPolicy = CreateParameterPolicy(
            None, arnoldOperatorParameter)
        self.__selectionParameterPolicy = CreateParameterPolicy(
            None, selectionParameter)
        self.__lookParameterPolicy = CreateParameterPolicy(
            None, lookParameter)
        self.__filenameParameterPolicy = CreateParameterPolicy(
            None, filenameParameter)
        self.__searchParameterPolicy = CreateParameterPolicy(
            None, searchParameter)

        self.__nameParameterPolicy.addCallback(
            self.nameChangedCallback)
        self.__selectionParameterPolicy.addCallback(
            self.selectionChangedCallback)
        self.__lookParameterPolicy.addCallback(
            self.lookChangedCallback)
        self.__filenameParameterPolicy.addCallback(
            self.filenameChangedCallback)
        self.__searchParameterPolicy.addCallback(
            self.searchChangedCallback)

        WidgetFactory = UI4.FormMaster.KatanaFactory.ParameterWidgetFactory
        nameParameterWidget = WidgetFactory.buildWidget(
            self, self.__nameParameterPolicy)
        arnoldOperatorWidget = WidgetFactory.buildWidget(
            self, self.__arnoldOperatorParameterPolicy)
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(nameParameterWidget)
        mainLayout.addWidget(arnoldOperatorWidget)

        # Apply the layout to the widget
        self.setLayout(mainLayout)

    # Public Functions --------------------------------------------------------
    def nameChangedCallback(self, *args, **kwds):
        nameParameter = self.__node.getParameter('name')
        nm_node = SA.GetRefNode(self.__node, 'networkMaterial')
        nm_node.getParameter('name').setValue(nameParameter.getValue(0), 0)

        Producer = Nodes3DAPI.GetRenderProducer(self.__node, 0, False, 0)
        callback = []
        location = "/root/materials/materialx"
        proc = Producer.getProducerByPath(location)
        SA.WalkProducer(proc, callback, ["material"])
        new_location = ""
        for path in callback:
            if new_location:
                new_location = new_location + "|" + path
            else:
                # The first path
                new_location = path
        attr_node = SA.GetRefNode(self.__node, 'arnoldGlobalSettings')
        attr_node.getParameter('args.arnoldGlobalStatements.operators.enable').setValue(True, 0)
        param = attr_node.getParameter('args.arnoldGlobalStatements.operators.value')
        operators = param.getValue(0)
        for operator_path in operators.split("|"):
            # if operator_path under '/root/materials/materialx', skip!
            if operator_path.find(location) >= 0:
                continue
            if operator_path in callback:
                continue
            # if operator_path is "", skip!
            if operator_path == "":
                continue
            new_location = new_location + "|" + operator_path
        param.setValue(new_location, 0)
        return 1

    def selectionChangedCallback(self, *args, **kwds):
        selectionParameter = self.__node.getParameter('arnoldOperator.selection')
        asn_node = SA.GetRefNode(self.__node, 'materialx')
        asn_node.checkDynamicParameters()
        asn_node.getParameter('parameters.selection.enable').setValue(True, 0)
        asn_node.getParameter('parameters.selection.value').setValue(selectionParameter.getValue(0), 0)
        return 1

    def lookChangedCallback(self, *args, **kwds):
        lookParameter = self.__node.getParameter('arnoldOperator.look')
        asn_node = SA.GetRefNode(self.__node, 'materialx')
        asn_node.checkDynamicParameters()
        asn_node.getParameter('parameters.look.enable').setValue(True, 0)
        asn_node.getParameter('parameters.look.value').setValue(lookParameter.getValue(0), 0)
        return 1

    def filenameChangedCallback(self, *args, **kwds):
        filenameParameter = self.__node.getParameter('arnoldOperator.filename')
        asn_node = SA.GetRefNode(self.__node, 'materialx')
        asn_node.checkDynamicParameters()
        asn_node.getParameter('parameters.filename.enable').setValue(True, 0)
        asn_node.getParameter('parameters.filename.value').setValue(filenameParameter.getValue(0), 0)
        return 1

    def searchChangedCallback(self, *args, **kwds):
        searchParameter = self.__node.getParameter('arnoldOperator.search_path')
        asn_node = SA.GetRefNode(self.__node, 'materialx')
        asn_node.checkDynamicParameters()
        asn_node.getParameter('parameters.search_path.enable').setValue(True, 0)
        asn_node.getParameter('parameters.search_path.value').setValue(searchParameter.getValue(0), 0)
        return 1