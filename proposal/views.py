from multiprocessing import context
from pickle import TRUE
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated,AllowAny,IsAuthenticatedOrReadOnly
from rest_framework import status
from .models import Proposal
from rest_framework.pagination import PageNumberPagination #pagination
from utils.pagination import PaginationHandlerMixin #pagination
from .serializers import ProposalSerializer, ProposalGetSerializer, ProposalPatchSerializer
from utils.get_obj import *
from utils.message import *

# Create your views here.

class BasicPagination(PageNumberPagination):
    page_size_query_param = 'limit'

class ProposalView(APIView, PaginationHandlerMixin):
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = BasicPagination

    def post(self,request):
        data = request.data
        data["created_user"] = request.user

        serializer = ProposalSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(msg_success, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, proposal_id=None):
        if proposal_id is None:
            proposal_list = Proposal.objects.all().order_by('-created_time')
            
            page = self.paginate_queryset(proposal_list)
            
            if page is not None:
                serializer = self.get_paginated_response(ProposalGetSerializer(page, many=True).data)
            else:
                serializer = ProposalGetSerializer(proposal_list, many=True)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            proposal = get_proposal(proposal_id)

            proposal_list_serializer = ProposalSerializer(proposal)
            return Response(proposal_list_serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, proposal_id=None):
        if proposal_id is None:
            return Response(msg_error, status=status.HTTP_400_BAD_REQUEST)
        proposal = get_proposal(proposal_id)

        data = request.data
        obj = {
            "title" : data["title"],
            "context" : data["context"],
        }
        if proposal.created_user == request.user:
            serializer = ProposalPatchSerializer(proposal, data=obj)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(msg_error, status=status.HTTP_400_BAD_REQUEST)
        return Response(msg_error, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, proposal_id=None):
        if proposal_id is None:
            return Response(msg_error, status=status.HTTP_400_BAD_REQUEST)
    
        proposal = get_proposal(proposal_id)

        if proposal.created_user == request.user or request.user.privilege == 2:
            proposal.delete()
            return Response(msg_success, status=status.HTTP_200_OK)
        else:
            return Response(msg_error, status=status.HTTP_400_BAD_REQUEST)
