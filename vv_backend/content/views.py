from django.shortcuts import render
from rest_framework.generics import ListAPIView
from content.models.content import Video
from .serializers import VideoSerializer

class VideoListView(ListAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer