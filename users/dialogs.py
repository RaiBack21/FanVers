from .models import Dialog

def get_or_create_dialog(user1, user2):
    try:
        dialog = Dialog.objects.get(user1=user1, user2=user2)
    except Dialog.DoesNotExist:
        dialog = Dialog(user1=user1, user2=user2)
        dialog.save()
    return dialog