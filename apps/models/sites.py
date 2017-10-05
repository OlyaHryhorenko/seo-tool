from wrapper import Wrapper


class Sites(object):

    def __init__(self, wrapper):
        if wrapper is None:
            raise TypeError

        self.w = wrapper
        self.NAME = 'sites'

    db_name = "sites"

    def get_all(self):
        return self.w.select(["*"], [self.db_name])

    def get_all_for_user(self, id):
        return self.w.select(["*"], [self.db_name], "where user_id=%s" % id)

    def add_site(self, fields):
        return self.w.insert(fields, self.NAME)

    def get_site(self, id):
        return self.w.select(["*"], [self.db_name], "where id=%s" % id)

    def edit_site(self, fields, condition):
        return self.w.update(fields, self.NAME, condition)
