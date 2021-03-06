from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
import jwt
from django.http.response import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Comment, Review
from movies.models import Movie
from .serializers import CommentSerializer, ReviewSerializer


@api_view(['POST'])
def review_create(request):
    # if request.user.is_authenticated:
    serializer = ReviewSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        movie = get_object_or_404(Movie, pk=request.data.get('movie'))
        serializer.save(user=request.user, movie=movie)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    # else:
    #     return Response({'error': '로그인을 해주세요.'}, status=status.HTTP_401_UNAUTHORIZED)


# review detail을 get할 때와 put, delete할 때의 필요 권한이 다른 문제... (@permission_classes([AllowAny]))

# @api_view(['GET'])
# @permission_classes([AllowAny])
# def review_detail(request, review_pk):
#     review = get_object_or_404(Review, pk=review_pk)
#     serializer = ReviewSerializer(review)
#     return Response(serializer.data)


# @api_view(['PUT', 'DELETE'])
# def review_update_or_delete(request, review_pk):
#     review = get_object_or_404(Review, pk=review_pk)

#     def review_update():
#         if request.user == review.user:
#             serializer = ReviewSerializer(instance=review, data=request.data)
#             if serializer.is_valid(raise_exception=True):
#                 serializer.save()
#                 return Response(serializer.data)
#         else:
#             return Response({'error': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
    
#     def review_delete():
#         if request.user == review.user:
#             review.delete()
#             return Response({'id': review_pk}, status=status.HTTP_204_NO_CONTENT)
#         else:
#             return Response({'error': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)

#     if request.method == 'PUT':
#         return review_update()
#     else:
#         return review_delete()


@api_view(['GET', 'PUT', 'DELETE', ])
@permission_classes([AllowAny])
def review_detail(request, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    
    def review_get():
        serializer = ReviewSerializer(review)
        return Response(serializer.data)

    @permission_classes([IsAuthenticated])
    def review_update():
        if request.user == review.user:
            serializer = ReviewSerializer(instance=review, data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data)
        else:
            return Response({'error': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)
    
    @permission_classes([IsAuthenticated])
    def review_delete():
        if request.user == review.user:
            review.delete()
            return Response({'id': review_pk}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'error': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        return review_get()
    elif request.method == 'PUT':
        return review_update()
    else:
        return review_delete()


@api_view(['POST'])
@permission_classes([AllowAny])
def review_likes(request, review_pk):
    review = get_object_or_404(Review, pk=review_pk)

    if review.like_users.filter(pk=request.user.pk).exists():
        # 좋아요 취소
        review.like_users.remove(request.user)
        liked = False
    else:
        # 좋아요 누름
        review.like_users.add(request.user)
        liked = True
    
    like_status = {
        'liked': liked,
        'count': review.like_users.count(),
    }
    return JsonResponse(like_status)


@api_view(['POST'])
def comment_create(request, review_pk):
    # if request.user.is_authenticated: 
    review = get_object_or_404(Review, pk=review_pk)
    serializer = CommentSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save(review=review, user=request.user)
        return Response(serializer.data)
    # else:
    #     return Response({'error': '로그인을 해주세요.'}, status=status.HTTP_401_UNAUTHORIZED) 

@api_view(['DELETE', 'PUT'])
def comment_delete(request, review_pk, comment_pk):
    comment = get_object_or_404(Comment, pk=comment_pk)
    if request.method == 'DELETE':
        if request.user == comment.user:
            comment.delete()
            return Response({'id': comment_pk}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'error': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)

    elif request.method == 'PUT':
        if request.user == comment.user:
            serializer = CommentSerializer(instance=comment, data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
    else:
        return Response({'error': '잘못된 요청입니다.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)