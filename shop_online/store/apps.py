from django.apps import AppConfig

class StoreConfig(AppConfig):
    name = 'store'

    def ready(self):
        import store.signals  # Signals should be imported here to ensure they are registered
