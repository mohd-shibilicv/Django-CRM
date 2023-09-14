from django import forms
from django.contrib.auth import get_user_model

from leads.models import Agent

User = get_user_model()

class AgentModelForm(forms.ModelForm):

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
        )


class AgentUpdateModelForm(forms.ModelForm):

    class Meta:
        model = Agent
        fields = (
            'user',
            'organisation',
        )