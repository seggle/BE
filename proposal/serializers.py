from rest_framework import serializers
from proposal.models import Proposal
from account.models import User

class ProposalGetAllSerializer(serializers.ModelSerializer):

    class Meta:
        model = Proposal
        #fields = ["title", "context", "created_user"]
        fields = ["id", "title", "created_user_id", "created_time"]
        #fields = "__all__"

        #fields = ["title","context"]

class ProposalSerializer(serializers.ModelSerializer):

    class Meta:
        model = Proposal
        fields = ["id", "title", "context", "created_user", "created_time"]