from Products.Five import BrowserView


class HistoryView(BrowserView):

    def get_useractions(self):
        name = '@@collective.history.manager'
        manager = self.context.restrictedTraverse(name)
        manager.update()
        return manager.search()
