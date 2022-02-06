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
from django.http import JsonResponse
from classes.models import Class, Class_user
from account.models import User
from .models import Contest, Contest_problem, Exam
from . import serializers

# Create your views here.

class ContestView(APIView):
    #permission_classes = [IsAdminUser]

    def get_object(self, class_id):
        classid = generics.get_object_or_404(Class, id = class_id)
        return classid

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

                data = request.data
                tilte_check = Contest_problem.objects.filter(contest_id = contest_id).filter(title = data['title']).count()
                if tilte_check != 0:
                    return Response({'error':"이미 존재하는 제목입니다."}, status=status.HTTP_400_BAD_REQUEST)

                order = Contest_problem.objects.filter(contest_id=contest_id).count() + 1

                data['contest_id'] = contest_id
                data['order'] = order
                serializer = serializers.ContestProblemSerializer(data=data)
                
                if serializer.is_valid():
                    serializer.save()
                    problem = Contest_problem.objects.filter(contest_id = contest_id).filter(title = data['title'])
                    contest_problem_add = Contest.objects.get(id = contest_id)
                    contest_problem_add.problems.add(problem[0])

                    serializer = serializers.ContestSerializer(contest_problem_add)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
                for contest_problem_list in contest_problem_lists:
                    print(contest_problem_list)
                    contest_problem.append(contest_problem_list)
                
                serializer = serializers.ContestProblemSerializer(contest_problem, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
    
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
                contest.name = data["name"]
                contest.start_time = data["start_time"]
                contest.end_time = data["end_time"]
                contest.is_exam = data["is_exam"]
                contest.save(force_update=True)

                contest_serializer = serializers.ContestSerializer(contest)
                return Response(contest_serializer.data, status=status.HTTP_200_OK)
                
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
                contest.delete()
                return Response("Success", status=status.HTTP_200_OK)
                

class ContestProblemInfoView(APIView):
    #permission_classes = [IsAdminUser]

    def get_object(self, class_id):
        classid = generics.get_object_or_404(Class, id = class_id)
        return classid

    def post(self,request, class_id):
        classid = self.get_object(class_id)

        # 기존 std 삭제
        user = Class.objects.get(id=class_id)
        if user.created_user == request.user:
            user_list = user.users.all()
            for users in user_list:
                if users.privilege == 0:
                    user.users.remove(users.id)
                    users.delete()

        # std 추가
        user_does_not_exist = {}
        user_does_not_exist['does_not_exist'] = []
        user_does_not_exist['is_existed'] = []
        datas = request.data
        user_add = Class.objects.get(id=class_id)
        for data in datas:
            is_check_user = User.objects.filter(username = data['username']).count()
            is_check_class_user = Class_user.objects.filter(username = data['username']).filter(class_id = class_id).count()
            if is_check_user == 0:
                user_does_not_exist['does_not_exist'].append(data['username'])
                continue
            if is_check_class_user != 0:
                user_does_not_exist['is_existed'].append(data['username'])
                continue
            
            data["is_show"] = True
            data["privilege"] = 0
            data["class_id"] = class_id
            
            serializer = serializers.Class_user_Serializer(data=data)
            
            if serializer.is_valid():
                serializer.save()
                user = Class_user.objects.filter(username = data['username']).filter(class_id = class_id)
                user_add.users.add(user[0])
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # 출력
        if (len(user_does_not_exist['does_not_exist']) == 0) and (len(user_does_not_exist['is_existed']) == 0):
            users_datas = user_add.users.all()
            class_Userlist_serializer = serializers.Class_user_Get_Serializer(users_datas, many=True)
            return Response(class_Userlist_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(user_does_not_exist, status=status.HTTP_201_CREATED)