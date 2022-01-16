from rest_framework import serializers
from proposal.models import Proposal


class ProposalSerializer(serializers.Serializer):
    _id = serializers.IntegerField(read_only=True)
    title = serializers.CharField()
    context = serializers.CharField()
    created_user = serializers.CharField()
    created_time = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        print(validated_data)
        return Proposal.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.context = validated_data.get('context', instance.context)
        instance.save()
        return instance