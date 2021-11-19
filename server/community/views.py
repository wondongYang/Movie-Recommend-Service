from django.shortcuts import get_object_or_404

from django.views.decorators.http import require_POST
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Review
from movies.models import Movie
from .serializers import CommentSerializer, ReviewSerializer


@api_view(['POST'])
def review_create(request):
    if request.user.is_authenticated:
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user)
            return Response(serializer.data)
    else:
        return Response({'error': '로그인을 해주세요.'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET', 'PUT', 'DELETE'])
def review_detail_or_update_or_delete(request, review_pk):
    review = get_object_or_404(Review, pk=review_pk)

    def review_detail():
        serializer = ReviewSerializer(review)
        return Response(serializer.data)

    def review_update():
        if request.user == review.user:
            serializer = ReviewSerializer(instance=review, data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data)
        else:
            return Response({'detail': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDON)
    
    def review_delete():
        if request.user == review.user:
            review.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'detail': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDON)

    if request.method == 'GET':
        return review_detail()
    elif request.method == 'PUT':
        return review_update()
    else:
        return review_delete()


@api_view(['POST'])
def comment_create(request, review_pk):
    if request.user.is_authenticated: 
        review = get_object_or_404(Review, pk=review_pk)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(review=review)
            return Response(serializer.data)
    else:
        return Response({'error': '로그인을 해주세요.'}, status=status.HTTP_401_UNAUTHORIZED) 

@api_view(['POST'])
def comment_delete(request, comment_pk):
    comment = get_object_or_404(Review, pk=comment_pk)
    if request.user == comment.user:
        comment.delete()
        return Response({ 'id': comment_pk })
    else:
        return Response({'detail': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDON)