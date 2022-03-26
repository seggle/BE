from rest_framework import serializers
from proposal.models import Proposal
from account.models import User

class ProposalSerializer(serializers.ModelSerializer):

    class Meta:
        model = Proposal
        # fields = "__all__"
        fields = ["id", "title", "context", "created_user", "created_time"]

class ProposalGetSerializer(serializers.ModelSerializer):

    class Meta:
        model = Proposal
        # fields = "__all__"
        fields = ["id", "title", "created_user", "created_time"]

class ProposalPatchSerializer(serializers.ModelSerializer):

    class Meta:
        model = Proposal
        # fields = "__all__"
        fields = ["title", "context"]