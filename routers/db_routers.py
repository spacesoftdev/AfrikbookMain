class AuthRouter:
    route_app_labels = {'auth', 'contenttypes', 'admin', 'sessions', 'messages', 'staticfiles', 'main', 'account', 'vendor', 'customer', 'journal', 'stock', 'report', 'settings'}

    def db_for_read(self, model, **hints):
        
        if model._meta.app_label in self.route_app_labels:
            return 'auth_db'
        return None

    def db_for_write(self, model, **hints):
        
        if model._meta.app_label in self.route_app_labels:
            return 'auth_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        
        if (
            obj1._meta.app_label in self.route_app_labels or
            obj2._meta.app_label in self.route_app_labels
        ):
           return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        
        if app_label in self.route_app_labels:
            return db == 'auth_db'
        return None
    


    
class EliteRouter:
    route_app_labels = {'auth', 'contenttypes', 'admin', 'sessions', 'messages', 'staticfiles', 'main', 'account', 'vendor', 'customer', 'journal', 'stock', 'report', 'settings'}

    def db_for_read(self, model, **hints):
        
        if model._meta.app_label in self.route_app_labels:
            return 'elite'
        return None

    def db_for_write(self, model, **hints):
        
        if model._meta.app_label in self.route_app_labels:
            return 'elite'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        
        if (
            obj1._meta.app_label in self.route_app_labels or
            obj2._meta.app_label in self.route_app_labels
        ):
           return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        
        if app_label in self.route_app_labels:
            return db == 'elite'
        return None
    


