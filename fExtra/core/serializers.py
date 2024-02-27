from rest_framework import serializers
from .models import Profile, Enfant, FraisExtraordinaire, IndiceSante, Correspondance

#


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"


class EnfantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enfant
        fields = "__all__"


class FraisExtraordinaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = FraisExtraordinaire
        fields = "__all__"


class IndiceSanteSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndiceSante
        fields = "__all__"


class CorrespondanceSerializer(serializers.ModelSerializer):
    parent_emetteur = serializers.SlugRelatedField(
        slug_field="user_id", queryset=Profile.objects.all()
    )
    parent_recepteur = serializers.SlugRelatedField(
        slug_field="user_id", queryset=Profile.objects.all()
    )

    class Meta:
        model = Correspondance
        fields = "__all__"
