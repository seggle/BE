from rest_framework import serializers
from proposal.models import Proposal
from account.models import User

class ProposalSerializer(serializers.ModelSerializer):

    class Meta:
        model = Proposal
        #fields = ["id", "title", "context", "created_user", "created_time"]
        fields = "__all__"
