from zope import component
from zope import interface

from repoze.catalog import query, catalog
from repoze.catalog.catalog import Catalog
from repoze.catalog.indexes.field import CatalogFieldIndex
from repoze.catalog.indexes.text import CatalogTextIndex

from souper import interfaces as isouper
from souper import soup
SOUP = 'collective_history'
# 
# 
# class StorageLocator(object):
# 
#     def __init__(self, context):
#        self.context = context
# 
#     def storage(self, soup_name):
#        if soup_name not in self.context:
#            self.context[soup_name] = soup.SoupData()
#        return self.context[soup_name]
# 
# component.provideAdapter(StorageLocator,
#                          adapts=[interface.Interface])


@interface.implementer(isouper.ICatalogFactory)
class CatalogFactory(object):

    def __call__(self, context=None):
        import pdb;pdb.set_trace()
        catalog = Catalog()

        id = soup.NodeAttributeIndexer('id')
        catalog[u'id'] = CatalogFieldIndex(id)

        what = soup.NodeAttributeIndexer('what')
        catalog[u'what'] = CatalogFieldIndex(what)
        what_info = soup.NodeAttributeIndexer('what_info')
        catalog[u'what_info'] = CatalogFieldIndex(what)
        on_what = soup.NodeAttributeIndexer('what_info')
        catalog[u'on_what'] = CatalogFieldIndex(on_what)

        when = soup.NodeAttributeIndexer('when')
        catalog[u'when'] = (when)

        where_path = soup.NodeAttributeIndexer('where_path')
        catalog[u'where_path'] = CatalogPathIndex(where_path)
        where_uri = soup.NodeAttributeIndexer('where_uri')
        catalog[u'where_uri'] = CatalogFieldIndex(where_uri)
        where_uid = soup.NodeAttributeIndexer('where_uid')
        catalog[u'where_uid'] = CatalogFieldIndex(where_uid)

        who = soup.NodeAttributeIndexer('who')
        catalog[u'who'] = CatalogFieldIndex(who)
        return catalog

component.provideUtility(CatalogFactory(), name=SOUP)



class SouperBackend(object):
    """Backend based on souper"""

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.isReady = False
        self.soup = None

    def update(self):
        self.isReady = True
        self.soup = soup.get_soup(SOUP, self.context)

    def add(self, useraction_wrapper):
        if not self.isReady:
            return
        record = soup.Record()
        record.attrs['what'] = useraction_wrapper.what
        record.attrs['what_info'] = useraction_wrapper.what_info
        record.attrs['on_what'] = useraction_wrapper.on_what
        record.attrs['when'] = useraction_wrapper.when
        record.attrs['where_uri'] = useraction_wrapper.where_uri
        record.attrs['where_uid'] = useraction_wrapper.where_uid
        record.attrs['where_path'] = useraction_wrapper.where_path
        record.attrs['who'] = useraction_wrapper.who
        record.attrs['id'] = useraction_wrapper.id
        record_id = self.soup.add(record)

    def rm(self, useraction_id):
        pass

    def search(self, **kwargs):
        return []

    def get(self, useraction_id):
        return

