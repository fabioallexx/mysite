from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group

class RegisterForm(UserCreationForm):
    email = forms.EmailField()
    group = forms.ModelChoiceField(queryset=Group.objects.all(), required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2", "group"]

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            group = self.cleaned_data['group']
            user.groups.add(group)
            user.save()
        return user