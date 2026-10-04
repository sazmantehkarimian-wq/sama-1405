from django.apps import AppConfig


class AuctionFlowConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'domains.auctionflow'
    verbose_name = 'گردش کامل مزایده'

    def ready(self):
        # These models live in a separate module to keep the core flow model readable,
        # but must be registered with the auctionflow app at startup.
        from . import intake_models  # noqa: F401
        from . import signals  # noqa: F401
