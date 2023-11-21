from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse, HttpResponse
import json as simplejson
from datetime import date, datetime
from django.views import View

from .models import Advertisement
from catalog.views import FandomAutocompleteView, GenresAutocompleteView, TagsAutocompleteView
from catalog.models import  Book, Fandom, Genres, Tag

def ajax_cost(request, book_id):
    location = request.GET.get('location')
    start = request.GET.get('start_date')
    end = request.GET.get('end_date')
    genre = request.GET.get("genre")
    tag = request.GET.get("tag")
    fandom = request.GET.get("fandom")

    start_date = datetime.strptime(start, '%Y-%m-%d')
    end_date = datetime.strptime(end, '%Y-%m-%d')
    days = end_date - start_date

    if genre or tag or fandom:
        price = 15
        cost = (days.days) * price
    else:
        price = 30
        cost = (days.days) * price

    results = {cost: cost}
    return HttpResponse(results)

def ajax_cost_sum(request, book_id):
    cost1 = int(request.GET.get('cost1'))
    cost2 = int(request.GET.get('cost2'))
    cost3 = int(request.GET.get('cost3'))
    cost4 = int(request.GET.get('cost4'))
    cost5 = int(request.GET.get('cost5'))
    cost = cost1+cost2+cost3+cost4+cost5
    results = {cost: cost}
    return HttpResponse(results)

@login_required
def book_advertisement_settings(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    genres = Genres.objects.all()
    tags = Tag.objects.all()
    fandoms = Fandom.objects.all()
    cost = 0
    cost1 = 0
    cost2 = 0
    cost3 = 0
    cost4 = 0
    cost5 = 0
    days = 0
    start_date = ''
    end_date = ''
    start_dateg = ''
    end_dateg = ''
    start_datet = ''
    end_datet = ''
    start_datef = ''
    end_datef = ''
    start_datec = ''
    end_datec = ''

    if request.method == 'GET':
        location = request.GET.get('location')
        start = request.GET.get('start_date')
        end = request.GET.get('end_date')
        if start and end:
            start_date = datetime.strptime(start, '%Y-%m-%d')
            end_date = datetime.strptime(end, '%Y-%m-%d')

        return render(request, 'Advertisement/advertisement_settings.html', {
                'book': book, 'genres': genres, 'fandoms': fandoms, 'tags': tags,
                'cost': cost, 'start_date': start_date, 'end_date': end_date,
            })

    if request.method == 'POST':
        cost = int(request.POST.get('cost'))
        cost1 = request.POST.get('cost1')
        cost2 = request.POST.get('cost2')
        cost3 = request.POST.get('cost3')
        cost4 = request.POST.get('cost4')
        cost5 = request.POST.get('cost5')

        location = request.POST.get('location')
        start = request.POST.get('start_date')
        end = request.POST.get('end_date')
        if start and end:
            start_date = datetime.strptime(start, '%Y-%m-%d')
            end_date = datetime.strptime(end, '%Y-%m-%d')

        locationc = request.POST.get('locationc')
        startc = request.POST.get('start_datec')
        endc = request.POST.get('end_datec')
        if startc and endc:
            start_datec = datetime.strptime(startc, '%Y-%m-%d')
            end_datec = datetime.strptime(endc, '%Y-%m-%d')

        locationg = request.POST.get('locationg')
        genre = request.POST.get('genre')
        startg = request.POST.get('start_dateg')
        endg = request.POST.get('end_dateg')
        if startg and endg:
            start_dateg = datetime.strptime(startg, '%Y-%m-%d')
            end_dateg = datetime.strptime(endg, '%Y-%m-%d')

        locationt = request.POST.get('locationt')
        tag = request.POST.get('tag')
        startt = request.POST.get('start_datet')
        endt = request.POST.get('end_datet')
        if startt and endt:
            start_datet = datetime.strptime(startt, '%Y-%m-%d')
            end_datet = datetime.strptime(endt, '%Y-%m-%d')

        locationf = request.POST.get('locationf')
        fandom = request.POST.get('fandom')
        startf = request.POST.get('start_datef')
        endf = request.POST.get('end_datef')
        if startf and endf:
            start_datef = datetime.strptime(startf, '%Y-%m-%d')
            end_datef = datetime.strptime(endf, '%Y-%m-%d')

        user_balance = request.user.profile.balance
        if user_balance < cost:
            # results = messages.error(request, 'На рахунку не достатньо коштів.')
            # return HttpResponse(results)
        # else:
            if start_date and end_date:
                with transaction.atomic():
                    request.user.profile.balance -= int(cost1)
                    request.user.profile.save()

                    advertisement = Advertisement(
                        user=request.user,
                        book=book,
                        start_date=start_date,
                        end_date=end_date,
                        location=location,
                        cost=int(cost1)
                    )
                    advertisement.save()

            if start_datec and end_datec:
                with transaction.atomic():
                    request.user.profile.balance -= int(cost2)
                    request.user.profile.save()

                    advertisement = Advertisement(
                        user=request.user,
                        book=book,
                        start_date=start_datec,
                        end_date=end_datec,
                        location=locationc,
                        cost=int(cost2)
                    )
                    advertisement.save()

            if start_dateg and end_dateg:
                with transaction.atomic():
                    request.user.profile.balance -= int(cost3)
                    request.user.profile.save()

                    advertisement = Advertisement(
                        user=request.user,
                        book=book,
                        start_date=start_dateg,
                        end_date=end_dateg,
                        location=locationg,
                        genre=genre,
                        cost=int(cost3)
                    )
                    advertisement.save()

            if start_datet and end_datet:
                with transaction.atomic():
                    request.user.profile.balance -= int(cost4)
                    request.user.profile.save()

                    advertisement = Advertisement(
                        user=request.user,
                        book=book,
                        start_date=start_datet,
                        end_date=end_datet,
                        location=locationt,
                        tag=tag,
                        cost=int(cost4)
                    )
                    advertisement.save()

            if start_datef and end_datef:
                with transaction.atomic():
                    request.user.profile.balance -= int(cost5)
                    request.user.profile.save()

                    advertisement = Advertisement(
                        user=request.user,
                        book=book,
                        start_date=start_datef,
                        end_date=end_datef,
                        location=locationf,
                        fandom=fandom,
                        cost=int(cost5)
                    )
                    advertisement.save()
            return redirect('main:home', book_id=book_id)

def del_adv():
    return Advertisement.objects.filter(end_date__lt=date.today()).delete()



def autocomplete_genre(request):
    def get(self, request):
        query = request.GET.get('query')
        genres = Genres.objects.filter(name__icontains=query)[:5]
        data = [{'id': genre.id} for genre in genres]
        return JsonResponse(data, safe=False)

def autocomplete_tag(request):
    def get(self, request):
        query = request.GET.get('query')
        tags = Tag.objects.filter(name__icontains=query)[:5]
        data = [{'name': tag.name} for tag in tags]
        return JsonResponse(data, safe=False)

def autocomplete_fandom(request):
    def get(self, request):
        query = request.GET.get('query')
        fandoms = Fandom.objects.filter(name__icontains=query)[:5]
        data = [{'name': fandom.name} for fandom in fandoms]
        return JsonResponse(data, safe=False)
