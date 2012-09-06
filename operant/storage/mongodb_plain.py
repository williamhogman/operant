from operant.storage.mongodb_common import MongoBase
import pymongo as pm


class MongoDS(MongoBase):
    """Datastore for pymongo"""

    def __init__(self, client, database=None):
        if isinstance(client, dict):
            if database is None and "database" in client:
                database = client.pop("database")
            client = pm.Connection(**client)

        if not database:
            database = "operant"
        self._db = client[database]

    def _update_user(self, doc, chng, fields, callback=None, new=True, **kwargs):
        res = self._users_col.find_and_modify(doc,
                                              chng,
                                              upsert=True,
                                              fields=fields,
                                              new=new,
                                              **kwargs)
        callback(res)

    def _find_user(user, parts, callback=None):
        res = self._users_col.find(dict(_id=user),
                                   parts)
        callback(res)

    def _insert_log(doc):
        self._log_col.insert(doc, safe=False)
