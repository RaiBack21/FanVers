from celery import shared_task
from FanVers.celery import app
from datetime import timedelta
from django.utils import timezone
from .models import Book, ViewedBooks
from django.contrib.auth.models import User
from .models import Notification
import logging
from users.models import Profile

logger = logging.getLogger(__name__)


@shared_task
def check_abandoned_books():
    try:
        hour_ago = timezone.now() - timedelta(minutes=3)
        books_to_update = Book.objects.filter(last_updated__lte=hour_ago,
                                              status=Book.TRANSLATING)  # тут перевірка статусу та активності

        print(f"Found {books_to_update.count()} books to update.")

        reergard_user = get_reergard_user()

        for book in books_to_update:
            print(f"Processing book '{book.title}'")

            # Debugging: Print the current status of the book
            print("Current status:", book.status)


            # Debugging: Change the status and print the new status
            new_status = Book.ABANDONED
            print(f"Changing status to {new_status}")
            book.set_status(new_status)
            book.save()

            notification_message = f'Книга "{book.title}" була перенесена в статус "Покинуті".'
            print(notification_message, flush=True)
            for profile in Profile.objects.filter(user=book.user):
                notification = Notification.objects.create(user_profile=profile, message=notification_message)
                notification.save()
            else:
                print("No books to process at this time.")

            # Debugging: Print the new status after saving
            print("Updated status:", book.status)

            # Debugging: Print the user and time before update
            print("User before update:", book.user)
            print("Last updated before update:", book.last_updated)

            # Update user and last_updated
            book.user = reergard_user
            book.last_updated = timezone.now()
            book.save()

            # Debugging: Print the user and time after update
            print("User after update:", book.user)
            print("Last updated after update:", book.last_updated)

            # Debugging: Print a message after processing each book
            print(f"Book '{book.title}' processed successfully")

        print("Task check_abandoned_books finished")

    except Exception as e:
        print("An error occurred:", e)


# logger = logging.getLogger(__name__)\

@shared_task
def send_abandoned_notification():
    logger.info(f"send_abandoned_notification started for book_id ")

    abandoned_threshold = timezone.now() - timedelta(minutes=1)

    books = Book.objects.filter(status=Book.TRANSLATING)
    logger.info(f"send_abandoned_notification ----------- found TRANSLATING books: " + str(len(books)) )


    for book in books:
        logger.info("BOOK " + book.title)

        if book.last_updated <= abandoned_threshold:
            logger.info("BOOK " + book.title + " last_updated <= abandoned_threshold")

            logger.info(f"book.status: {book.status}")
            logger.info(f"book.last_updated: {book.last_updated}")
            logger.info(f"abandoned_threshold: {abandoned_threshold}")
            logger.info(f"book.user: {book.user}")

            notification_message = f'Книга "{book.title}" будет перенесена в статус "Покинутые" через Х дней бездействия.'
            print(notification_message, flush=True)
            for profile in Profile.objects.filter(user=book.user):
                logger.info("Profile(user=book.user) id = " + str(profile.user.id))
                notification = Notification.objects.create(user_profile=profile, message=notification_message)
                notification.save()
                logger.info(f'Sent notification: {notification.message} to {profile.user.username}')





def get_reergard_user():
    #  вернуть существующего пользователя
    user, created = User.objects.get_or_create(username='reergard_user')
    return user


@shared_task
def simple_debug_task():
    print("Simple debug task executed successfully")

@shared_task
def update_trending_score():
    # Оновлення trending_score для книг
    books = Book.objects.all()
    for book in books:
        views_last_week = book.viewed_by.filter(viewedbooks__revision_date__gte=timezone.now() - timedelta(days=7)).count()
        book.trending_score = views_last_week
        book.save()
