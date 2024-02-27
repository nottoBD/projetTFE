from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProfileViewSet,
    EnfantViewSet,
    FraisExtraordinaireViewSet,
    IndiceSanteViewSet,
    CorrespondanceViewSet,
)

# routeur drf, map viewsets et chemins


router = DefaultRouter()

router.register(r"profiles", ProfileViewSet)
router.register(r"enfants", EnfantViewSet)
router.register(r"fraisextraordinaires", FraisExtraordinaireViewSet)
router.register(r"indicesante", IndiceSanteViewSet)
router.register(r"correspondances", CorrespondanceViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
