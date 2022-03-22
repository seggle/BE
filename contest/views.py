from multiprocessing import context
from pickle import TRUE
from django.shortcuts import render
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import status
from datetime import datetime
from django.utils import timezone
from django.http import JsonResponse
from classes.models import Class, ClassUser
from account.models import User
from problem.models import Problem
from .models import Contest, ContestProblem
from serializers import ContestSerializer, ContestGetSerializer, ContestPatchSerializer, ContestProblemSerializer, ContestProblemDesSerializer
from utils.get_obj import *
from utils.message import *
from utils.common import IP_ADDR

# Create your views here.

class ContestView(APIView):
    #permission_classes = [IsAdminUser]

    #05-08
    def post(self,request):
        class_id = request.get.GET("class_id")
        class_ = get_class(class_id)
        
        data = request.data
        data['class_id'] = class_id
        serializer = ContestSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED) #client에게 JSON response 전달
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 05-07
    # 비공개 관련 처리 필요함
    def get(self, request):
        class_id = request.get.GET("class_id")
        class_ = get_class(class_id)
        contest = []
        contest_lists = Contest.objects.filter(class_id=class_id)
        for contest_list in contest_lists:
            contest_list_serializer = ContestGetSerializer(contest_list)
            contest.append(contest_list_serializer.data)
        return Response(contest, status=status.HTTP_200_OK)

class ContestCheckView(APIView):
    #permission_classes = [IsAdminUser]

    #05-09
    def patch(self, request):
        # 0315 permission
        class_id = request.get.GET("class_id")
        class_ = get_class(class_id)
        contest_id = request.get.GET("contest_id")
        contest = get_contest(contest_id)

        if contest.class_id.id != class_id:
            return Response(msg_error, status=status.HTTP_400_BAD_REQUEST)

        contest.visible = not contest.visible
        contest = contest.save()
        serializer = ContestSerializer(contest) #Request의 data를 UserSerializer로 변환
        return Response(serializer.data, status=status.HTTP_200_OK)

class ContestProblemView(APIView):
    #permission_classes = [IsAdminUser]

    # 05-13-01
    def post(self,request):
        # permission 해당 Class의 ClassUser privilege 2 이상 & admin 
        class_id = request.get.GET("class_id")
        class_ = get_class(class_id)
        contest_id = request.get.GET("contest_id")
        contest = get_contest(contest_id)

        datas = request.data
        error = {
            "Error_problem_id": []
        }
        for data in datas:
            # exist and Problem id and public and is_deleted is not checking
            problem_data = {}
            problem_data = data
            # problem_id 가 존재하지 않거나, 이미 등록된 경우
            if (Problem.objects.filter(id=data['problem_id']).count() == 0) or (ContestProblem.objects.filter(contest_id=contest_id).filter(problem_id=data['problem_id']).count() != 0):
                error['Error_problem_id'].append(data['problem_id'])
                continue

            order = ContestProblem.objects.filter(contest_id=contest_id).count() + 1
            problem = Problem.objects.get(id=data['problem_id'])
            # 0315 수정 필요
            # if ((problem.public != 1) or (problem.is_deleted != 0)):
            #     error['Error_problem_id'].append(data['problem_id'])
            #     continue

            # 0315
            problem_data = {
                "contest_id" : contest_id,
                "order" : order,
                "title" : problem.title,
                "description" : problem.description,
                "data_description" : problem.data_description
            }
            serializer = ContestProblemSerializer(data=problem_data)

            if serializer.is_valid():
                serializer.save()
                
        if(len(error['Error_problem_id'])) == 0:
            return Response(msg_success, status=status.HTTP_201_CREATED) # 0315
        else:
            return Response(error, status=status.HTTP_201_CREATED) # 0315

    #05-11
    def get(self, request):
        class_id = request.get.GET("class_id")
        class_ = get_class(class_id)
        contest_id = request.get.GET("contest_id")
        contest = get_contest(contest_id)

        contest_problem_lists = ContestProblem.objects.filter(contest_id=contest_id).order_by('order')
        contest_problem_list = []

        if contest_problem_lists.count() == 0:
            return Response(contest_problem_list, status=status.HTTP_200_OK)

        if contest_problem_lists[0].contest.class_.id != class_id:
            return Response(msg_error, status=status.HTTP_400_BAD_REQUEST) # 0315

        start_time = contest_problem_lists[0].contest.start_time
        end_time = contest_problem_lists[0].contest.end_time

        time_check = timezone.now()
        if (start_time > time_check) or (end_time < time_check):
            return Response(msg_contest_time_error, status=status.HTTP_400_BAD_REQUEST)

        for contest_problem in contest_problem_lists:
            contest_problem_json = {
                "id": contest_problem.id,
                "contest_id": contest_problem.contest.id,
                "problem_id": contest_problem.problem.id,
                "title": contest_problem.title,
                "start_time": start_time,
                "end_time": end_time,
                "order": contest_problem.order
            }
            contest_problem_list.append(contest_problem_json)

        return Response(contest_problem_list, status=status.HTTP_200_OK)

    #05-10
    def patch(self, request):
        class_id = request.get.GET("class_id")
        class_ = get_class(class_id)
        contest_id = request.get.GET("contest_id")
        contest = get_contest(contest_id)

        if contest.class_.id != class_id:
            return Response(msg_error, status=status.HTTP_400_BAD_REQUEST)
        
        data = request.data
        serializer = ContestPatchSerializer(contest, data=data)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 05-12
    def delete(self, request):
        class_id = request.get.GET("class_id")
        class_ = get_class(class_id)
        contest_id = request.get.GET("contest_id")
        contest = get_contest(contest_id)
        
        if contest.class_.id != class_id:
            return Response(msg_error, status=status.HTTP_400_BAD_REQUEST)
        contest.is_deleted = True
        contest.save()
        
        return Response(msg_success, status=status.HTTP_200_OK)

class ContestProblemOrderView(APIView):
    #permission_classes = [IsAdminUser]

    #05-13-02
    def patch(self, request):
        class_id = request.get.GET("class_id")
        class_ = get_class(class_id)
        contest_id = request.get.GET("contest_id")
        contest = get_contest(contest_id)

        datas = request.data

        # contest_problem_id check
        for data in datas:
            contest_problem = get_contest_problem(data['id'])
            # url check
            if (contest_problem.contest.id != contest_id) or (contest_problem.contest.class_.id != class_id):
                return Response(msg_error, status=status.HTTP_400_BAD_REQUEST)

        for data in datas:
            contest_problem = ContestProblem.objects.get(id=data['id'])
            contest_problem.order = data['order']
            contest_problem.save()

        return Response(msg_success, status=status.HTTP_200_OK)

class ContestProblemTitleDescptView(APIView):
    #permission_classes = [IsAdminUser]

    #05-13-03
    def patch(self, request):
        class_id = request.get.GET("class_id")
        class_ = get_class(class_id)
        contest_id = request.get.GET("contest_id")
        contest = get_contest(contest_id)
        cp_id = request.get.GET("cp_id")
        contest_problem = get_contest(cp_id)
        
        data = request.data
        
        serializer = ContestProblemDesSerializer(contest_problem, data=data)
        if serializer.is_valid:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.error, status=status.HTTP_400_BAD_REQUEST)

class ContestProblemInfoView(APIView):
    #permission_classes = [IsAdminUser]

    #05-14
    def get(self, request):
        class_id = request.get.GET("class_id")
        class_ = get_class(class_id)
        contest_id = request.get.GET("contest_id")
        contest = get_contest(contest_id)
        cp_id = request.get.GET("cp_id")
        contest_problem = get_contest(cp_id)

        if (contest_problem.contest.id != contest_id) or (contest_problem.contest.class_.id != class_id):
            return Response(msg_error, status=status.HTTP_400_BAD_REQUEST)
        
        time_check = timezone.now()
        if (contest_problem.contest.start_time > time_check) or (contest_problem.contest.end_time < time_check):
            return Response(msg_contest_time_error, status=status.HTTP_400_BAD_REQUEST)

        problem = Problem.objects.get(id=contest_problem.problem.id)
        
        data_url = "http://{0}/api/problems/{1}/download/data".format(IP_ADDR, problem.id)
        cp_json = {
            "id": contest_problem.id,
            "contest_id": contest_problem.contest.id,
            "problem_id": contest_problem.problem.id,
            "title": contest_problem.title,
            "description": contest_problem.description,
            "data_description": contest_problem.data_description,
            "start_time": contest_problem.contest.start_time,
            "end_time": contest_problem.contest.end_time,
            "evaluation": contest_problem.problem.evaluation,
            "problem_data": data_url,
        }

        return Response(cp_json, status=status.HTTP_200_OK)

    #05-15
    def delete(self, request, **kwargs):
        class_id = request.get.GET("class_id")
        class_ = get_class(class_id)
        contest_id = request.get.GET("contest_id")
        contest = get_contest(contest_id)
        cp_id = request.get.GET("cp_id")
        contest_problem = get_contest(cp_id)
        if (contest_problem.contest.id != contest_id) or (contest_problem.contest.class_.id != class_id):
            return Response(msg_error, status=status.HTTP_400_BAD_REQUEST)

        contest_problem_lists = ContestProblem.objects.filter(contest_id=contest_id).order_by('-order')

        for contest_problem_list in contest_problem_lists:
            if(contest_problem_list.order > contest_problem.order):
                contest_problem_list.order = contest_problem_list.order - 1
                contest_problem_list.save()
            else:
                contest_problem.is_deleted = True
                contest_problem.save()
                return Response(msg_success, status=status.HTTP_200_OK)