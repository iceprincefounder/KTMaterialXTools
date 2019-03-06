#!/usr/bin/python


import os, math
VECTOR2 = ['x', 'y']
VECTOR3 = ['x', 'y', 'z']
COLOR3 = ['r', 'g', 'b']
COLOR4 = ['r', 'g', 'b', 'a']
SWIZZLE_SUFFIX = ['r', 'g', 'b', 'a', 'x', 'y', 'z']
OUT = ['out']
OUT_XY = ['out', 'out.x', 'out.y']
OUT_XYZ= ['out', 'out.x', 'out.y', 'out.z']
OUT_RGB = ['out', 'out.r', 'out.g', 'out.b']
OUT_RGBA = ['out', 'out.r', 'out.g', 'out.b', 'out.a']

def removeSwizzleSuffix(param_name):
    """
    Remove param subffix so that we could get it`s type for once.
    """
    if param_name.find(".") < 0:
        pass
    else:
        param_name = param_name.split(".")[0]
    return param_name

def getParamsType(asnode, param_name):
    param = asnode.getParameter("parameters.%s.value"%param_name)
    ktn_type = param.getType()
    if   ktn_type == "number":
        print param_name, "float/boolean/integer", param.getValue(0)
    elif ktn_type == "string":
        print param_name, "string", param.getValue(0)
    elif ktn_type == "numberArray":
        print param_name, "color/vector",
        for child in param.getChildren():
            print child.getName()
    else:
        pass


def createMtoAArnoldShadingNodes():
    def getAllMtoAArnoldShadingTypes():
        import RenderingAPI
        result = []
        # Obtain a list of names of available shaders from the renderer info plug-in
        renderer = RenderingAPI.RenderPlugins.GetDefaultRendererPluginName()
        rendererInfoPlugin = RenderingAPI.RenderPlugins.GetInfoPlugin(renderer)
        shaderType = RenderingAPI.RendererInfo.kRendererObjectTypeShader
        nodeTypes = rendererInfoPlugin.getRendererObjectNames(shaderType)

        for node_type in nodeTypes:
            if node_type.startswith("Maya") or node_type.startswith("Mtoa"):
                result.append(node_type)
        return result    

    from Katana import NodegraphAPI
    shader_type_list = getAllMtoAArnoldShadingTypes()
    result = []
    i = 0
    for shader_type in shader_type_list:    
        as_node = NodegraphAPI.GetNode(shader_type)

        if not as_node:
            as_node = NodegraphAPI.CreateNode('ArnoldShadingNode', NodegraphAPI.GetRootNode())
            width = 5
            NodegraphAPI.SetNodePosition(as_node, (150*math.floor(i/width), -50*(i%width)))
            i += 1

        as_node.getParameter('nodeType').setValue(shader_type, 0)
        as_node.checkDynamicParameters()
        as_node.getParameter('name').setValue(shader_type, 0)

        result.append(as_node)
    return result

def createLCAArnoldShadingNodes():
    def getAllLCAArnoldShadingTypes():
        import RenderingAPI
        result = []
        # Obtain a list of names of available shaders from the renderer info plug-in
        renderer = RenderingAPI.RenderPlugins.GetDefaultRendererPluginName()
        rendererInfoPlugin = RenderingAPI.RenderPlugins.GetInfoPlugin(renderer)
        shaderType = RenderingAPI.RendererInfo.kRendererObjectTypeShader
        nodeTypes = rendererInfoPlugin.getRendererObjectNames(shaderType)

        for node_type in nodeTypes:
            if node_type.startswith("lc_"):
                result.append(node_type)
        return result

    from Katana import NodegraphAPI
    shader_type_list = getAllLCAArnoldShadingTypes()
    result = []
    i = 0
    for shader_type in shader_type_list:    
        as_node = NodegraphAPI.GetNode(shader_type)

        if not as_node:
            as_node = NodegraphAPI.CreateNode('ArnoldShadingNode', NodegraphAPI.GetRootNode())
            width = 5
            NodegraphAPI.SetNodePosition(as_node, (150*math.floor(i/width), -50*(i%width)))
            i += 1

        as_node.getParameter('nodeType').setValue(shader_type, 0)
        as_node.checkDynamicParameters()
        as_node.getParameter('name').setValue(shader_type, 0)

        result.append(as_node)
    return result

def ExpoetMaterialX(nodes, saveTo):
    import MaterialX as mx
    reload (mx)
    doc = mx.createDocument()
    mx_typedef = doc.addTypeDef("closure")
    mx_typedef.setSemantic("shader")
    as_node_list = nodes
    for as_node in as_node_list:
        param_names = []
        _name = as_node.getName()
        output_subffixs = [x.getName() for x in as_node.getOutputPorts()]
        if output_subffixs == OUT:
            _type = "float"
        elif output_subffixs == OUT_XY:
            _type = "vector2"
        elif output_subffixs == OUT_XYZ:
            _type = "vector3"
        elif output_subffixs == OUT_RGB:
            _type = "color3"
        elif output_subffixs == OUT_RGBA:
            _type = "color4"
        else:
            pass
        _node = as_node.getParameter('nodeType').getValue(0)
        mx_nodedef = doc.addNodeDef(_name, _type, _node)
        input_ports = [x.getName() for x in as_node.getInputPorts()]
        for input_port in input_ports:
            as_node.checkDynamicParameters()
            param_name = removeSwizzleSuffix(input_port)
            if param_name in param_names:
                continue
            else:
                param_names.append(param_name)
            param = as_node.getParameter("parameters.%s.value"%param_name)
            # There is three types of Katana Standard Data Type
            # {number, numberArray, string}
            ktn_type = param.getType()
            # This type contents {float, integer, boolean}
            if   ktn_type == "number":
                input_ptr = mx_nodedef.addInput(param_name, "float")
                input_ptr.setValue(param.getValue(0), "float")
            # This type contents {string, envm, map}
            elif ktn_type == "string":
                # Check out param is string or closure.
                if param.getValue(0) == "Connect to a shader in the node graph":
                    mx_nodedef.addInput(param_name, "closure")
                    # If nodedef input contents colsure, it must output closure.
                    mx_nodedef.setType("closure")
                else:
                    input_ptr = mx_nodedef.addInput(param_name, "string")
                    input_ptr.setValue(param.getValue(0), "string")                
            # This type contents {array, matrix, color, vector}
            elif ktn_type == "numberArray":
                # There is four normal MaterialX Data Type
                # {color3, color4, vector2, vector3}
                input_subffixs = []
                for input_port in input_ports:
                    # Get a list contents subffix
                    if input_port.startswith(param_name) and input_port.find(".")>=0:
                        subffix = input_port.split(".")[-1]
                        if subffix not in SWIZZLE_SUFFIX:
                            continue
                        input_subffixs.append(subffix)
                if not input_subffixs:
                    mx_nodedef.addInput(param_name, "floatarray")
                else:
                    # Set color3
                    if input_subffixs == COLOR3:
                        _tuple = [x.getValue(0) for x in param.getChildren()]
                        if _tuple:
                            input_ptr = mx_nodedef.addInput(param_name, "color3")
                            input_ptr.setValue(mx.Color3(_tuple[0], _tuple[1], _tuple[2]), "color3")
                        else:
                            input_ptr = mx_nodedef.addInput(param_name, "floatarray")
                    # Set color4
                    elif input_subffixs == COLOR4:
                        _tuple = [x.getValue(0) for x in param.getChildren()]
                        if _tuple:
                            input_ptr = mx_nodedef.addInput(param_name, "color4")
                            input_ptr.setValue(mx.Color4(_tuple[0], _tuple[1], _tuple[2], _tuple[3]), "color3")
                        else:
                            input_ptr = mx_nodedef.addInput(param_name, "floatarray")
                    # Set vector2
                    elif input_subffixs == VECTOR2:
                        _tuple = [x.getValue(0) for x in param.getChildren()]
                        if _tuple:
                            input_ptr = mx_nodedef.addInput(param_name, "vector2")
                            input_ptr.setValue(mx.Vector2(_tuple[0], _tuple[1]), "color3")
                        else:
                            input_ptr = mx_nodedef.addInput(param_name, "floatarray")
                    # Set vector3
                    elif input_subffixs == VECTOR3:
                        _tuple = [x.getValue(0) for x in param.getChildren()]
                        if _tuple:
                            input_ptr = mx_nodedef.addInput(param_name, "vector3")
                            input_ptr.setValue(mx.Vector3(_tuple[0], _tuple[1], _tuple[2]), "color3")
                        else:
                            input_ptr = mx_nodedef.addInput(param_name, "floatarray")
                    else:
                        mx_nodedef.addInput(param_name, "floatarray")
            else:
                pass
    mx.writeToXmlFile(doc, saveTo)

def main():
    mtoa_nodes = createMtoAArnoldShadingNodes()
    saveTo = "/path/to/mtoa_nodedefs_orig.mtlx"

    ExpoetMaterialX(mtoa_nodes,saveTo)


if __name__ == "__main__":
    print ""


"""
#~ Run this script in Katana Python Tab
import sys
path = "--/KTMaterialXTools/python/KTMaterialXTools"
sys.path.append(path)
import NodedefsGeneration as Gen
reload(Gen)
Gen.main()
"""