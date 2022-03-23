from curses import use_default_colors
from multiprocessing import context
from pickle import TRUE
from django.shortcuts import render
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken, OutstandingToken, BlacklistedToken
from rest_framework import status
from django.http import JsonResponse
from .models import Proposal
from rest_framework.pagination import PageNumberPagination #pagination
from utils.pagination import PaginationHandlerMixin #pagination
from serializers import ProposalSerializer
from django.db.models import F
from utils.get_obj import *
from utils.message import *

# Create your views here.

class BasicPagination(PageNumberPagination):
    page_size_query_param = 'limit'

class ProposalView(APIView, PaginationHandlerMixin):
    # pagination
    pagination_class = BasicPagination

    # 08-01 건의 작성
    def post(self, request):
        data = request.data
        data["created_user"] = request.user
        serializer = ProposalSerializer(data=data) #Request의 data를 UserSerializer로 변환
        if serializer.is_valid():
            serializer.save() #UserSerializer의 유효성 검사를 한 뒤 DB에 저장
            return Response(serializer.data, status=status.HTTP_201_CREATED) #client에게 JSON response 전달
        else:
            return Response(serializer.error, status=status.HTTP_400_BAD_REQUEST)

    # 08-02 건의 글 세부 조회
    def get(self, request, proposal_id):
        proposal = get_proposal(proposal_id)
        proposal_list_serializer = ProposalSerializer(proposal)
        return Response(proposal_list_serializer.data, status=status.HTTP_200_OK)

    # 08-03 건의 글 수정
    def patch(self, request, proposal_id):
        proposal = get_proposal(proposal_id)
        data = request.data
        if proposal.created_user == request.user:
            serializer = ProposalSerializer(proposal, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.error, status=status.HTTP_400_BAD_REQUEST)

    # 08-04 건의 글 삭제
    def delete(self, request, proposal_id):
        proposal = get_proposal(proposal_id)
        if proposal.created_user == request.user:
            proposal.delete()
            return Response(msg_success, status=status.HTTP_200_OK)
        else:
            return Response(msg_error, status=status.HTTP_400_BAD_REQUEST)