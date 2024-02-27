from django.shortcuts import render
from rest_framework import viewsets
from .models import Profile, Enfant, FraisExtraordinaire, IndiceSante, Correspondance
from .serializers import (
    ProfileSerializer,
    EnfantSerializer,
    FraisExtraordinaireSerializer,
    IndiceSanteSerializer,
    CorrespondanceSerializer,
)

# TODO: permissions, filtrage pagination tri, testing #


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer


class EnfantViewSet(viewsets.ModelViewSet):
    queryset = Enfant.objects.all()
    serializer_class = EnfantSerializer


class FraisExtraordinaireViewSet(viewsets.ModelViewSet):
    queryset = FraisExtraordinaire.objects.all()
    serializer_class = FraisExtraordinaireSerializer


class IndiceSanteViewSet(viewsets.ModelViewSet):
    queryset = IndiceSante.objects.all()
    serializer_class = IndiceSanteSerializer


class CorrespondanceViewSet(viewsets.ModelViewSet):
    queryset = Correspondance.objects.all()
    serializer_class = CorrespondanceSerializer
