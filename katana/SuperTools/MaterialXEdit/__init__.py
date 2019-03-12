import logging
log = logging.getLogger('MaterialXEdit')

try:
    import v1 as MaterialXEdit
except Exception as exception:
    log.exception('Error importing Super Tool Python package: %s' % str(exception))
else:
    PluginRegistry = [("SuperTool", 2, "MaterialXEdit",
                      (MaterialXEdit.MaterialXEditNode,
                       MaterialXEdit.GetEditor))]