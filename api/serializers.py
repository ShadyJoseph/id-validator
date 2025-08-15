from rest_framework import serializers


class NationalIDSerializer(serializers.Serializer):
    national_id = serializers.CharField(max_length=14, min_length=14)
