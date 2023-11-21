from django.http import JsonResponse, HttpResponse
from .forms import CreationUserForm, LoginForm, AddFundsForm, PurchaseChapterForm, MessageForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Profile, Transaction, Message
from .forms import ProfileForm, MessageForm
from django.urls import reverse_lazy
from django.contrib.auth.models import Group, User
from django.http import HttpResponseNotFound
from django.contrib.auth.decorators import login_required
from django.db import transaction
from catalog.models import Chapter, Book, Comment, Rating
from decimal import Decimal
from django.views.generic import TemplateView, ListView, DetailView, UpdateView, View
from django.http import Http404
from .models import Dialog
from .dialogs import get_or_create_dialog
from django.db.models import Q, Count, Avg, Sum, Case, When, IntegerField
from rest_framework_simplejwt.views import TokenObtainPairView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def save_token(request):
    if request.method == 'POST':
        token = request.POST.get('token')
        user = request.user  # Получите текущего аутентифицированного пользователя

        if user and token:

            # Сохраните токен в базе данных
            user.profile.token = token  # Предполагается, что у пользователя есть профиль с полем "token"
            user.profile.save()

            return JsonResponse({'message': 'Токен успешно сохранен'})
        else:
            return JsonResponse({'message': 'Ошибка: недопустимый токен или пользователь'}, status=400)

    return JsonResponse({'message': 'Ошибка: неверный метод запроса'}, status=400)



def login_modal_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                # Создание экземпляра TokenObtainPairView и получение токена
                token_obtain_pair_view = TokenObtainPairView.as_view()
                response = token_obtain_pair_view(request)
                return response
            else:
                messages.error(request, 'Невірний Логін або Пароль')
                return JsonResponse({'success': False, 'errors': 'Невірний Логін або Пароль'}, status=400)
        else:
            errors = form.errors.as_json()
            return JsonResponse({'success': False, 'errors': errors}, status=400)
    else:
        form = LoginForm()
        return render(request, 'users/login_modal.html', {'form': form})


def logout_view(request):
    logout(request)

    response = redirect('main:home')
    response.delete_cookie('sessionid')
    return response


#  регистрация
def signup_modal_view(request):
    page = 'main:home'
    if request.method == 'POST':
        form = CreationUserForm(request.POST)
        if form.is_valid():
            user = form.save()

            user.is_active = True
            user.save()

            # Получаем группу 'Читач'
            reader_group = Group.objects.get(name='Читач')

            # Добавляем пользователя в группу 'Читач'
            user.groups.add(reader_group)

            # Обновляем профиль пользователя
            user.profile.group = user.groups.first()
            user.profile.save()

            # Авторизация пользователя
            login(request, user)
            # authenticate(request, username=user.username, password=user.password)

            messages.success(request, 'Обліковий запис успішно створено!')
            # Обработка успешной регистрации

            return JsonResponse(data={}, status=200)

        else:
            errors = form.errors.as_json()
            return JsonResponse(data={'errors': errors}, status=400)



class ProfileListView(ListView):
    model = Profile
    template_name = 'users/translators.html'
    context_object_name = 'translators'

    def get(self, request):
        order = request.GET.get('order_t', 'nick')

        translators = (Profile.objects.
            filter(group__name__startswith='Перекладач').
            annotate(total_books=Count('user__books')).
            annotate(total_chapters=Count('user__books__book_chapters')).
            annotate(author_avg_rating=Avg('user__books__book_ratings__stars')).
            annotate(free_chapters=Sum(
                Case(When(
                    user__books__book_chapters__price=0, then=1),
                    default=0, output_field=IntegerField(),
                    )))
        )

        if order == 'nick':
            translators = translators.order_by('username')
        if order == 'book_count':
            translators = translators.order_by('-total_books')
        if order == 'chapter_count':
            translators = translators.order_by('-total_chapters')
        if order == 'avg_rating':
            translators = translators.order_by('-author_avg_rating')
        if order == 'free_chapters':
            translators = translators.order_by('-free_chapters')
        if order == 'activity':
            translators = sorted(translators, key=Profile.total_activity, reverse=True)
        if order == 'last_login':
            translators = translators.order_by('-user__last_login')

        context = {
            'translators': translators, 'ordert': order
        }
        return render(request, 'users/translators.html', context)


# Для  користувача який онлайн
class ProfileDetail(LoginRequiredMixin, DetailView):
    """Вывод профиля пользователя"""
    model = Profile
    context_object_name = 'profile'
    template_name = 'users/profile.html'

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        total_chars = sum(ch.content_length for ch in Chapter.objects.filter(book__user=self.request.user))

        user = (Profile.objects.filter(user=self.request.user).
            annotate(total_chapters=Count('user__books__book_chapters')).
            annotate(author_avg_rating=Avg('user__books__book_ratings__stars')).
            annotate(free_chapters=Sum(
                Case(When(
                    user__books__book_chapters__price=0, then=1),
                    default=0, output_field=IntegerField(),
                    ))))

        # Вычисляем комиссию на основе количества символов
        if total_chars < 5000:
            commission_rate = 15
        elif total_chars < 10000:
            commission_rate = 12
        else:
            commission_rate = 5

        context['user_profile'] = user
        context['transactions'] = Transaction.objects.filter(user=self.request.user)
        context['total_chars'] = total_chars
        context['commission_rate'] = commission_rate

        return context



class OtherUserProfileDetail(DetailView):
    """Вывод профиля другого пользователя"""
    model = Profile
    context_object_name = 'profile'
    template_name = 'users/other_profile.html'

    def get_object(self, queryset=None):
        username = self.kwargs.get('username')  # Получаем имя пользователя из URL-параметра
        user = get_object_or_404(User, username=username)
        return user.profile

class ProfileUpdate(LoginRequiredMixin, UpdateView):
    """Редактирование профиля"""
    form_class = ProfileForm
    model = Profile
    template_name = "users/profile_form.html"


    def form_valid(self, form):
        return super().form_valid(form)

    def get_object(self, queryset=None):
        return self.request.user.profile

    def form_invalid(self, form):
        print(form.instance.username)
        print(form.instance.email)
        print(form.instance.about)
        print(form.instance.image)
        return super().form_invalid(form)

    success_url = reverse_lazy('users:ProfileUpdate')




@login_required
@transaction.atomic
def add_funds(request):
    if request.method == 'POST':
        form = AddFundsForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            # тут ваш код для интеграции с платежной системой
            user_profile = UserProfile.objects.get(user=request.user)
            user_profile.balance += amount
            user_profile.save()

            # Записываем транзакцию
            Transaction.objects.create(user=request.user, amount=amount, description="Пополнение баланса")

            return redirect('profile_view')
    else:
        form = AddFundsForm()

    return render(request, 'users/add_funds.html', {'form': form})








def calculate_commission(amount, total_chars):
    if total_chars < 5000:
        commission_rate = 0.15
    elif total_chars < 10000:
        commission_rate = 0.12
    else:
        commission_rate = 0.05

    return amount * Decimal(commission_rate)




SYSTEM_USER_ID = 1  # ID системного пользователя
@login_required
@transaction.atomic
def purchase_chapter(request, chapter_id):
    profile = Profile.objects.get(user=request.user)
    chapter = get_object_or_404(Chapter, id=chapter_id)
    book = chapter.book



    if not book:
        messages.error(request, "Ошибка: глава не связана с книгой!")

        return redirect(request.META.get('HTTP_REFERER', 'default_redirect_url'))

    book_owner = book.user  # Получаем владельца книги
    price = chapter.price

    # Подсчет символов всех книг пользователя
    total_chars = sum(ch.content_length for ch in Chapter.objects.filter(book__user=book_owner))
    commission = calculate_commission(price, total_chars)

    if profile.balance >= price:
        profile.balance -= (price + commission)
        profile.save()


        # Записываем транзакцию для покупателя
        Transaction.objects.create(user=request.user, amount=-price, description=f"Покупка главы {chapter_id}")

        # Записываем комиссию на системный аккаунт
        system_user = User.objects.get(id=SYSTEM_USER_ID)
        system_user.profile.balance += commission
        system_user.profile.save()

        # Записываем транзакцию комиссии для системного аккаунта
        Transaction.objects.create(user=system_user, amount=commission,
                                   description=f"Комиссия за покупку главы {chapter_id}")

        # Записываем транзакцию комиссии
        Transaction.objects.create(user=request.user, amount=-commission, description=f"Комиссия за покупку главы {chapter_id}")

        # Увеличиваем баланс владельца книги
        book_owner.profile.balance += (price - commission)
        book_owner.profile.save()

        # Записываем транзакцию для владельца книги
        Transaction.objects.create(user=book_owner, amount=price - commission, description=f"Продажа главы {chapter_id}")



        chapter.purchased_by.add(request.user)
        chapter.save()
        # Здесь можно также добавить логику для предоставления доступа к главе пользователю.
        # ...

        messages.success(request, "Глава успешно куплена!")
        return redirect(request.META.get('HTTP_REFERER', 'default_redirect_url'))
    else:
        # Если у пользователя недостаточно средств
        return redirect('some_error_page')  # Например, страница с сообщением об ошибке






SYSTEM_USER_ID = 1  # ID системного пользователя

@login_required
def commission_stats(request):
    # Проверяем, является ли пользователь владельцем сайта (замените YOUR_USERNAME на ваше имя пользователя)
    if request.user.username != 'YOUR_USERNAME':
        return HttpResponseForbidden("У вас нет прав для просмотра этой страницы.")

    system_user = User.objects.get(id=SYSTEM_USER_ID)
    system_user_balance = system_user.profile.balance
    transactions = Transaction.objects.filter(user=system_user).order_by('-date_created')

    context = {
        'system_user_balance': system_user_balance,
        'transactions': transactions,
    }

    return render(request, 'path_to_template/commission_stats.html', context)






@login_required
@login_required
def create_dialog(request):
    other_user = get_object_or_404(User, username='admin')
    dialog = get_or_create_dialog(request.user, other_user)
    return redirect('users:dialog_view', dialog_id=dialog.id)


@login_required
def dialog_view(request, dialog_id):
    dialog = get_object_or_404(Dialog, id=dialog_id)
    if request.user not in [dialog.user1, dialog.user2]:
        raise Http404

    messages = dialog.message_set.order_by('date_created')

    other_user = dialog.user1 if dialog.user1 != request.user else dialog.user2

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.dialog = dialog  # Указываем диалог
            message.sender = request.user
            message.save()
            return redirect('users:dialog_view', dialog_id=dialog.id)
    else:
        form = MessageForm()

    context = {
        'dialog': dialog,
        'messages': messages,
        'form': form,
        'other_user': other_user,
    }

    return render(request, 'users/dialog.html', context)


@login_required
def dialogs_list(request):#шаблон для списка диалогов
    dialogs = Dialog.objects.filter(Q(user1=request.user) | Q(user2=request.user))

    context = {
        'dialogs': dialogs
    }

    return render(request, 'users/mail.html', context)
