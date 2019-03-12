from Katana import Nodes3DAPI, QtCore, QtGui, UI4, QT4Widgets, QT4FormWidgets

import ScriptActions as SA

import logging
log = logging.getLogger('MaterialXEditEditor')

from MXQtGui import MaterialXEditor

# Class Definitions -----------------------------------------------------------

class MaterialXEditEditor(QtGui.QWidget):
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

        materialNode = SA.GetRefNode(self.__node, 'material')
        shaderParameter = materialNode.getParameter('shaders.parameters')
        # Get the SuperTool's parameters
        saveAsParameter = self.__node.getParameter('saveAs')
        materialParameter = self.__node.getParameter('material')
        saveButtonParameter = self.__node.getParameter("save")

        CreateParameterPolicy = UI4.FormMaster.CreateParameterPolicy

        self.__saveAsParameterPolicy = CreateParameterPolicy(
            None, saveAsParameter)
        self.__materialParameterPolicy = CreateParameterPolicy(
            None, materialParameter)
        self.__shaderParameterPolicy = CreateParameterPolicy(
            None, shaderParameter)

        self.__saveAsParameterPolicy.addCallback(
            self.saveAsChangedCallback)
        self.__materialParameterPolicy.addCallback(
            self.materialChangedCallback)
        self.__saveButtonParameterPolicy = CreateParameterPolicy(
                None, saveButtonParameter)

        WidgetFactory = UI4.FormMaster.KatanaFactory.ParameterWidgetFactory
        saveAsParameterWidget = WidgetFactory.buildWidget(
            self, self.__saveAsParameterPolicy)
        materialParameterWidget = WidgetFactory.buildWidget(
            self, self.__materialParameterPolicy)
        shaderParameterWidget = WidgetFactory.buildWidget(
            self, self.__shaderParameterPolicy)
        saveButtonParameterWidget = WidgetFactory.buildWidget(
            self, self.__saveButtonParameterPolicy)

        editorWidget = MaterialXEditor(None)
        editorWidget.setFixedHeight(150)
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(saveAsParameterWidget)
        mainLayout.addWidget(materialParameterWidget)
        mainLayout.addWidget(shaderParameterWidget)
        mainLayout.addWidget(editorWidget)
        mainLayout.addWidget(saveButtonParameterWidget)

        # Apply the layout to the widget
        self.setLayout(mainLayout)

    # Public Functions --------------------------------------------------------
    def saveAsChangedCallback(self, *args, **kwds):
        materialParameter = self.__node.getParameter('saveAs')
        filenameParameter = SA.GetRefNode(self.__node, 'material').getParameter('shaders.parameters.filename')
        orig_path = ""
        if filenameParameter:
            orig_path = filenameParameter.getChild("value").getValue(0)
        save_path = materialParameter.getValue(0)
        from shutil import copyfile
        if orig_path and save_path:
            copyfile(orig_path, save_path)
            filenameParameter.getChild("enable").setValue(True, 0)
            filenameParameter.getChild("value").setValue(save_path, 0)
        return 1
    def materialChangedCallback(self, *args, **kwds):
        materialNode = SA.GetRefNode(self.__node, 'material')
        materialParameter = self.__node.getParameter('material')
        materialNode.getParameter('edit.location').setValue(materialParameter.getValue(0), 0)
        return 1