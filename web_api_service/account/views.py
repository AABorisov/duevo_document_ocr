from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from document_processing import constants
from .forms import UserRegistrationForm, UserUpdateForm, ProfileUpdateForm
from django.utils.translation import gettext_lazy as _
from .models import User
from document.models import Nlp
from django.utils import translation


# Create your views here.
def main_page(request):

    # user_language = 'ru'
    # translation.activate(user_language)
    # request.session[translation.LANGUAGE_SESSION_KEY] = user_language

    if translation.LANGUAGE_SESSION_KEY in request.session:
        del request.session[translation.LANGUAGE_SESSION_KEY]

    context = {
        'navbar': constants.NAVBAR_MAIN,
    }
    return render(request, 'account/index.html', context=context)


def register(request):

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            message_text = _('Account created for %(email)s') % {'email': email}
            message_text = _('Your account has been created! You are now able to log in')
            messages.success(request, message_text)
            return redirect('login_url')
    else:
        form = UserRegistrationForm()

    context = {
        'form': form,
    }
    return render(request, 'account/register.html', context=context)


@login_required
def user_account(request):
    context = {
        'navbar': constants.NAVBAR_USER_ACCOUNT
    }
    return render(request, "account/main.html", context=context)


@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            message_text = _('Your account has been updated!')
            messages.success(request, message_text)

            return redirect('profile_url')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'navbar': constants.NAVBAR_PROFILE
    }
    return render(request, "account/profile.html", context=context)
