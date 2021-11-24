from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .serializers import UserSerializer, UserProfileSerializer
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
	#1-1. Client에서 온 데이터를 받아서
    password = request.data.get('password')
    password_confirmation = request.data.get('passwordConfirmation')
		
	#1-2. 패스워드 일치 여부 체크
    if password != password_confirmation:
        return Response({'error': '비밀번호가 일치하지 않습니다.'}, status=status.HTTP_400_BAD_REQUEST)
    
    if len(password) < 8:
        return Response({'error': '비밀번호는 8자리 이상이어야 합니다.'}, status=status.HTTP_400_BAD_REQUEST)

    if len(request.data.get('username')) < 4:
        return Response({'error': '계정명은 4글자 이상이어야 합니다.'}, status=status.HTTP_400_BAD_REQUEST)
		
	#2. UserSerializer를 통해 데이터 직렬화
    serializer = UserSerializer(data=request.data)
    
	#3. validation 작업 진행 -> password도 같이 직렬화 진행
    if serializer.is_valid(raise_exception=True):
        user = serializer.save()
        #4. 비밀번호 해싱 후 
        user.set_password(request.data.get('password'))
        user.save()
    # password는 직렬화 과정에는 포함 되지만 → 표현(response)할 때는 나타나지 않는다.
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([AllowAny])
def profile(request, username):
    person = get_object_or_404(get_user_model(), username=username)
    serializer = UserProfileSerializer(person)
    return Response(serializer.data, status=status.HTTP_200_OK)