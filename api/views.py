from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from movierater.api.serializers import UserSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from movierater.api.models import Movie, Rating
from movierater.api.serializers import MovieSerializer, RatingsSerializer
from rest_framework.decorators import action


class UserViewSet(viewsets.ModelViewSet):

    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class CustomObtainAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        response = super(CustomObtainAuthToken, self).post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        user = User.objects.get(id=token.user_id)
        serializer = UserSerializer(user, many=False)
        return Response({'token': token.key, 'user': serializer.data})


class MovieViewSet(viewsets.ModelViewSet):

    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)


class RatingViewSet(viewsets.ModelViewSet):

    queryset = Rating.objects.all()
    serializer_class = RatingsSerializer
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)

    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated])
    def rate_movie(self, request):
        if 'movie' in request.data and 'user' in request.data and 'stars' in request.data:
            movie = Movie.objects.get(id=request.data['movie'])
            user = User.objects.get(id=request.data['user'])
            stars = request.data['stars']

            try:
                my_rating = Rating.objects.get(movie=movie.id, user=user.id)
                my_rating.stars = stars
                my_rating.save()
                serializer = MovieSerializer(movie, many=False)
                response = {"message": "Rating update", "result": serializer.data}
                return Response(response, status=status.HTTP_200_OK)

            except:
                Rating.objects.create(movie=movie, user=user, stars=stars)
                serializer = MovieSerializer(movie, many=False)
                response = {"message": "Rating created", "result": serializer.data}
                return Response(response, status=status.HTTP_200_OK)
        else:
            response = {"message": "You must enter all parameter"}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)




