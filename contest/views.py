import os
import shutil
from multiprocessing import context
from pickle import TRUE

from django.http import JsonResponse
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.utils import timezone
import seggle.settings
from problem.models import Problem
from problem.serializers import ProblemPutSerializer
from utils.pagination import PaginationHandlerMixin, BasicPagination, ListPagination
from .models import Contest, ContestProblem
from .serializers import ContestSerializer, ContestPatchSerializer, ContestProblemPostSerializer, \
    ContestProblemDesSerializer, ContestProblemDesEvaluateSerializer, ContestProblemSerializer
from utils.get_obj import *
from utils.message import *
from utils.common import IP_ADDR
from utils.permission import *


# Create your views here.

class ContestView(APIView, PaginationHandlerMixin):
    permission_classes = [IsSafeMethod | IsClassProfOrTA | IsAdmin]
    pagination_class = BasicPagination

    # 05-08
    # 비공개 관련 처리 필요함
    def get(self, request: Request, class_id: int) -> Response:
        contest_lists = Contest.objects.filter(class_id=class_id).order_by("start_time").active()

        page = self.paginate_queryset(contest_lists)
        if page is not None:
            serializer = self.get_paginated_response(ContestSerializer(page, many=True).data)
        else:
            serializer = ContestSerializer(contest_lists)

        return Response(serializer.data, status=status.HTTP_200_OK)

    # 05-09
    def post(self, request: Request, class_id: int) -> Response:
        class_ = get_class(class_id)

        data = request.data.copy()
        data['class_id'] = class_id

        serializer = ContestSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContestCheckView(APIView):
    permission_classes = [IsClassProfOrTA | IsAdmin]

    # 05-10
    def patch(self, request: Request, class_id: int, contest_id: int) -> Response:
        # 0315 permission
        contest = get_contest(contest_id)

        if contest.class_id.id != class_id:
            return Response(msg_error_invalid_contest, status=status.HTTP_400_BAD_REQUEST)

        contest.visible = not contest.visible
        contest.save()

        return Response(msg_success_check_private if not contest.visible else msg_success_check_public,
                        status=status.HTTP_200_OK)


class ContestProblemView(APIView, PaginationHandlerMixin):
    permission_classes = [IsSafeMethod | IsClassProfOrTA | IsAdmin]
    pagination_class = BasicPagination

    # 05-12
    def get(self, request: Request, class_id: int, contest_id: int) -> Response or JsonResponse:
        contest = get_contest(contest_id)

        time_check = timezone.now()
        if (contest.start_time > time_check) or (contest.end_time < time_check):
            return Response(msg_time_error, status=status.HTTP_400_BAD_REQUEST)

        contest_problem_lists = ContestProblem.objects.filter(contest_id=contest_id).order_by('order').active()
        contest_problem_list = []

        problem_count = contest_problem_lists.count()

        if problem_count > 0:
            if contest_problem_lists[0].contest_id.class_id.id != class_id:
                return Response(msg_error, status=status.HTTP_400_BAD_REQUEST)

            for contest_problem in contest_problem_lists:
                if contest_problem.problem_id.is_deleted:
                    continue
                contest_problem_json = {
                    "id": contest_problem.id,
                    "contest_id": contest_problem.contest_id.id,
                    "problem_id": contest_problem.problem_id.id,
                    "title": contest_problem.title,
                    "start_time": contest.start_time,
                    "end_time": contest.end_time,
                    "order": contest_problem.order
                }
                contest_problem_list.append(contest_problem_json)

        list_paginator = ListPagination(request)
        p_size = seggle.settings.REST_FRAMEWORK.get('PAGE_SIZE', 15)

        return list_paginator.paginate_list(
            contest_problem_list, p_size, int(request.GET.get('page', default=1)))

    # 05-13-01
    def post(self, request: Request, class_id: int, contest_id: int) -> Response:
        # permission 해당 Class의 ClassUser privilege 2 이상 & admin

        datas = request.data
        error = {
            "Error_problem_id": []
        }
        for data in datas.get('problem_id'):
            pro_id = int(data)
            # exist and Problem id and public and is_deleted is not checking
            # problem_id 가 존재하지 않거나, 이미 등록된 경우
            if Problem.objects.filter(id=pro_id).active().count() == 0 or \
               ContestProblem.objects.filter(contest_id=contest_id).filter(problem_id=pro_id).active().count() != 0:
                error['Error_problem_id'].append(data)
                continue

            order = ContestProblem.objects.filter(contest_id=contest_id).active().count() + 1
            problem = Problem.objects.get(id=pro_id)
            # 0315 수정 필요
            # if ((problem.public != 1) or (problem.is_deleted != 0)):
            #     error['Error_problem_id'].append(data['problem_id'])
            #     continue

            problem_data = {
                "contest_id": contest_id,
                "problem_id": pro_id,
                "order": order,
                "title": problem.title,
                "description": problem.description,
                "data_description": problem.data_description
            }
            serializer = ContestProblemPostSerializer(data=problem_data)

            if serializer.is_valid():
                serializer.save()

        if len(error.get('Error_problem_id')) == 0:
            return Response(msg_success_create, status=status.HTTP_201_CREATED)
        else:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

    # 05-11
    def patch(self, request: Request, class_id: int, contest_id: int) -> Response:
        contest = get_contest(contest_id)

        if contest.class_id.id != class_id:
            return Response(msg_error, status=status.HTTP_400_BAD_REQUEST)

        data = request.data
        obj = {
            'id': contest.id,
            'name': data.get('name', contest.name),
            'start_time': data.get('start_time', contest.start_time),
            'end_time': data.get('end_time', contest.end_time),
            'visible': data.get('visible', contest.visible),
            'is_exam': data.get('is_exam', contest.is_exam)
        }
        serializer = ContestPatchSerializer(contest, data=obj, partial=True)
        if serializer.is_valid():
            serializer.save()
        else:
            Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.data, status=status.HTTP_200_OK)

    # 05-13
    def delete(self, request: Request, class_id: int, contest_id: int) -> Response:
        contest = get_contest(contest_id)

        if contest.class_id.id != class_id:
            return Response(msg_error_invalid_contest, status=status.HTTP_400_BAD_REQUEST)
        contest.is_deleted = True
        contest.save()

        return Response(msg_success_delete, status=status.HTTP_200_OK)


class ContestProblemOrderView(APIView):
    permission_classes = [IsClassProfOrTA | IsAdmin]

    # 05-13-02
    def patch(self, request: Request, class_id: int, contest_id: int) -> Response:

        datas = request.data

        # contest_problem_id check
        for data in datas:
            contest_problem = get_contest_problem(data.get('id'))
            # url check
            if (contest_problem.contest_id.id != contest_id) or (contest_problem.contest_id.class_id.id != class_id):
                return Response(msg_error, status=status.HTTP_400_BAD_REQUEST)

        for data in datas:
            contest_problem = ContestProblem.objects.get(id=data.get('id'))
            contest_problem.order = data.get('order')
            contest_problem.save()

        return Response(msg_success, status=status.HTTP_200_OK)


class ContestProblemInfoView(APIView):
    permission_classes = [IsSafeMethod | IsClassProfOrTA | IsAdmin]

    # 05-14
    def get(self, request: Request, class_id: int, contest_id: int, cp_id: int) -> Response:
        contest_problem = get_contest_problem(cp_id)

        if (contest_problem.contest_id.id != contest_id) or (contest_problem.contest_id.class_id.id != class_id):
            return Response(msg_error_id, status=status.HTTP_400_BAD_REQUEST)

        time_check = timezone.now()
        if (contest_problem.contest_id.start_time > time_check) or (contest_problem.contest_id.end_time < time_check):
            return Response(msg_time_error, status=status.HTTP_400_BAD_REQUEST)

        problem = Problem.objects.get(id=contest_problem.problem_id.id)

        # data_url = "http://{0}/api/problems/{1}/download/data".format(IP_ADDR, problem.id)
        cp_json = {
            "id": contest_problem.id,
            "contest_id": contest_problem.contest_id.id,
            "problem_id": contest_problem.problem_id.id,
            "title": contest_problem.title,
            "description": contest_problem.description,
            "data_description": contest_problem.data_description,
            "start_time": contest_problem.contest_id.start_time,
            "end_time": contest_problem.contest_id.end_time,
            "evaluation": contest_problem.problem_id.evaluation,
            # "problem_data": data_url,
        }

        return Response(cp_json, status=status.HTTP_200_OK)

    # 05-15
    def delete(self, request: Request, class_id: int, contest_id: int, cp_id: int) -> Response:
        contest_problem = ContestProblem.objects.filter(contest_id=contest_id, cp_id=cp_id).active().first()

        if contest_problem is None:
            return Response(msg_error_problem_not_found, status=status.HTTP_404_NOT_FOUND)

        problem_id = contest_problem.problem_id.id
        if contest_problem.contest_id.id != contest_id or contest_problem.contest_id.class_id.id != class_id:
            return Response(msg_error_invalid_url, status=status.HTTP_400_BAD_REQUEST)

        contest_problem_lists = ContestProblem.objects.filter(contest_id=contest_id).order_by('-order').active()

        for con_p in contest_problem_lists:
            if con_p.order > contest_problem.order:
                con_p.order = con_p.order - 1
                con_p.save()
            else:
                contest_problem.is_deleted = True
                contest_problem.save()

                p = get_problem(id=problem_id)
                p.is_deleted = True
                p.save()

                return Response(msg_success_delete, status=status.HTTP_200_OK)

    # 05-13-03
    def put(self, request: Request, class_id: int, contest_id: int, cp_id: int) -> Response:
        contest_problem = get_contest_problem(cp_id)
        problem = get_problem(id=contest_problem.problem_id.id)

        if contest_problem.contest_id.id != contest_id or contest_problem.contest_id.class_id.id != class_id:
            return Response(msg_error_invalid_url, status=status.HTTP_400_BAD_REQUEST)

        data = request.data

        if len(request.data) == 0:
            return Response(msg_error_no_request, status=status.HTTP_400_BAD_REQUEST)

        obj = {
            "title": data.get('title', contest_problem.title),
            "description": data.get('description', contest_problem.description),
            "data_description": data.get('data_description', contest_problem.data_description),
            'evaluation': data.get('evaluation', problem.evaluation),
            "public": data.get("public", problem.public),
        }

        if data.get('data', '') != '':
            data_str = data['data'].name.split('.')[-1]
            print(data_str)
            if data_str != 'zip':
                return Response(msg_ProblemView_post_e_2, status=status.HTTP_400_BAD_REQUEST)
            # 폴더 삭제
            if os.path.isfile(problem.data.path):
                if os.name == 'posix':
                    path = problem.data.path.split("uploads/problem/")
                    path = path[1].split("/", 1)
                    shutil.rmtree('./uploads/problem/' + path[0] + '/')  # 폴더 삭제 명령어 - shutil
                else:
                    path = os.path.normpath(problem.data.path.split('problem')[1])
                    path = path.split("\\")[1]
                    shutil.rmtree('./uploads/problem/' + path + '/')  # 폴더 삭제 명령어 - shutil

        if data.get('solution', '') != '':
            solution_str = data['solution'].name.split('.')[-1]
            if solution_str != 'csv':
                return Response(msg_ProblemView_post_e_3, status=status.HTTP_400_BAD_REQUEST)
            if os.path.isfile(problem.solution.path):
                if os.name == 'posix':
                    path = problem.solution.path.split("uploads/solution/")
                    path = path[1].split("/", 1)
                    shutil.rmtree('./uploads/solution/' + path[0] + '/')
                else:
                    path = os.path.normpath(problem.solution.path.split('solution')[1])
                    path = path.split("\\")[1]
                    shutil.rmtree('./uploads/solution/' + path + '/')  # 폴더 삭제 명령어 - shutil

        serializer = ProblemPutSerializer(problem, data=request.data, partial=True)
        conserializer = ContestProblemSerializer(contest_problem, data=obj, partial=True)

        if serializer.is_valid() and conserializer.is_valid():
            serializer.save()
            conserializer.save()

            rt = {
                'id': problem.id,
                'cp_id': conserializer.data.get('id'),
                'order': conserializer.data.get('order'),
                'title': serializer.data.get('title'),
                'description': serializer.data.get('description'),
                'data_description': serializer.data.get('data_description'),
                'data': serializer.data.get('data'),
                'solution': serializer.data.get('solution'),
                'evaluation': serializer.data.get('evaluation'),
                'public': serializer.data.get('public'),
            }
            return Response(rt, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
