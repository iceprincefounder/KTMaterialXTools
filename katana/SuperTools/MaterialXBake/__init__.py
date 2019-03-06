import logging
log = logging.getLogger('MaterialXBake')

try:
    import v1 as MaterialXBake
except Exception as exception:
    log.exception('Error importing Super Tool Python package: %s' % str(exception))
else:
    PluginRegistry = [("SuperTool", 2, "MaterialXBake",
                      (MaterialXBake.MaterialXBakeNode,
                       MaterialXBake.GetEditor))]

