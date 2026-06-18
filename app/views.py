from django.shortcuts import render, redirect, get_object_or_404
from .models import Category, Film, Comments, LikeComment
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from .forms import UserRegister, Search
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.db.models import Q
import json


def home(request):
    categories = Category.objects.all()
    films = Film.objects.all()
    context = {'categories': categories, 'films': films}
    return render(request, 'home.html', context)


def film(request, pk):
    film_id = get_object_or_404(Film, id=pk)
    comments = Comments.objects.filter(comment_film=film_id, parent__isnull=True)

    liked_comments = []
    if request.user.is_authenticated:
        liked_comments = LikeComment.objects.filter(
            like_user=request.user
        ).values_list('like_comment_id', flat=True)

    context = {
        'film': film_id,
        'comments': comments,
        'liked_comments': liked_comments
    }
    return render(request, 'film.html', context)


@login_required(login_url='/login')
def comment_page(request, pk):
    if request.method == 'POST':
        comment_text = request.POST.get('comment', '').strip()
        if comment_text:
            film = get_object_or_404(Film, id=pk)
            comment = Comments.objects.create(
                comment_film=film,
                comment_text=comment_text,
                comment_user=request.user
            )

            html = render_to_string("partials/comment.html", {
                "comment": comment
            }, request=request)

            return JsonResponse({
                "success": True,
                "html": html,
                "comment_id": comment.id
            })

    return JsonResponse({"success": False, "error": "invalid"}, status=400)


@login_required(login_url='/login')
def comment_reply(request, pk):
    if request.method == 'POST':
        text = request.POST.get('reply', '').strip()
        if text:
            parent = get_object_or_404(Comments, id=pk)

            reply = Comments.objects.create(
                comment_film=parent.comment_film,
                comment_user=request.user,
                comment_text=text,
                parent=parent
            )

            html = render_to_string("partials/reply.html", {
                "reply": reply
            }, request=request)

            return JsonResponse({
                "success": True,
                "html": html,
                "comment_id": parent.id
            })

    return JsonResponse({"success": False, "error": "invalid"}, status=400)


@login_required(login_url='/login')
def add_like(request, pk):
    if request.method == 'POST':
        comment = get_object_or_404(Comments, id=pk)

        like, created = LikeComment.objects.get_or_create(
            like_comment=comment,
            like_user=request.user
        )

        if created:
            comment.comment_likes += 1
            liked = True
        else:
            like.delete()
            comment.comment_likes -= 1
            liked = False

        comment.save(update_fields=['comment_likes'])

        return JsonResponse({
            "success": True,
            "likes": comment.comment_likes,
            "liked": liked
        })

    return JsonResponse({"success": False}, status=400)


@login_required(login_url='/login')
def favourite(request, pk):
    if request.method == 'POST':
        film = get_object_or_404(Film, id=pk)
        user_films = request.user.user_favourites.all()

        if film in user_films:
            request.user.user_favourites.remove(film)
            message = "Удалено из избранного"
        else:
            request.user.user_favourites.add(film)
            message = "Добавлено в избранное"

        return JsonResponse({
            "success": True,
            "message": message
        })

    return JsonResponse({"success": False}, status=400)


# ==================== Остальные функции без изменений ====================

def category(request, pk):
    category_id = Category.objects.get(category_name=pk)
    films = Film.objects.filter(film_category=category_id)
    context = {'category': category_id, 'films': films}
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
    return render(request, 'profile.html', {'user': request.user})

@login_required(login_url='/login')
def change_avatar(request):
    if request.method == 'POST':
        avatar = request.FILES.get('avatar')
        if avatar:
            request.user.user_avatar = avatar
            request.user.save(update_fields=['user_avatar'])
    return redirect('/profile')

@login_required
def change_username(request):
    if request.method == "POST":
        data = json.loads(request.body)
        name = data.get("username")

        if name:
            request.user.username = name
            request.user.save(update_fields=["username"])
            return JsonResponse({"success": True})

    return JsonResponse({"success": False})


def logout_page(request):
    logout(request)
    return redirect('/')


def search(request):
    query = request.GET.get('q', '').strip()

    if query:
        films = Film.objects.filter(
            Q(film_search__icontains=query)
        ).values('id', 'film_name', 'film_date')

        data = [
            {
                "id": f["id"],
                "film_name": f["film_name"],
                "film_date": f["film_date"].strftime("%Y")
            }
            for f in films
        ]

        return JsonResponse(data, safe=False)

    return JsonResponse([], safe=False)