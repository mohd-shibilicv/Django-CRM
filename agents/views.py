import random

from django.shortcuts import reverse
from django.views import generic
from django.core.mail import send_mail

from leads.models import Agent
from .forms import AgentModelForm, AgentUpdateModelForm
from .mixins import OrgainsorAndLoginRequiredMixin


class AgentListView(OrgainsorAndLoginRequiredMixin, generic.ListView):
    template_name = 'agents/agents_list.html'
    context_object_name = 'agents'
    
    def get_queryset(self):
        organisation = self.request.user.userprofile
        return Agent.objects.filter(organisation=organisation)
    

class AgentCreateView(OrgainsorAndLoginRequiredMixin, generic.CreateView):
    template_name = 'agents/agent_create.html'
    form_class = AgentModelForm

    def get_success_url(self):  
        return reverse('agents:agents-list')
    
    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_agent = True
        user.is_organisor = False
        user.set_password(f"{random.randint(0, 1000000)}")
        user.save()
        Agent.objects.create(
            user=user,
            organisation = self.request.user.userprofile,
        )
        send_mail(
            subject="You're Invited to be an agent",
            message="You were updated as an agent.",
            from_email='test@test.com',
            recipient_list=[user.email],
        )

        return super(AgentCreateView, self).form_valid(form)
    

class AgentDetailView(OrgainsorAndLoginRequiredMixin, generic.DetailView):
    template_name = 'agents/agent_details.html'
    context_object_name = 'agent'

    def get_queryset(self):
        organisation = self.request.user.userprofile
        return Agent.objects.filter(organisation=organisation)


class AgentUpdateView(OrgainsorAndLoginRequiredMixin, generic.UpdateView):
    template_name = 'agents/agent_update.html'
    form_class = AgentUpdateModelForm

    def get_queryset(self):
        organisation = self.request.user.userprofile
        return Agent.objects.filter(organisation=organisation)
    
    def get_success_url(self):
        return reverse('agents:agent-details', kwargs={'pk': self.get_object().id})


class AgentDeleteView(OrgainsorAndLoginRequiredMixin, generic.DeleteView):
    template_name = 'agents/agent_delete.html'
    
    def get_queryset(self):
        organisation = self.request.user.userprofile
        return Agent.objects.filter(organisation=organisation)

    def get_success_url(self):
        return reverse('agents:agents-list')
