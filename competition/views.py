from competition.serializers import (
    CompetitionDetailSerializer, CompetitionSerializer,
    CompetitionProblemCheckSerializer, CompetitionPutSerializer,
    CompetitionUserGetSerializer, CompetitionUserSerializer,
)
from problem.serializers import ProblemSerializer
from competition.models import Competition, CompetitionUser
from problem.models import Problem
from account.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from utils.permission import *
from utils.get_obj import *
from utils.common import IP_ADDR
import os
import shutil
import uuid
from django.http import Http404
from django.utils import timezone
from rest_framework.permissions import IsAuthenticatedOrReadOnly,IsAuthenticated
from utils.message import *


class CompetitionView(APIView):
    permissions = [IsProfAdminOrReadOnly]
    # 06-00 대회 리스트 조회
    def get(self, request):
        competitions = Competition.objects.filter(problem_id__is_deleted=False).active()
        keyword = request.GET.get('keyword', '')
        if keyword:
            competitions = competitions.filter(problem_id__title__icontains=keyword) # 제목에 keyword가 포함되어 있는 레코드만 필터링
        obj_list = []
        for competition in competitions:
            if competition.is_deleted:
                continue
            obj = {
                "problem": Problem.objects.get(id=competition.problem_id.id),
                "id": competition.id,
                "start_time": competition.start_time,
                "end_time": competition.end_time
            }
            obj_list.append(obj)
        competition_detail_serializer = CompetitionDetailSerializer(obj_list, many=True)

        return Response(competition_detail_serializer.data, status=status.HTTP_200_OK)

    # 06-01 대회 생성
    def post(self, request):
        data = request.data.copy()
        data_str = data['data'].name.split('.')[-1]
        solution_str = data['solution'].name.split('.')[-1]
        if data_str != 'zip':
            return Response(msg_ProblemView_post_e_2, status=status.HTTP_400_BAD_REQUEST)
        if solution_str != 'csv':
            return Response(msg_ProblemView_post_e_3, status=status.HTTP_400_BAD_REQUEST)


        data['created_user'] = request.user
        check = CompetitionProblemCheckSerializer(data=data)
        if check.is_valid():
            # 문제 생성
            problem = ProblemSerializer(data=data)
            if problem.is_valid():
                problem_obj = problem.save()
            else:
                return Response(problem.errors, status=status.HTTP_400_BAD_REQUEST)
            # 대회 생성
            obj = {
                "problem_id" : problem_obj.id,
                "start_time" : data['start_time'],
                "end_time" : data['end_time']
            }
            competition = CompetitionSerializer(data=obj)
            if competition.is_valid():
                competition_obj = competition.save()
                # 대회 참가 - 교수님
                user_data = {
                    "username": request.user.username,
                    "privilege": 2,
                    "competition_id": competition_obj.id
                }
                competition_user_serializer = CompetitionUserSerializer(data=user_data)
                if competition_user_serializer.is_valid():
                    competition_user_serializer.save()
                    # 대회 정보
                    obj = {
                        "problem": problem_obj,
                        "id": competition_obj.id,
                        "start_time": competition_obj.start_time,
                        "end_time": competition_obj.end_time
                    }
                    competition_detail_serializer = CompetitionDetailSerializer(obj)
                    return Response(competition_detail_serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(competition_user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(competition.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(check.errors, status=status.HTTP_400_BAD_REQUEST)

class CompetitionDetailView(APIView):
    permission_classes = [IsCompetitionManagerOrReadOnly]
    # 06-02 대회 개별 조회
    def get(self, request, competition_id):
        competition = get_competition(id=competition_id)
        problem = get_problem(competition.problem_id.id)

        # data_url = "http://{0}/api/problems/{1}/download/data".format(IP_ADDR, problem.id)
        # solution_url = "http://{0}/api/problems/{1}/download/solution".format(IP_ADDR, problem.id)

        obj = {
            "id":competition.id,
            "problem_id":problem.id,
            "title":problem.title,
            "start_time":competition.start_time,
            "end_time":competition.end_time,
            "description":problem.description,
            # "data":data_url,
            "data_description":problem.data_description,
            # "solution":solution_url,
            "evaluation":problem.evaluation
        }

        return Response(obj, status=status.HTTP_200_OK)

    # 06-03-01 대회 개별 수정
    def put(self, request, competition_id):
        competition = get_competition(id=competition_id)
        problem = get_problem(competition.problem_id.id)

        data = request.data
        # problem 수정
        obj = {
            "title": data["title"],
            "description": data["description"],
            "data_description": data["data_description"],
            "evaluation":data["evaluation"],
            "public": False
        }
        if data['data']:
            data_str = data['data'].name.split('.')[-1]
            if data_str != 'zip':
                return Response(msg_ProblemView_post_e_2, status=status.HTTP_400_BAD_REQUEST)
            if os.path.isfile(problem.data.path):
                path = (problem.data.path).split("uploads/problem/")
                path = path[1].split("/", 1)
                shutil.rmtree('./uploads/problem/' + path[0] + '/') # 폴더 삭제 명령어 - shutil
            obj['data'] = data['data']
        if data['solution']:
            solution_str = data['solution'].name.split('.')[-1]
            if solution_str != 'csv':
                return Response(msg_ProblemView_post_e_3, status=status.HTTP_400_BAD_REQUEST)
            if os.path.isfile(problem.solution.path):
                path = (problem.solution.path).split("uploads/solution/")
                path = path[1].split("/", 1)
                shutil.rmtree('./uploads/solution/' + path[0] + '/')
            obj['solution'] = data['solution']

        problem_serializer = ProblemSerializer(problem, data=obj, partial=True)
        if problem_serializer.is_valid():
            problem_obj = problem_serializer.save()
        else:
            return Response(problem_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # competition 수정
        competition_serializer = CompetitionPutSerializer(competition, data=data)
        if competition_serializer.is_valid():
            competition_obj = competition_serializer.save()
        else:
            return Response(competition_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        obj2 = {
            "problem":problem_obj,
            "id":competition_obj.id,
            "start_time":competition_obj.start_time,
            "end_time":competition_obj.end_time
        }
        serializer = CompetitionDetailSerializer(obj2)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 06-03-02 대회 삭제
    def delete(self, request, competition_id):
        competition = get_competition(id=competition_id)
        problem = get_problem(competition.problem_id.id)
        problem.is_deleted = True
        temp = str(uuid.uuid4()).replace("-","")
        problem.title = problem.title + ' - ' + temp
        problem.save()
        return Response({"success": "competition 삭제 완료"}, status=status.HTTP_200_OK)

class CompetitionUserView(APIView):
    permission_classes = [IsAuthenticated]
    # 06-05-01 대회 유저 참가
    def post(self, request, competition_id):
        competition = get_competition(competition_id)

        time_check = timezone.now()
        if (competition.start_time > time_check) or (competition.end_time < time_check):
            return Response(msg_time_error, status=status.HTTP_400_BAD_REQUEST)

        # competition_user에 username이 이미 존재하는지 체크
        if CompetitionUser.objects.filter(username = request.user).filter(competition_id = competition_id).count():
            return Response({"error":"이미 참가한 대회 입니다."}, status=status.HTTP_400_BAD_REQUEST)

        data = {
            "username": request.user.username,
            "privilege": 0,
            "competition_id": competition_id
        }
        serializer = CompetitionUserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 06-05-03 대회 참가자, 관리자 전체 조회
    def get(self, request, competition_id):
        competition = get_competition(competition_id)
        user_list = CompetitionUser.objects.filter(competition_id = competition.id)
        competition_Userlist_serializer = CompetitionUserGetSerializer(user_list, many=True)
        return Response(competition_Userlist_serializer.data, status=status.HTTP_200_OK)

class CompetitionTaView(APIView):
    permission_classes = [IsCompetitionManagerOrReadOnly]
    # 06-05-02 대회 유저 참가
    def post(self, request, competition_id):
        competition = get_competition(competition_id)

        # 0315
        # 기존 TA 삭제
        if (competition.problem_id.created_user == request.user) or request.user.privilege == 2: # 대회 담당 교수, admin인 경우에만
            user_list = CompetitionUser.objects.filter(competition_id=competition.id)
            for users in user_list:
                if users.privilege == 1:
                    users.delete()
        else:
            return Response({'error':"추가 권한이 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

        # TA 추가
        user_does_not_exist = {
            "does_not_exist": [],
            "is_existed": []
        }
        datas = request.data
        for data in datas:
            is_check_user = User.objects.filter(username = data['username']).count()
            is_check_competition_user_ta = CompetitionUser.objects.filter(username = data['username']).filter(competition_id = competition_id).filter(privilege = 1).count()
            if is_check_user == 0:
                user_does_not_exist['does_not_exist'].append(data['username'])
                continue
            if is_check_competition_user_ta:
                user_does_not_exist['is_existed'].append(data['username'])
                continue
            is_check_competition_user = CompetitionUser.objects.filter(username = data['username']).filter(competition_id = competition_id).filter(privilege = 0)
            if is_check_competition_user.count():
                is_check_competition_user[0].delete()

            obj = {
                "username" : data['username'],
                "is_show" : True,
                "privilege" : 1,
                "competition_id" : competition_id
            }

            serializer = CompetitionUserSerializer(data=obj)

            if serializer.is_valid():
                serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # 출력
        if (len(user_does_not_exist['does_not_exist']) == 0) and (len(user_does_not_exist['is_existed']) == 0):
            return Response(msg_success, status=status.HTTP_201_CREATED)
        else:
            return Response(user_does_not_exist, status=status.HTTP_201_CREATED)

