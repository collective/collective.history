import datetime
import json
import os
import sqlite3
import logging
from collective.history.useraction import IUserAction
from zope import interface

LOG = logging.getLogger("collective.history")
DB_PATH_ENV = 'collective_history_sqlite'
DB_PATH = os.environ.get(DB_PATH_ENV)
DATEF = '%Y%m%d%H%M%S'
COLUMNS = ("`id`,  `what`, `on_what`, `what_info`, `when`, `where_uri`, "
           "`where_uid`, `where_path`, `who`")


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def date_to_int(date):
    integer = int(date.strftime(DATEF))
    return integer


def int_to_date(integer):
    s = str(integer)
    return datetime.datetime.strptime(s, DATEF)


class UserAction(object):
    interface.implements(IUserAction)

    def __init__(self, original):
        self.what = original['what']
        self.what_info = json.loads(original['what_info'])
        self.on_what = original['on_what']
        when = original['when']
        if type(when) != datetime.datetime:
            self.when = int_to_date(when)
        else:
            self.when = when
        self.where_uri = original['where_uri']
        self.where_uid = original['where_uid']
        self.where_path = str(original['where_path'])
        self.who = original['who']
        self.id = original['id']


class SQLiteBackend(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.isReady = False
        self.db_path = DB_PATH
        self.db = None
        self._should_closedb = True

    def update(self):
        self.isReady = True

    def add(self, useraction_wrapper):
        if not self.isReady:
            return
        uw = useraction_wrapper
        query = """INSERT INTO history (%s)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""" % COLUMNS
        values = [
            uw.id,
            uw.what,
            uw.on_what,
            json.dumps(uw.what_info),
            int(uw.when.strftime(DATEF)),
            uw.where_uri,
            uw.where_uid,
            uw.where_path,
            uw.who
        ]
        self._querydb(query, values)

    def rm(self, useraction_id):
        if not self.isReady:
            return
        query = """DELETE FROM history WHERE id=?"""
        self._querydb(query, [useraction_id])

    def search(self, **kwargs):
        if not self.isReady:
            return []
        query = "SELECT %s FROM history" % COLUMNS
        where = []
        values = []
        #when={
        #    'query': DateTime(lastCheck),
        #    'range': 'min'
        #}
        if 'when' in kwargs:
            operator, value = self._searchWhen(**kwargs)
            where.append("`when` %s ?" % operator)
            values.append(value)
        if where:
            query += " where %s" % (" AND ".join(where))
        query += " ORDER BY `when` DESC"
        results = self._querydb(query, values).fetchall()
        updated = []
        for info in results:
            updated.append(UserAction(info))
        return updated

    def _searchWhen(self, **kwargs):
        when = kwargs['when']
        value = None
        operator = "="
        if 'query' in when:
            value = date_to_int(when['query'])
        else:
            value = date_to_int(when)
        if 'range' in when:
            r = when['range']
            if r == 'min':
                operator = ">"
            elif r == 'max':
                operator = "<"
        return (operator, value)

    def get(self, useraction_id):
        if not self.isReady:
            return
        self._initdb()
        QUERY = "SELECT %s FROM history WHERE `id` = ?" % COLUMNS
        result = self.db.execute(QUERY, [useraction_id]).fetchone()
        self._closedb()
        return UserAction(result)

    def _initdb(self):
        if self.db is not None:
            return

        self.db = sqlite3.connect(self.db_path)
        self.db.row_factory = dict_factory
        self.db.execute(
            '''
            CREATE TABLE IF NOT EXISTS history(
            `id`            TEXT,
            `what`          TEXT,
            `on_what`       TEXT,
            `what_info`     TEXT,
            `when`          INTEGER,
            `where_uri`     TEXT,
            `where_uid`     TEXT,
            `where_path`    TEXT,
            `who`           TEXT,
            `transactionid` TEXT,
            PRIMARY KEY(`id`))
            '''
        )

    def _closedb(self):
        if self.db is None or not self._should_closedb:
            return
        self._db_close = True
        self.db.commit()
        self.db.close()
        self.db = None

    def _querydb(self, query, values):
        self._initdb()
        try:
            return self.db.execute(query, values)
        except sqlite3.IntegrityError as e:
            LOG.error(e)
        self._closedb()
