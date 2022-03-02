from multiprocessing import context
from pickle import TRUE
from django.shortcuts import render
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken, OutstandingToken, BlacklistedToken
from rest_framework import status
from datetime import datetime
from django.utils import timezone
from django.http import JsonResponse
from classes.models import Class, Class_user
from account.models import User
from problem.models import Problem
from .models import Contest, Contest_problem
from . import serializers

# Create your views here.

class ContestView(APIView):
    #permission_classes = [IsAdminUser]

    def get_object(self, class_id):
        classid = generics.get_object_or_404(Class, id = class_id)
        return classid
    #05-08
    def post(self,request, **kwargs):
        if kwargs.get('class_id') is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            class_id = kwargs.get('class_id')
            classid = self.get_object(class_id)
            #class_list_serializer = serializers.ClassSerializer(Class.objects.get(id=class_id))
            data = request.data
            data['class_id'] = class_id
            serializer = serializers.ContestSerializer(data=data)
            
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED) #client에게 JSON response 전달
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #05-07
    #비공개 관련 처리 필요함
    def get(self, request, **kwargs):
        if kwargs.get('class_id') is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            class_id = kwargs.get('class_id')
            classid = self.get_object(class_id)
            contest = []
            contest_lists = Contest.objects.filter(class_id=class_id)
            for contest_list in contest_lists:
                contest_list_serializer = serializers.ContestGetSerializer(contest_list)
                contest.append(contest_list_serializer.data)
            return Response(contest, status=status.HTTP_200_OK)
    
class ContestCheckView(APIView):
    #permission_classes = [IsAdminUser]

    def get_object_class(self, class_id):
        classid = generics.get_object_or_404(Class, id = class_id)
        return classid

    def get_object_contest(self, contest_id):
        contestid = generics.get_object_or_404(Contest, id = contest_id)
        return contestid

    #05-09
    def patch(self, request, **kwargs):
        if kwargs.get('class_id') is None:
            return Response("Fail", status=status.HTTP_400_BAD_REQUEST)
        else:
            class_id = kwargs.get('class_id')
            classid = self.get_object_class(class_id)
            
            if kwargs.get('contest_id') is None:
                return Response("Fail", status=status.HTTP_400_BAD_REQUEST)
            else:
                contest_id = kwargs.get('contest_id')
                contestid = self.get_object_contest(contest_id)

                user = Contest.objects.get(id=contest_id)

                if user.class_id.id != class_id:
                    return Response("Fail", status=status.HTTP_400_BAD_REQUEST)
                
                user.visible = not user.visible
                user.save(force_update=True)
                serializer = serializers.ContestSerializer(Contest.objects.get(id=contest_id)) #Request의 data를 UserSerializer로 변환
                return Response(serializer.data, status=status.HTTP_200_OK)

                # if user.created_user == request.user:
                #     user.visible = not user.visible
                #     user.save(force_update=True)
                #     serializer = serializers.FaqSerializer(Faq.objects.get(id=faq_id)) #Request의 data를 UserSerializer로 변환
                #     return Response(serializer.data, status=status.HTTP_200_OK)
                # else:
                #     return Response("Fail", status=status.HTTP_400_BAD_REQUEST)

class ContestProblemView(APIView):
    #permission_classes = [IsAdminUser]

    def get_object_class(self, class_id):
        classid = generics.get_object_or_404(Class, id = class_id)
        return classid

    def get_object_contest(self, contest_id):
        contestid = generics.get_object_or_404(Contest, id = contest_id)
        return contestid

    #05-13-01
    def post(self,request, **kwargs):
        if kwargs.get('class_id') is None:
            return Response("Fail", status=status.HTTP_400_BAD_REQUEST)
        else:
            class_id = kwargs.get('class_id')
            classid = self.get_object_class(class_id)
            
            if kwargs.get('contest_id') is None:
                return Response("Fail", status=status.HTTP_400_BAD_REQUEST)
            else:
                contest_id = kwargs.get('contest_id')
                contestid = self.get_object_contest(contest_id)

                datas = request.data
                # tilte_check = Contest_problem.objects.filter(contest_id = contest_id).filter(title = data['title']).count()
                # if tilte_check != 0:
                #     return Response({'error':"이미 존재하는 제목입니다."}, status=status.HTTP_400_BAD_REQUEST)
                error = {}
                error['Error_problem_id'] = []
                for data in datas:
                    # exist and Problem id and public and is_deleted is not checking
                    problem_data = {}
                    problem_data = data
                    if (Problem.objects.filter(id=data['problem_id']).count() == 0) or (Contest_problem.objects.filter(contest_id=contest_id).filter(problem_id=data['problem_id']).count() != 0):
                        error['Error_problem_id'].append(data['problem_id'])
                        continue

                    order = Contest_problem.objects.filter(contest_id=contest_id).count() + 1
                    problem = Problem.objects.get(id=data['problem_id'])
                    if (problem.public != 1) or (problem.is_deleted != 0):
                        error['Error_problem_id'].append(data['problem_id'])
                        continue
                    
                    problem_data['contest_id'] = contest_id
                    problem_data['order'] = order
                    problem_data['title'] = problem.title
                    problem_data['description'] = problem.description
                    problem_data['data_description'] = problem.data_description
                    serializer = serializers.ContestProblemSerializer(data=problem_data)
                    
                    if serializer.is_valid():
                        serializer.save()
                        problem = Contest_problem.objects.filter(contest_id = contest_id).filter(title = problem_data['title'])
                        contest_problem_add = Contest.objects.get(id = contest_id)
                        contest_problem_add.problems.add(problem[0])
                if(len(error['Error_problem_id'])) == 0:
                    return Response("Success", status=status.HTTP_201_CREATED)
                else:
                    return Response(error, status=status.HTTP_201_CREATED)

    #05-11
    def get(self, request, **kwargs):
        if kwargs.get('class_id') is None:
            return Response("Fail", status=status.HTTP_400_BAD_REQUEST)
        else:
            class_id = kwargs.get('class_id')
            classid = self.get_object_class(class_id)
            
            if kwargs.get('contest_id') is None:
                return Response("Fail", status=status.HTTP_400_BAD_REQUEST)
            else:
                contest_id = kwargs.get('contest_id')
                contestid = self.get_object_contest(contest_id)

                

                contest_problem_lists = Contest_problem.objects.filter(contest_id=contest_id).order_by('order')
                contest_problem = []
                
                if contest_problem_lists.count() == 0:
                    return Response(contest_problem, status=status.HTTP_200_OK)
                
                if contest_problem_lists[0].contest_id.class_id.id != class_id:
                    return Response("Fail", status=status.HTTP_400_BAD_REQUEST)
                
                start_time = contest_problem_lists[0].contest_id.start_time
                end_time = contest_problem_lists[0].contest_id.end_time
                #print(start_time)
                
                for contest_problem_list in contest_problem_lists:
                    #print(contest_problem_list)
                    cp_json = {
                        "id": contest_problem_list.id,
                        "contest_id": contest_problem_list.contest_id.id,
                        "problem_id": contest_problem_list.problem_id.id,
                        "title": contest_problem_list.title,
                        "start_time": start_time,
                        "end_time": end_time,
                        "order": contest_problem_list.order
                    }
                    contest_problem.append(cp_json)
                
                #serializer = serializers.ContestProblemSerializer(contest_problem, many=True)
                return Response(contest_problem, status=status.HTTP_200_OK)
    
    #05-10
    def patch(self, request, **kwargs):
        if kwargs.get('class_id') is None:
            return Response("Fail", status=status.HTTP_400_BAD_REQUEST)
        else:
            class_id = kwargs.get('class_id')
            classid = self.get_object_class(class_id)
            
            if kwargs.get('contest_id') is None:
                return Response("Fail", status=status.HTTP_400_BAD_REQUEST)
            else:
                contest_id = kwargs.get('contest_id')
                contestid = self.get_object_contest(contest_id)

                data = request.data
                contest = Contest.objects.get(id=contest_id)

                if contest.class_id.id != class_id:
                    return Response("Fail", status=status.HTTP_400_BAD_REQUEST)
                
                contest.name = data["name"]
                contest.start_time = data["start_time"]
                contest.end_time = data["end_time"]
                contest.is_exam = data["is_exam"]
                contest.visible = data["visible"]
                contest.save(force_update=True)

                contest_serializer = serializers.ContestSerializer(contest)
                return Response(contest_serializer.data, status=status.HTTP_200_OK)

    #05-12    
    def delete(self, request, **kwargs):
        if kwargs.get('class_id') is None:
            return Response("Fail", status=status.HTTP_400_BAD_REQUEST)
        else:
            class_id = kwargs.get('class_id')
            classid = self.get_object_class(class_id)
            
            if kwargs.get('contest_id') is None:
                return Response("Fail", status=status.HTTP_400_BAD_REQUEST)
            else:
                contest_id = kwargs.get('contest_id')
                contestid = self.get_object_contest(contest_id)

                contest = Contest.objects.get(id=contest_id)
                if contest.class_id.id != class_id:
                    return Response("Fail", status=status.HTTP_400_BAD_REQUEST)
                
                contest.delete()
                return Response("Success", status=status.HTTP_200_OK)
                
class ContestProblemOrderView(APIView):
    #permission_classes = [IsAdminUser]

    def get_object_class(self, class_id):
        classid = generics.get_object_or_404(Class, id = class_id)
        return classid

    def get_object_contest(self, contest_id):
        contestid = generics.get_object_or_404(Contest, id = contest_id)
        return contestid

    #05-13-02
    def patch(self, request, **kwargs):
        if kwargs.get('class_id') is None:
            return Response("Fail", status=status.HTTP_400_BAD_REQUEST)
        else:
            class_id = kwargs.get('class_id')
            classid = self.get_object_class(class_id)
            
            if kwargs.get('contest_id') is None:
                return Response("Fail", status=status.HTTP_400_BAD_REQUEST)
            else:
                contest_id = kwargs.get('contest_id')
                contestid = self.get_object_contest(contest_id)

                datas = request.data
                error = {}
                error['Error'] = []
                error['Error_Contest_Problem_id'] = []

                for data in datas:
                    if Contest_problem.objects.filter(id=data['id']).count() == 0:
                        error['Error_Contest_Problem_id'].append(data['id'])
                        continue
                    contest_problem = Contest_problem.objects.get(id=data['id'])
                    
                    if (contest_problem.contest_id.id != contest_id) or (contest_problem.contest_id.class_id.id != class_id):
                        error['Error'].append(data['id'])
                        continue
                    
                    # if (Problem.objects.filter(id=data['problem_id']).count() == 0) or (Contest_problem.objects.filter(contest_id=contest_id).filter(problem_id=data['problem_id']).count() == 0):
                    #     error['Error_Problem_id'].append(data['problem_id'])
                    #     continue

                    # tilte_check = Contest_problem.objects.filter(contest_id = contest_id).filter(title = data['title']).count()
                    # if tilte_check != 0:
                    #     error['Error_title_is_existed'].append(data['title'])
                    #     continue
                        # return Response({'error':"이미 존재하는 제목입니다."}, status=status.HTTP_400_BAD_REQUEST)
                    contest_problem.order = data['order']
                    contest_problem.save(force_update=True)

                if (len(error['Error']) != 0) or (len(error['Error_Contest_Problem_id']) != 0):
                    return Response(error, status=status.HTTP_200_OK)
                else:
                    return Response("Success", status=status.HTTP_200_OK)

class ContestProblemTitleDescptView(APIView):
    #permission_classes = [IsAdminUser]

    def get_object_class(self, class_id):
        classid = generics.get_object_or_404(Class, id = class_id)
        return classid

    def get_object_contest(self, contest_id):
        contestid = generics.get_object_or_404(Contest, id = contest_id)
        return contestid

    #05-13-03
    def patch(self, request, **kwargs):
        if kwargs.get('class_id') is None:
            return Response("Fail", status=status.HTTP_400_BAD_REQUEST)
        else:
            class_id = kwargs.get('class_id')
            classid = self.get_object_class(class_id)
            
            if kwargs.get('contest_id') is None:
                return Response("Fail", status=status.HTTP_400_BAD_REQUEST)
            else:
                contest_id = kwargs.get('contest_id')
                contestid = self.get_object_contest(contest_id)

                datas = request.data
                error = {}
                error['Error'] = []
                error['Error_Contest_Problem_id'] = []

                for data in datas:
                    if Contest_problem.objects.filter(id=data['id']).count() == 0:
                        error['Error_Contest_Problem_id'].append(data['id'])
                        continue
                    contest_problem = Contest_problem.objects.get(id=data['id'])
                    
                    if (contest_problem.contest_id.id != contest_id) or (contest_problem.contest_id.class_id.id != class_id):
                        error['Error'].append(data['id'])
                        continue
                    
                    # if (Problem.objects.filter(id=data['problem_id']).count() == 0) or (Contest_problem.objects.filter(contest_id=contest_id).filter(problem_id=data['problem_id']).count() == 0):
                    #     error['Error_Problem_id'].append(data['problem_id'])
                    #     continue

                    # tilte_check = Contest_problem.objects.filter(contest_id = contest_id).filter(title = data['title']).count()
                    # if tilte_check != 0:
                    #     error['Error_title_is_existed'].append(data['title'])
                    #     continue
                        # return Response({'error':"이미 존재하는 제목입니다."}, status=status.HTTP_400_BAD_REQUEST)
                    contest_problem.title = data['title']
                    contest_problem.description = data['description']
                    contest_problem.data_description = data['data_description']
                    contest_problem.save(force_update=True)

                if (len(error['Error']) != 0) or (len(error['Error_Contest_Problem_id']) != 0):
                    return Response(error, status=status.HTTP_200_OK)
                else:
                    return Response("Success", status=status.HTTP_200_OK)

class ContestProblemInfoView(APIView):
    #permission_classes = [IsAdminUser]

    def get_object_class(self, class_id):
        classid = generics.get_object_or_404(Class, id = class_id)
        return classid

    def get_object_contest(self, contest_id):
        contestid = generics.get_object_or_404(Contest, id = contest_id)
        return contestid

    def get_object_contest_problem(self, cp_id):
        cpid = generics.get_object_or_404(Contest_problem, id = cp_id)
        return cpid

    #05-14
    def get(self, request, **kwargs):
        if kwargs.get('class_id') is None:
            return Response("Fail", status=status.HTTP_400_BAD_REQUEST)
        else:
            class_id = kwargs.get('class_id')
            classid = self.get_object_class(class_id)
            
            if kwargs.get('contest_id') is None:
                return Response("Fail", status=status.HTTP_400_BAD_REQUEST)
            else:
                contest_id = kwargs.get('contest_id')
                contestid = self.get_object_contest(contest_id)

                if kwargs.get('cp_id') is None:
                    return Response("Fail", status=status.HTTP_400_BAD_REQUEST)
                else:
                    cp_id = kwargs.get('cp_id')
                    cpid = self.get_object_contest_problem(cp_id)

                    contest_problem = Contest_problem.objects.get(id=cp_id)

                    if (contest_problem.contest_id.id != contest_id) or (contest_problem.contest_id.class_id.id != class_id):
                        return Response("Fail", status=status.HTTP_400_BAD_REQUEST)
                    
                    # print(timezone.now())
                    time_check = timezone.now()
                    if (contest_problem.contest_id.start_time > time_check) or (contest_problem.contest_id.end_time < time_check):
                        return Response({'error': 'time error!'}, status=status.HTTP_400_BAD_REQUEST)

                    problem = Problem.objects.get(id=contest_problem.problem_id.id)
                    
                    ip_addr = "3.37.186.158"
                    path = str(problem.data.path).replace("/home/ubuntu/BE/uploads/", "")
                    url = "http://{0}/{1}" . format (ip_addr, path)

                    cp_json = {
                        "id": contest_problem.id,
                        "contest_id": contest_problem.contest_id.id,
                        "problem_id": contest_problem.problem_id.id,
                        "title": contest_problem.title,
                        "description": contest_problem.description,
                        "data_description": contest_problem.data_description,
                        "start_time": contest_problem.contest_id.start_time,
                        "end_time": contest_problem.contest_id.end_time,
                        # "problem_data": problem.data.path,
                        "problem_data": url,
                    }

                    #serializer = serializers.ContestProblemSerializer(contest_problem, many=True)
                    return Response(cp_json, status=status.HTTP_200_OK)
    
    #05-15
    def delete(self, request, **kwargs):
        if kwargs.get('class_id') is None:
            return Response("Fail", status=status.HTTP_400_BAD_REQUEST)
        else:
            class_id = kwargs.get('class_id')
            classid = self.get_object_class(class_id)
            
            if kwargs.get('contest_id') is None:
                return Response("Fail", status=status.HTTP_400_BAD_REQUEST)
            else:
                contest_id = kwargs.get('contest_id')
                contestid = self.get_object_contest(contest_id)

                if kwargs.get('cp_id') is None:
                    return Response("Fail", status=status.HTTP_400_BAD_REQUEST)
                else:
                    cp_id = kwargs.get('cp_id')
                    cpid = self.get_object_contest_problem(cp_id)
                    
                    contest_problem = Contest_problem.objects.get(id=cp_id)
                    if (contest_problem.contest_id.id != contest_id) or (contest_problem.contest_id.class_id.id != class_id):
                        return Response("Fail", status=status.HTTP_400_BAD_REQUEST)
                    

                    contest_problem_lists = Contest_problem.objects.filter(contest_id=contest_id).order_by('-order')
                    
                    for contest_problem_list in contest_problem_lists:
                        if(contest_problem_list.order > contest_problem.order):
                            contest_problem_list.order = contest_problem_list.order - 1
                            contest_problem_list.save(force_update=True)
                        else:
                            contest_problem.delete()
                            return Response("Success", status=status.HTTP_200_OK)