from users.forms import LoginForm, CreationUserForm

def get_context_data(request):
    context = {
    'login_form': LoginForm(),
    'signup_form': CreationUserForm()
    }
    return context
