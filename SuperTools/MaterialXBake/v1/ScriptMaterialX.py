import os,sys
import logging
log = logging.getLogger('MaterialXBakeNode')
try:
    import MaterialX as mx
except ImportError:
    log.error("Can`t find MaterialX -- %s"% sys.exc_info()[0])
try:
    from Katana import NodegraphAPI
except ImportError:
    print "Can`t find Katana"

ARNOLD_NODEDEFS=os.path.join(os.path.dirname(__file__), 'arnold', 'nodedefs.mtlx')

COLOR3 = ['out', 'out.r', 'out.g', 'out.b']
COLOR4 = ['out', 'out.r', 'out.g', 'out.b', 'out.a']
SWIZZLE_SUFFIX = ['.r', '.g', '.b', '.a', '.x', '.y', '.z']

def TraverseUpstreamNodes(asnode, sets):
    log.info("Traverse current node -%s"%asnode)
    up_nodes = getConnectedUpstreamNodes(asnode)
    for t_node in up_nodes:
        sets.append(t_node)
        TraverseUpstreamNodes(t_node, sets)

def getConnectedUpstreamNodes(node):
    """
    Get upstream nodes which connected to current node.
    """
    result_nodes = []
    inputports = node.getInputPorts()
    for i_port in inputports:
        port = i_port.getConnectedPort(0)
        if not port:
            continue
        shader_name = port.getNode()
        result_nodes.append(shader_name)
    return result_nodes

def isPortConnected(port):
    """
    Check out if this port connected with any other ports.
    """
    ports = port.getConnectedPorts()
    if ports:
        return True
    else:
        return False

def getConnectedNode(port):
    """
    Get the node which connected to the input port.
    """
    if isPortConnected(port):
        return port.getConnectedPort(0).getNode()
    else:
        return None

def isKatanaParamEnable(asnode, param_name):
    _enable = asnode.getParameter("parameters.%s.enable"%param_name).getValue(0)
    if _enable:
        return True
    else:
        return False

def getMaterialXParamsValue(asnode, param_name):
    """
    Get MaterialX Standard Value from ArnoldShadingNode.
    """
    def _getType(asnode, param_name):
        doc = mx.createDocument()
        mx.readFromXmlFile(doc, ARNOLD_NODEDEFS)

        input_type = asnode.getParameter('nodeType').getValue(0)
        # Traverse the document tree in depth-first order.
        return doc.getNodeDef(input_type).getInput(param_name).getType()
    param_type = asnode.getParameter("parameters.%s.value"%param_name).getType()
    input_type = _getType(asnode, param_name)
    # If parameter is katana type string
    if param_type == "string":
        return "string", asnode.getParameter("parameters.%s.value"%param_name).getValue(0)
    # If parameter is katana type number
    elif param_type == "number":
        if input_type == "integer":
            return "integer", asnode.getParameter("parameters.%s.value"%param_name).getValue(0)
        elif input_type == "boolean":
            if int(asnode.getParameter("parameters.%s.value"%param_name).getValue(0)):
                return "boolean", "true"
            else:
                return "boolean", "false"
        elif input_type == "float":
            return "float", asnode.getParameter("parameters.%s.value"%param_name).getValue(0)
    # If parameter is katana type numberArray
    elif param_type == "numberArray":
        # Find out the tuple type,color or vector?
        _size =  asnode.getParameter("parameters.%s.value"%param_name).getTupleSize()
        _tuple = []
        for i in range(0, _size):
            _tuple.append(asnode.getParameter("parameters.%s.value.i%i"%(param_name, i)).getValue(0))
        if input_type == "color2":
            return "color2", mx.Color2(_tuple[0], _tuple[1])
        elif input_type == "color3":
            return "color3", mx.Color3(_tuple[0], _tuple[1], _tuple[2])
        elif input_type == "color4":
            return "color4", mx.Color4(_tuple[0], _tuple[1], _tuple[2], _tuple[3])
        elif input_type == "vector2":
            return "vector2", mx.Vector2(_tuple[0], _tuple[1])
        elif input_type == "vector3":
            return "vector3", mx.Vector3(_tuple[0], _tuple[1], _tuple[2])
        elif input_type == "vector4":
            return "vector4", mx.Vector4(_tuple[0], _tuple[1], _tuple[2], _tuple[3])

def removeSwizzleSuffix(param_name):
    """
    Remove param subffix so that we could get it`s type for once.
    """
    suffix_list = SWIZZLE_SUFFIX
    for suffix in suffix_list:
        if param_name.endswith(suffix ):
            param_name = param_name[:-2]
    return param_name


def SetMaterialXShaderRefParams(mxnode, asnode):
    """
    Set Arnold Params to MaterialX ShaderRef Parameter.
    """
    _param_name_list = []
    for input_port in asnode.getInputPorts():
        param_name = removeSwizzleSuffix(input_port.getName())
        # To ignore some input ports like base_color,base_color.r etc.
        # Make sure every parameter loops just once.
        if param_name not in _param_name_list:
            _param_name_list.append(param_name)
        else:
            continue
        if isPortConnected(input_port):
            bind_input = mxnode.addBindInput(param_name)
            upstream_node = getConnectedNode(input_port)
            bind_input.setNodeGraphString("NodeGraph__"+upstream_node.getName())
            bind_input.setOutputString("out")
        else:
            # If katana param is not enabled, skip!
            print "bind_input:", param_name, isKatanaParamEnable(asnode, param_name)
            if not isKatanaParamEnable(asnode, param_name):
                continue
            _type, _value = getMaterialXParamsValue(asnode, param_name)
            bind_input = mxnode.addBindInput(param_name, _type)
            bind_input.setValue(_value)

def SetMaterialXNodeRefParams(mxnode, asnode):
    """
    Set Arnold Params to MaterialX NodeRef Parameter.
    """
    _param_name_list = []
    for input_port in asnode.getInputPorts():
        param_name = removeSwizzleSuffix(input_port.getName())
        # To ignore some input ports like base_color,base_color.r etc.
        # Make sure every parameter loops just once.
        if param_name not in _param_name_list:
            _param_name_list.append(param_name)
        else:
            continue
        if isPortConnected(input_port):
            upstream_node = getConnectedNode(asnode.getInputPort(param_name))
            mxnode.setConnectedNodeName(param_name, upstream_node.getName())
        else:
            # If katana param is not enabled, skip!
            if not isKatanaParamEnable(asnode, param_name):
                continue
            _type, _value = getMaterialXParamsValue(asnode, param_name)
            mxnode.setInputValue(param_name, _value, _type)


def buildMXMaterial(document, ktnnode):
    """
    Create MaterialX Material and and inside contents.
    """
    material_name = ktnnode.getName()
    mx_material = document.getMaterial("Material__"+material_name)
    if not mx_material:
        mx_material = document.addMaterial("Material__"+material_name)
    return mx_material

def buildMXShaderRef(document, asnode):
    material_name = asnode.getOutputPortByIndex(0).getConnectedPort(0).getNode().getName()
    material = document.getMaterial("Material__" + material_name)
    shader_ref_name = asnode.getName()
    shader_refinput_type = asnode.getParameter('nodeType').getValue(0)
    mx_shader_ref = material.getShaderRef("ShaderRef__"+shader_ref_name)    
    if not mx_shader_ref:
        mx_shader_ref = material.addShaderRef("ShaderRef__"+shader_ref_name, shader_refinput_type)
        #~ Set shaderref parameter
        SetMaterialXShaderRefParams(mx_shader_ref, asnode)
    return mx_shader_ref


def buildMXNodeGraph(document, asnode):
    """
    Create MaterialX NodeGraph and inside contents.
    """
    node_graph_name = asnode.getName()
    mx_node_graph = document.getNodeGraph("NodeGraph__"+node_graph_name)
    if not mx_node_graph:
        mx_node_graph = document.addNodeGraph("NodeGraph__"+node_graph_name)

        root_asnode_name = asnode.getName()
        root_asnode_type = asnode.getParameter('nodeType').getValue(0)
        root_asnode = mx_node_graph.addNode( root_asnode_type, name=root_asnode_name)
        SetMaterialXNodeRefParams(root_asnode, asnode)
        
        upstream_nodes = []
        TraverseUpstreamNodes(asnode, upstream_nodes)
        for next_node in upstream_nodes:
            next_asnode_name = next_node.getName()
            next_asnode_type = next_node.getParameter('nodeType').getValue(0)
            next_asnode = mx_node_graph.getNode( next_asnode_name )
            if not next_asnode:
                next_asnode = mx_node_graph.addNode( next_asnode_type, name=next_asnode_name)
                SetMaterialXNodeRefParams(next_asnode, next_node)
        output = mx_node_graph.addOutput('out')
        output.setConnectedNode(root_asnode)
    return mx_node_graph

def export(sets, saveTo):
    # Create a document.
    doc = mx.createDocument()
    # Include Arnold nodedefs.
    mx.prependXInclude(doc, ARNOLD_NODEDEFS)

    for look_name in sets:
        node_sets = sets[look_name]

        for node_set in node_sets:
            collection_node_name = node_set[0]
            network_material_node_name = node_set[1]
            # {nm_node} : NetworkMaterialNode
            nm_node = NodegraphAPI.GetNode(network_material_node_name)
            # The material node might be surafceShader or displacementShader
            # so we need to record it all.
            material_node_list = getConnectedUpstreamNodes(nm_node)
            # {as_node} : ArnoldShadingNode
            for as_node in material_node_list:
                mx_material = buildMXMaterial(doc, nm_node)
                mx_shader_ref = buildMXShaderRef(doc, as_node)
                input_port_list = as_node.getInputPorts()
                node_graph_node_list = []
                # Get nodeGraph root node list
                for input_port in input_port_list:
                    if isPortConnected(input_port):
                        node_graph_node = getConnectedNode(input_port)
                        if not node_graph_node in node_graph_node_list:
                            node_graph_node_list.append(node_graph_node)
                # Create nodeGraph node
                for node_graph_node in node_graph_node_list:
                    mx_node_graph = buildMXNodeGraph(doc,node_graph_node)

        # Create a look.
        look = doc.addLook(look_name)
        for node_set in node_sets:
            collection_node_name = node_set[0]
            network_material_node_name = node_set[1]

            # Create a collection.
            collection = doc.addCollection("Colloction__"+look_name+"_"+collection_node_name.replace("/","_"))
            # collection.addCollectionAdd("CollectionAdd__"+look_name+"_"+collection_node_name.replace("/","_"))
            collection.setIncludeGeom ("*"+collection_node_name)

            materialAssign = look.addMaterialAssign("MaterialAssign__"+look_name+"_"+collection_node_name.replace("/","_"))
            materialAssign.setCollection(collection)
            materialAssign.setMaterial("Material__"+network_material_node_name)

    mx.writeToXmlFile(doc, saveTo)