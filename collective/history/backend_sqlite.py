import json
import os
import sqlite3
import logging


LOG = logging.getLogger("collective.history")
DB_PATH_ENV = 'collective_history_sqlite'
DB_PATH = os.environ.get(DB_PATH_ENV)
DATEF = '%Y%m%d%H%M%S'
COLUMNS = "`id`,  `what`, `on_what`, `what_info`, `when`, `where_uri`, `where_uid`, `where_path`, `who`"


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class SQLiteBackend(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.isReady = False
        self.db_path = DB_PATH
        self.db = None

    def update(self):
        self.isReady = True

    def add(self, useraction_wrapper):
        if not self.isReady:
            return
        self._initdb()
        uw = useraction_wrapper
        REQUEST = """INSERT INTO history (%s)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""" % COLUMNS
        VALUES = [
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
        LOG.info(REQUEST)
        LOG.info(VALUES)
        try:
            self.db.execute(REQUEST, VALUES)
        except sqlite3.IntegrityError as e:
            LOG.error(e)
        self._closedb()

    def rm(self, useraction_id):
        if not self.isReady:
            return
        self._initdb()
        REQUEST = """DELETE FROM history WHERE id=?"""
        self.db.execute(REQUEST, [useraction_id])
        self._closedb()

    def search(self, **kwargs):
        if not self.isReady:
            return []
        self._initdb()
        QUERY = "SELECT %s FROM history" % COLUMNS
        WHERE = []
        VALUES = []
        #when={
        #    'query': DateTime(lastCheck),
        #    'range': 'min'
        #}
        LOG.info('search')
        if 'when' in kwargs:
            when = kwargs['when']
            value = None
            operator = "="
            if 'query' in when:
                value = int(when['query'].strftime(DATEF))
            else:
                value = int(when.strftime(DATEF))
            if 'range' in when:
                r = when['range']
                if r == 'min':
                    operator = "<"
                elif r == 'max':
                    operator = ">"
            WHERE.append("`when` %s ?" % operator)
            VALUES.append(value)
        if WHERE:
            QUERY += "WHERE %s" % (" AND ".join(WHERE))
        results = self.db.execute(QUERY).fetchall()
        self._closedb()
        return results

    def get(self, useraction_id):
        if not self.isReady:
            return
        LOG.info('get %s' % useraction_id)
        QUERY = "SELECT %s FROM history WHERE `id` = ?" % COLUMNS
        return self.db.excecute(QUERY, [useraction_id]).fetchall()

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
        if self.db is None:
            return
        self.db.commit()
        self.db.close()
        self.db = None
