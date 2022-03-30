from multiprocessing import context
from pickle import TRUE
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from ..models import Faq
from ..serializers import FaqSerializer
from rest_framework.permissions import AllowAny
# Create your views here.

class FaqView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        faq_list = Faq.objects.exclude(visible=False)
        faq_list_serializer = FaqSerializer(faq_list, many=True)
        return Response(faq_list_serializer.data, status=status.HTTP_200_OK)
        
