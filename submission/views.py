from rest_framework.views import APIView
from classes.models import Class
from contest.models import Contest, Contest_problem
from .serializers import SubmissionClassSerializer, PathSerializer
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import status
import uuid


class SubmissionClassView(APIView):
    def get_object_class(self, class_id):
        classid = generics.get_object_or_404(Class, id = class_id)
        return classid

    def get_object_contest(self, contest_id):
        contestid = generics.get_object_or_404(Contest, id = contest_id)
        return contestid

    def get_object_contest_problem(self, cp_id):
        cpid = generics.get_object_or_404(Contest_problem, id = cp_id)
        return cpid

    # 05-16
    def post(self, request, **kwargs):
        if kwargs.get('class_id') is None:
            return Response({"error": "class_id"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            class_id = kwargs.get('class_id')
            classid = self.get_object_class(class_id)
            
            if kwargs.get('contest_id') is None:
                return Response({"error": "contest_id"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                contest_id = kwargs.get('contest_id')
                contestid = self.get_object_contest(contest_id)

                if kwargs.get('cp_id') is None:
                    return Response({"error": "cp_id"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    cp_id = kwargs.get('cp_id')
                    cpid = self.get_object_contest_problem(cp_id)

                    username = kwargs.get('username')
                    
                    if username != request.user.username:
                        return Response({"error": "username"}, status=status.HTTP_400_BAD_REQUEST)
                    
                    contest_problem_id = Contest_problem.objects.get(id=cp_id)
                    
                    if (contest_problem_id.contest_id.id != contest_id) or (contest_problem_id.contest_id.class_id.id != class_id):
                        return Response({"error": "id"}, status=status.HTTP_400_BAD_REQUEST)

                    # 
                    # csv, ipynb file check
                    # 

                    data = request.data.copy()
                    
                    path_json = {}
                    temp = str(uuid.uuid4()).replace("-","")
                    path_json['username'] = request.user
                    path_json['path'] = temp
                    path_json['problem_id'] = contest_problem_id.id
                    path_json['score'] = None
                    path_json['ip_address'] = data['ip_address']
                    # path_json['on_leaderboard'] = request.user
                    # path_json['status'] = 0

                    submission_json = {}
                    submission_json['username'] = request.user
                    submission_json['class_id'] = contest_problem_id.contest_id.class_id.id
                    submission_json['contest_id'] = contest_problem_id.contest_id.id
                    submission_json['c_p_id'] = contest_problem_id.id
                    submission_json['csv'] = data['csv']
                    submission_json['ipynb'] = data['ipynb']
                    

                    path_serializer = PathSerializer(data=path_json)
                    if path_serializer.is_valid():
                        path = path_serializer.save()
                        submission_json['path'] = path.id
                        submission_serializer = SubmissionClassSerializer(data=submission_json)

                        if submission_serializer.is_valid():
                            submission_serializer.save()
                            return Response(submission_serializer.data, status=status.HTTP_200_OK)
                        else:
                            return Response(submission_serializer.errors, status=status.HTTP_400_BAD_REQUEST)