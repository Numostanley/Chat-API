from rest_framework import serializers

from ... import models as user_models


class UserDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = user_models.User
        fields: list[str] = [
            'id', 'email', 'phone_number', 'username'
        ]

    def to_representation(self, instance):
        representation = super(UserDetailSerializer, self).to_representation(instance)
        representation['full_name'] = instance.get_full_name
        return representation
