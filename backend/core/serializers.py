from rest_framework import serializers
from .models import Address, User

from rest_framework import serializers
from .models import Address

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            'id',
            'user',
            'name',
            'address',
            'city',
            'state',
            'country',
            'postal_code',
            'is_default',
            'created_at',
            'updated_at',
        ]