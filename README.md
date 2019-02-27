
# kt-materialx-tools
The Tools Decompile MaterialX to Nodes and Material Network Nodes to MaterialX Generating.
![enter image description here](https://user-images.githubusercontent.com/16664056/53480443-2faf7e80-3ab6-11e9-892e-f4162bc118a8.png)

## Overview and Purpose

This repository contents the tools to create [MaterialX](https://www.materialx.org/) file for Arnold Renderer.

We generate [Katana](https://www.foundry.com/products/katana) ArnoldShadingNode Networks to MaterialX mtlx file, assign mtlx file to models via  [Arnold Operators MaterialX node](https://docs.arnoldrenderer.com/display/A5NodeRef/materialx) .

We could create whole material networks from MaterialX file and edit.


## Current Support
Katana + Arnold KtoA + MaterialX

## How to Install
You should compile MaterialX 1.36.0 or later;

Make sure you have suitable version of Arnold KtoA that support MaterialX;

Set those environment into you Katana launcher:
~~~{.sh}
export PYTHONPATH=$PYTHONPATH:/path/to/materialx-v1.36.1/python
export KATANA_RESOURCES=$KATANA_RESOURCES:/path/to/KTMaterialXTools
~~~

Open Katana and create node MaterialXBake!

## Simple Example

Katana Example : [example_001.zip](https://github.com/iceprincefounder/KTMaterialXTools/files/2909497/example_001.zip)

MaterialX File : [pony.zip](https://github.com/iceprincefounder/KTMaterialXTools/files/2909554/pony.zip)

