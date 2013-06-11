from Products.CMFPlone.CatalogTool import CatalogTool as PloneCatalogTool
from Products.CMFCore.utils import getToolByName

class CatalogTool(PloneCatalogTool):
    id = 'portal_history_catalog'
