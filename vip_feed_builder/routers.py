from .config import databases

class AuthRouter:
    route_app_labels = {'auth', 'contenttypes'}

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return('default')
        return(None)

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return('default')
        return(None)

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.route_app_labels:
            return db == 'dj_vipp'
        return(None)

class VipVersionRouter:

    def db_for_read(self, model, **hints):
        return(databases[model._meta.app_label]['NAME'])

    def db_for_write(self, model, **hints):
        return(databases[model._meta.app_label]['NAME'])

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        print(db, app_label)
        if app_label == 'vip6':
            return db == 'vip6'
        elif app_label == 'vip52':
            return db == 'vip52'
        else:
            return(False)
