from rest_framework.views import APIView
from ..models import Problem
from ..serializers import ProblemGenerateSerializer, ProblemSerializer, AllProblemSerializer, ProblemPatchSerializer
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404


class ProblemView(APIView):
    serializer_class = ProblemGenerateSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ProblemGenerateSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            problem = serializer.save(created_user=request.user)
            data["id"] = problem.id
        else:
            data = serializer.errors

        return Response(data)

    def get(self, request):
        problems = Problem.objects.all()
        serializer = AllProblemSerializer(problems, many=True)
        return Response(serializer.data)


class ProblemDetailView(APIView):
    serializer_class = ProblemPatchSerializer
    permission_classes = [AllowAny]

    def get_object(self, problem_id):
        problem = get_object_or_404(Problem,id = problem_id)
        return problem

    def get(self, request, problem_id):
        problem = self.get_object(problem_id)
        serializer = ProblemSerializer(problem)
        return Response(serializer.data)

    def put(self, request, problem_id):
        problem = self.get_object(problem_id)
        data = request.data
        obj = {}
        obj["title"] = data["title"]
        obj["description"] = data["description"]
        obj["data_description"] = data["data_description"]
        obj["public"] = data["public"]
        serializer = ProblemPatchSerializer(problem, data=obj)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            data = serializer.errors()
            return Response(data)

    def delete(self,request,problem_id):
        problem = self.get_object(problem_id)
        problem.delete()
        return Response({True})

class ProblemVisibilityView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, problem_id):
        problem = get_object_or_404(Problem,id = problem_id)
        return problem

    def post(self,request,problem_id):
        problem = self.get_object(problem_id)
        if problem.public:
            problem.public = False
        else:
            problem.public = True
        problem.save()
        return Response(data=ProblemSerializer(problem).data)

