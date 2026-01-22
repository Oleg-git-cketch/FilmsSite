from django.contrib.auth.forms import UserCreationForm
from .models import User, Film, Comments


class UserRegister(UserCreationForm):

    class Meta:
        model = User
        fields = ('username', 'password1','password2', 'user_avatar')

class Search:
    class Meta:
        model = Film
        fields = ('name',)
