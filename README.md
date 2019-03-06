

# kt-materialx-tools
The Tools translate Material Network Nodes to MaterialX file and assign and edit MaterialX file into scene with Arnold Operator.
![show image](https://user-images.githubusercontent.com/16664056/53862468-7525fb80-4022-11e9-81a2-2a8b2f2f2a35.png)

## Overview and Purpose

This repository contents the tools to create and edit [MaterialX](https://www.materialx.org/) file for Arnold Renderer.

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
export PYTHONPATH=$PYTHONPATH:/path/to/KTMaterialXTools/python
export KATANA_RESOURCES=$KATANA_RESOURCES:/path/to/KTMaterialXTools/katana
~~~

Open Katana and create node MaterialXBake MaterialXAssign MaterialXEdit!

## Simple Example
![enter image description here](https://user-images.githubusercontent.com/16664056/53865226-858da480-4029-11e9-9d67-1623bfc5bc74.png)
Katana Example : [example_001.zip](https://github.com/iceprincefounder/KTMaterialXTools/files/2909497/example_001.zip)  [example_002.zip](https://github.com/iceprincefounder/KTMaterialXTools/files/2935094/example_002.zip)
MaterialX File : [pony.zip](https://github.com/iceprincefounder/KTMaterialXTools/files/2909554/pony.zip)
