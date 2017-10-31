from wrapper import Wrapper


class Statuses(object):

    def __init__(self, wrapper):
        if wrapper is None:
            raise TypeError

        self.w = wrapper
        self.NAME = 'site_status'

    db_name = "site_status"

    def get_all(self):
        return self.w.select(["*"], [self.db_name])

    def add_status(self, fields):
        return self.w.insert(fields, self.NAME)

    def get_status(self, id):
        return self.w.select({"data", "date", "type_id", "type", "status_id"}, [self.db_name],
                             "INNER JOIN types on site_status.type_id = types.id where site_id=%s" % id)

    def get_status_for_all(self):
        return self.w.select({"site_id", 'count(*) as count'}, [self.db_name],
                             "GROUP BY site_status.site_id")

    def edit_status(self, fields, condition):
        return self.w.update(fields, self.NAME, condition)

    def delete_status(self, id):
        return self.w.delete(self.NAME,  id)
