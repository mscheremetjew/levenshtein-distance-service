from django.contrib.auth.forms import UserCreationForm
from django.forms import EmailField
from django.urls import reverse_lazy
from django.views import generic

from authentication.models import User


class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email",)
        field_classes = {"email": EmailField}


class RegisterView(generic.CreateView):
    form_class = RegistrationForm
    success_url = reverse_lazy("login")
    template_name = "registration/register.html"
