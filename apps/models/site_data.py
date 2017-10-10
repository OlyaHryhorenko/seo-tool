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

    def add_title(self, fields):
        return self.w.insert(fields, self.NAME)

    def add_h1(self, fields):
        return self.w.insert(fields, self.NAME)

    def add_description(self, fields):
        return self.w.insert(fields, self.NAME)

    def add_response(self, fields):
        return self.w.insert(fields, self.NAME)

    def add_robots(self, fields):
        return self.w.insert(fields, self.NAME)

    def add_sitemap(self, fields):
        return self.w.insert(fields, self.NAME)

    def add_html(self, fields):
        return self.w.insert(fields, self.NAME)

    def add_ip(self, fields):
        return self.w.insert(fields, self.NAME)

    def get_site_data(self, id):
        return self.w.select({"data", "date", "type_id", "type"}, [self.db_name],
                             "INNER JOIN types on site_data.type_id = types.id where site_id=%s" % id)

    def get_sites_title(self, id):
        return self.w.select({"data"}, [self.db_name],
                             "where type_id=1 and site_id=%s" % id)

    def get_sites_response(self, id):
        return self.w.select({"data"}, [self.db_name],
                         "where type_id=3 and site_id=%s" % id)

    def get_sites_h1(self, id):
        return self.w.select({"data"}, [self.db_name],
                             "where type_id=2 and site_id=%s" % id)

    def get_sites_description(self, id):
        return self.w.select({"data"}, [self.db_name],
                             "where type_id=4 and site_id=%s" % id)

    def get_sites_robots(self, id):
        return self.w.select({"data"}, [self.db_name],
                             "where type_id=5 and site_id=%s" % id)

    def get_sites_sitemap(self, id):
        return self.w.select({"data"}, [self.db_name],
                             "where type_id=7 and site_id=%s" % id)

    def get_sites_html(self, id):
        return self.w.select({"data"}, [self.db_name],
                             "where type_id=8 and site_id=%s" % id)

    def get_sites_ip(self, id):
        return self.w.select({"data"}, [self.db_name],
                             "where type_id=9 and site_id=%s" % id)

    def delete_site_data(self, id):
        return self.w.delete_site(self.NAME, id)
    #
    # def edit_site(self, fields, condition):
    #     return self.w.update(fields, self.NAME, condition)
