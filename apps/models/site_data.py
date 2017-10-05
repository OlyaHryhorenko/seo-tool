from wrapper import Wrapper


class SiteData(object):

    def __init__(self, wrapper):
        if wrapper is None:
            raise TypeError

        self.w = wrapper
        self.NAME = 'site_data'

    db_name = "site_data"

    # def get_all(self):
    #     return self.w.select(["*"], [self.db_name])
    #
    # def get_all_for_user(self, id):
    #     return self.w.select(["*"], [self.db_name], "where user_id=%s" % id)

    def add_site_data(self, fields):
        return self.w.insert(fields, self.NAME)

    def get_site_data(self, id):
        return self.w.select(["*"], [self.db_name], "where site_id=%s" % id)
    #
    # def edit_site(self, fields, condition):
    #     return self.w.update(fields, self.NAME, condition)
