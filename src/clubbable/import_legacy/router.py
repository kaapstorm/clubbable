
class LegacyDbRouter(object):
    """
    This router controls database operations for import_legacy.models in
    order to use the legacy database.
    """

    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'import_legacy':
            return 'legacy'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'import_legacy':
            return 'legacy'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        # Allow relations if both models are import_legacy.models
        if (
            obj1._meta.app_label == 'import_legacy' and
            obj2._meta.app_label == 'import_legacy'
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # Don't try to write migrations to the legacy database
        if app_label == 'import_legacy':
            return False
        return None
