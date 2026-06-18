from django.shortcuts import render, redirect
from .models import Category, Film, User, Comments, LikeComment
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from .forms import UserRegister, Search
from django.contrib.auth.decorators import login_required


# Create your views here.
def home(request):
    categories = Category.objects.all()
    films = Film.objects.all()

    context = {
        'categories': categories,
        'films': films,
    }
    return render(request, 'home.html', context)

def film(request, pk):
    film_id = Film.objects.get(id=pk)
    comments = Comments.objects.filter(comment_film=film_id, parent__isnull=True)
    liked_comments = LikeComment.objects.filter(
        like_user=request.user
    ).values_list('like_comment_id', flat=True)

    context =  {
        'film': film_id,
        'comments': comments,
        'liked_comments': liked_comments
    }
    return render(request, 'film.html', context)

def category(request, pk):
    category_id = Category.objects.get(category_name=pk)
    films = Film.objects.filter(film_category=category_id)

    context = {
        'category': category_id,
        'films': films,
    }
    return render(request, 'category.html', context)

def register(request):
    if request.method == 'POST':
        form = UserRegister(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('/login')
        else:
            print(form.errors)
    else:
        form = UserRegister()
    return render(request, 'register/register.html', {'form': form})

def login_page(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('/')
    else:
        form = AuthenticationForm()
    return render(request, 'register/login.html', {'form': form})


@login_required(login_url='/login')
def profile(request):
    user = request.user

    context = {
        'user': user
    }
    return render(request, 'profile.html', context)

def change_avatar(request):
    if request.method == 'POST':
        avatar = request.FILES.get('avatar')

        if avatar:
            request.user.user_avatar = avatar
            request.user.save(update_fields=['user_avatar'])

    return redirect('/profile')


@login_required(login_url='/login')
def favourite(request, pk):
    if request.method == 'POST':
        film = Film.objects.get(id=pk)
        user_films = request.user.user_favourites.all()
        url = int(pk)
        for i in user_films:
            if i.id == film.id:
                return redirect(f'/film/{url}')
        request.user.user_favourites.add(film)
        return redirect(f'/film/{url}')
    return redirect('/')

def logout_page(request):
    logout(request)
    return redirect('/')

def search(request):
    if request.method == 'POST':
        query = request.POST.get('query', '')  # получаем строку поиска
        if query:
            films = Film.objects.filter(film_name__icontains=query)  # поиск по части названия
            return render(request, 'search_results.html', {'films': films, 'query': query})
    return redirect('/')


@login_required(login_url='/login')
def comment_page(request, pk):
    if request.method == 'POST':
        comment = request.POST.get('comment')
        if comment:
            film = Film.objects.get(id=pk)
            user = request.user
            Comments.objects.create(comment_film=film, comment_text=comment, comment_user=user)
            return redirect(f'/film/{pk}')
    return redirect('/')

def comment_reply(request, pk):
    if request.method == 'POST':
        comment = request.POST.get('reply')
        if comment:
            parent_comment = Comments.objects.get(id=pk)

            Comments.objects.create(
                comment_film=parent_comment.comment_film,
                comment_user=request.user,
                comment_text=comment,
                parent=parent_comment
            )
            return redirect(f'/film/{parent_comment.comment_film.id}')
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required(login_url='/login')
def add_like(request, pk):
    comment = Comments.objects.get(id=pk)

    like, created = LikeComment.objects.get_or_create(
        like_comment=comment,
        like_user=request.user
    )

    if not created:
        like.delete()
        comment.comment_likes -= 1
    else:
        comment.comment_likes += 1

    comment.save(update_fields=['comment_likes'])
    return redirect(f'/film/{comment.comment_film.id}')