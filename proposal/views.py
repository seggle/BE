from curses import use_default_colors
from multiprocessing import context
from pickle import TRUE
from django.shortcuts import render
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken, OutstandingToken, BlacklistedToken
from rest_framework import status
from django.http import JsonResponse
from .models import Proposal
from rest_framework.pagination import PageNumberPagination #pagination
from utils.pagination import PaginationHandlerMixin #pagination
from . import serializers
from django.db.models import F

# Create your views here.

class BasicPagination(PageNumberPagination):
    page_size_query_param = 'limit'

class ProposalView(APIView, PaginationHandlerMixin):

    # pagination
    pagination_class = BasicPagination

    def get_object(self, proposal_id):
        proposal = generics.get_object_or_404(Proposal, id = proposal_id)
        return proposal

    def post(self,request):
        data = request.data
        data._mutable = True
        data["created_user"] = request.user
        #data._mutable = False
        #print(data)

        serializer = serializers.ProposalSerializer(data=data) #Request의 data를 UserSerializer로 변환

        if serializer.is_valid():
            serializer.save() #UserSerializer의 유효성 검사를 한 뒤 DB에 저장
            #return Response(serializer.data, status=status.HTTP_201_CREATED) #client에게 JSON response 전달
            return Response("Success", status=status.HTTP_201_CREATED) #client에게 JSON response 전달
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, **kwargs):

        if kwargs.get('proposal_id') is None:
            proposal_list = Proposal.objects.values('id', 'title', 'created_user', 'created_time')
            page = self.paginate_queryset(proposal_list)

            if page is not None:
                serializer = self.get_paginated_response(page)
            else:
                serializer = self.serializer_class(proposal_list, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)
        else:

            proposal_id = kwargs.get('proposal_id')
            proposal = self.get_object(proposal_id)

            proposal_list_serializer = serializers.ProposalSerializer(Proposal.objects.get(id=proposal_id))
            return Response(proposal_list_serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, **kwargs):
        if kwargs.get('proposal_id') is None:
            return Response("Fail", status=status.HTTP_400_BAD_REQUEST)
        else:
            proposal_id = kwargs.get('proposal_id')
            proposal = self.get_object(proposal_id)

            data = request.data
            user = Proposal.objects.get(id=proposal_id)
            if user.created_user == request.user:
                user.title = data["title"]
                user.context = data["context"]
                user.save(force_update=True)
                return Response("Success", status=status.HTTP_200_OK)
            else:
                return Response("Fail", status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, **kwargs):
        if kwargs.get('proposal_id') is None:
            return Response("Fail", status=status.HTTP_400_BAD_REQUEST)
        else:
            proposal_id = kwargs.get('proposal_id')
            proposal = self.get_object(proposal_id)

            user = Proposal.objects.get(id=proposal_id)
            if user.created_user == request.user:
                user.delete()
                return Response("Success", status=status.HTTP_200_OK)
            else:
                return Response("Fail", status=status.HTTP_400_BAD_REQUEST)


