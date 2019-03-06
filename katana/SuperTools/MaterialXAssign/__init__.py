import logging
log = logging.getLogger('MaterialXAssign')

try:
    import v1 as MaterialXAssign
except Exception as exception:
    log.exception('Error importing Super Tool Python package: %s' % str(exception))
else:
    PluginRegistry = [("SuperTool", 2, "MaterialXAssign",
                      (MaterialXAssign.MaterialXAssignNode,
                       MaterialXAssign.GetEditor))]