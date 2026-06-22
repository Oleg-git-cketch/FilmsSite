from django.shortcuts import render, redirect, get_object_or_404
from .models import Category, Film, Comments, LikeComment, SubCategory, User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from .forms import UserRegister, Search
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.db.models import Q
import json
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
import random



def home(request):
    categories = Category.objects.all()
    sub_categories = SubCategory.objects.all()

    films_list = Film.objects.all().order_by('-film_rating')  # лучше сортировать

    paginator = Paginator(films_list, 20)  # 12 фильмов на страницу

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'categories': categories,
        'sub_categories': sub_categories,
        'films': page_obj,
        'user': request.user,
    }

    return render(request, 'home.html', context)


def film(request, pk):
    film_obj = get_object_or_404(Film, film_slug=pk)
    comments = Comments.objects.filter(comment_film=film_obj, parent__isnull=True)

    liked_comments = []
    is_favourite = False

    if request.user.is_authenticated:
        liked_comments = LikeComment.objects.filter(
            like_user=request.user
        ).values_list('like_comment_id', flat=True)

        is_favourite = film_obj in request.user.user_favourites.all()

    context = {
        'film': film_obj,
        'comments': comments,
        'liked_comments': liked_comments,
        'is_favourite': is_favourite,  # ← Добавили
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

            return JsonResponse({
                "success": True,
                "comment": {
                    "id": comment.id,
                    "username": comment.comment_user.username,
                    "text": comment.comment_text,
                    "date": comment.comment_added.strftime("%d %b %Y %H:%M"),
                    "avatar": comment.comment_user.user_avatar.url if comment.comment_user.user_avatar else None
                }
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

            return JsonResponse({
                "success": True,
                "reply": {
                    "id": reply.id,
                    "username": reply.comment_user.username,
                    "text": reply.comment_text,
                    "date": reply.comment_added.strftime("%d %b %Y %H:%M"),
                    "avatar": reply.comment_user.user_avatar.url if reply.comment_user.user_avatar else None,
                    "parent_id": parent.id
                }
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

def category_page(request, pk):
    category_id = Category.objects.get(category_name=pk)
    films = Film.objects.filter(film_category=category_id)
    context = {'category': category_id, 'films': films}
    return render(request, 'category.html', context)

def sub_category_page(request, category_id, sub_category_id):
    category = Category.objects.get(id=category_id)
    sub_category = SubCategory.objects.get(
        id=sub_category_id,
        main_category=category
    )
    films = Film.objects.filter(film_subcategory=sub_category)

    context = {
        'sub_category': sub_category,
        'films': films,
        'category': category
    }
    return render(request, 'sub_category.html', context)


@login_required(login_url='/login')
def profile(request, pk):
    user = get_object_or_404(User, id=pk)
    own_user = request.user

    if user != own_user:
        return render(request, 'profile.html', {'user': user, 'own_user': own_user})

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        errors = []

        if not username:
            errors.append("Имя пользователя обязательно.")
        elif username != user.username and User.objects.filter(username=username).exists():
            errors.append("Это имя пользователя уже занято.")

        if not email:
            errors.append("Email обязателен.")
        elif email != user.email and User.objects.filter(email=email).exists():
            errors.append("Этот email уже используется.")

        if password1 or password2:
            if password1 != password2:
                errors.append("Пароли не совпадают.")
            elif len(password1) < 8:
                errors.append("Пароль должен содержать минимум 8 символов.")

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'profile.html', {
                'user': user,
                'own_user': own_user,
                'form_data': request.POST
            })

        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.email = email

        if password1:
            user.password = make_password(password1)

        user.save()

        messages.success(request, "Данные успешно обновлены!")
        return redirect(f'/profile/{user.pk}/')

    return render(request, 'profile.html', {'user': user, 'own_user': own_user})


@login_required(login_url='/login')
def change_avatar(request):
    if request.method == 'POST':
        avatar = request.FILES.get('avatar')
        if avatar:
            if avatar.size > 5 * 1024 * 1024:  # 5 МБ
                return JsonResponse({'success': False, 'error': 'Файл слишком большой (макс. 5 МБ)'}, status=400)

            request.user.user_avatar = avatar
            request.user.save(update_fields=['user_avatar'])

            return JsonResponse({
                'success': True,
                'avatar_url': request.user.user_avatar.url
            })

    return JsonResponse({'success': False, 'error': 'Нет файла'}, status=400)

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
        )

        data = []

        for film in films:
            data.append({
                "id": film.id,
                "film_name": film.film_name,
                "film_slug": film.film_slug,
                "film_description": film.film_description,
                "film_date": film.film_date.strftime("%Y"),
                "film_rating": str(film.film_rating),
                "film_category": film.film_subcategory.sub_category_name,
                "film_poster": film.film_poster.url if film.film_poster else None,
            })

        return JsonResponse(data, safe=False)

    return JsonResponse([], safe=False)


def send_email(gmail):
    code = random.randint(100000, 999999)

    send_mail(
        "Подтверждение email",
        f"Ваш код: {code}",
        "yourgmail@gmail.com",
        [gmail],
        fail_silently=False,
    )

    return code

def register(request):
    if request.method == 'POST':
        form = UserRegister(request.POST, request.FILES)

        if form.is_valid():

            code = send_email(form.cleaned_data['email'])

            request.session['auth_data'] = {
                'username': form.cleaned_data['username'],
                'first_name': form.cleaned_data['first_name'],
                'last_name': form.cleaned_data['last_name'],
                'email': form.cleaned_data['email'],
                'password': form.cleaned_data['password1'],
                'code': code,
                'type': 'register'
            }

            return redirect('/confirm_email/')

        else:
            print(form.errors)

    else:
        form = UserRegister()

    return render(request, 'register/register.html', {'form': form})

from django.contrib.auth import login

def confirm_email(request):
    data = request.session.get('auth_data')

    if not data:
        return redirect('/register/')

    if request.method == "POST":
        input_code = request.POST.get("code")

        if str(input_code) == str(data['code']):

            # ================= REGISTER FLOW =================
            if 'username' in data:
                user = User.objects.create_user(
                    username=data['username'],
                    email=data['email'],
                    password=data['password'],
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                )

            # ================= LOGIN FLOW =================
            else:
                user = User.objects.get(id=data['user_id'])

            del request.session['auth_data']

            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('/')

        return render(request, 'register/confirm_email.html', {
            'email': data.get('email', ''),
            'error': 'Неверный код'
        })

    return render(request, 'register/confirm_email.html', {
        'email': data.get('email', '')
    })

def login_page(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)

        if form.is_valid():
            user = form.get_user()

            code = send_email(user.email)

            request.session['auth_data'] = {
                'user_id': user.id,
                'code': code
            }

            return redirect('/confirm_email/')

    else:
        form = AuthenticationForm()

    return render(request, 'register/login.html', {'form': form})