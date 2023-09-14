from django.shortcuts import render, redirect, reverse
from django.views import generic
from django.core.mail import send_mail
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Lead, Agent, Category
from .forms import LeadForm, LeadModelForm, CustomUserCreationForm, AssignAgentForm, LeadCategoryUpdateForm, CategoryModelForm
from agents.mixins import OrgainsorAndLoginRequiredMixin


class LandingPageView(generic.TemplateView):
    template_name = 'landing_page.html'


def landing_page(request):
    return render(request, 'leads/landing_page.html')


class SignUpView(generic.CreateView):
    template_name = 'registration/signup.html'
    form_class = CustomUserCreationForm

    def get_success_url(self) -> str:
        return reverse('login')


class LeadListView(LoginRequiredMixin, generic.ListView):
    template_name = 'leads/lead_list.html'
    context_object_name = 'leads'

    def get_queryset(self):
        user = self.request.user

        if user.is_organisor:
            queryset = Lead.objects.filter(
                organisation=user.userprofile,
                agent__isnull=False,
            )
        else:
            queryset = Lead.objects.filter(
                organisation=user.agent.organisation,
                agent__isnull=False,
            )
            queryset = queryset.filter(agent__user=user)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.is_organisor:
            queryset = Lead.objects.filter(
                organisation = user.userprofile,
                agent__isnull=True,
            )
            context.update({
                'unassigned_leads': queryset,
            })
        
        return context

def lead_list(request):
    leads = Lead.objects.all()
    context = {
        'leads': leads
    }
    return render(request, "leads/lead_list.html", context=context)



class LeadDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = 'leads/lead_details.html'
    context_object_name = 'lead'

    def get_queryset(self):
        user = self.request.user

        if user.is_organisor:
            queryset = Lead.objects.filter(organisation=user.userprofile)
        else:
            queryset = Lead.objects.filter(organisation=user.agent.organisation)
            queryset = queryset.filter(agent__user=user)
        return queryset


def lead_details(request, pk):
    lead = Lead.objects.get(id=pk)
    context = {
        'lead': lead
    }
    return render(request, "leads/lead_details.html", context=context)



def _create_lead(request):
    form = LeadForm()

    if request.method == 'POST':
        form = LeadForm(request.POST)

        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            age = form.cleaned_data['age']
            agent = Agent.objects.first()
            
            Lead.objects.create(
                first_name=first_name,
                last_name=last_name,
                age=age,
                agent=agent,
            )
        
            return redirect('leads:lead-list')
    
    context = {
        'form': form
    }
    return render(request, 'leads/create_lead.html', context=context)


class LeadCreateView(OrgainsorAndLoginRequiredMixin, generic.CreateView):
    template_name = 'leads/create_lead.html'
    form_class = LeadModelForm

    def get_success_url(self):
        return reverse("leads:lead-list")
    
    def form_valid(self, form):
        # TODO send email
        lead = form.save(commit=False)
        lead.organisation = self.request.user.userprofile
        lead.save()
        send_mail(
            subject="A Lead has been created",
            message="Go back to the site to see the new lead",
            from_email="test@test.com",
            recipient_list=["test2@test.com"],
        )
        return super(LeadCreateView, self).form_valid(form)

    
def create_lead(request):
    form = LeadModelForm()

    if request.method == 'POST':
        form = LeadModelForm(request.POST)

        if form.is_valid():
            form.save()
        
            return redirect('leads:lead-list')
    
    context = {
        'form': form
    }
    return render(request, 'leads/create_lead.html', context=context)



def _lead_update(request, pk):
    lead = Lead.objects.get(id=pk)
    form = LeadForm()

    if request.method == 'POST':
        form = LeadForm(request.POST)

        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            age = form.cleaned_data['age']
            lead.first_name = first_name
            lead.last_name = last_name
            lead.age = age
            lead.save()

            return redirect('leads:lead-list')
    
    context = {
        'lead': lead,
        'form': form,
    }
    return render(request, 'leads/lead_update.html', context=context)


class LeadUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = "leads/lead_update.html"
    form_class = LeadModelForm

    def get_queryset(self):
        user = self.request.user

        if user.is_organisor:
            queryset = Lead.objects.filter(organisation=user.userprofile)
        else:
            queryset = Lead.objects.filter(organisation=user.agent.organisation)
            queryset = queryset.filter(agent__user=user)
        return queryset

    def get_success_url(self) -> str:
        return reverse('leads:lead-details', kwargs={'pk': self.get_object().id})


def lead_update(request, pk):
    lead = Lead.objects.get(id=pk)
    form = LeadModelForm(instance=lead)

    if request.method == 'POST':
        form = LeadModelForm(request.POST, instance=lead)

        if form.is_valid():
            form.save()

            return redirect('leads:lead-details', pk)

    context = {
        'form': form,
        'lead': lead
    }
    return render(request, 'leads/lead_update.html', context=context)


class LeadCategoryUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = 'leads/lead_category.html'
    form_class = LeadCategoryUpdateForm

    def get_queryset(self):
        user = self.request.user
        if user.is_organisor:
            queryset = Lead.objects.filter(organisation=user.userprofile)
        else:
            queryset = Lead.objects.filter(organisation=user.agent.organisation)
            queryset = queryset.filter(agent__user=user)

        return queryset
    
    def get_success_url(self) -> str:
        return reverse('leads:lead-details', kwargs={'pk': self.get_object().id})


class LeadDeleteView(OrgainsorAndLoginRequiredMixin, generic.DeleteView):
    template_name = 'leads/lead_delete.html'
    
    def get_queryset(self):
        user = self.request.user

        if user.is_organisor:
            queryset = Lead.objects.filter(organisation=user.userprofile)
        else:
            queryset = Lead.objects.filter(organisation=user.agent.organisation)
            queryset = queryset.filter(agent__user=user)
        return queryset

    def get_success_url(self) -> str:
        return reverse('leads:lead-list')


def lead_delete(request, pk):
    lead = Lead.objects.get(id=pk)
    lead.delete()
    return redirect('leads:lead-list')


class AssignAgentView(OrgainsorAndLoginRequiredMixin, generic.FormView):
    template_name = 'leads/assign_agent.html'
    form_class = AssignAgentForm

    def get_form_kwargs(self, **kwargs):
        kwargs = super(AssignAgentView, self).get_form_kwargs(**kwargs)
        kwargs.update({
            'request': self.request
        })
        return kwargs

    def get_success_url(self):
        return reverse('leads:lead-list')
    
    def form_valid(self, form):
        agent = form.cleaned_data['agent']
        lead = Lead.objects.get(id=self.kwargs['pk'])
        lead.agent = agent
        lead.save()
        return super(AssignAgentView, self).form_valid(form)
    

class CategoryListView(LoginRequiredMixin, generic.ListView):
    template_name = 'leads/category_list.html'
    context_object_name = 'category_list'

    def get_context_data(self, **kwargs):
        context = super(CategoryListView, self).get_context_data(**kwargs)

        user = self.request.user
        if user.is_organisor:
            queryset = Lead.objects.filter(organisation=user.userprofile)
        else:
            queryset = Lead.objects.filter(organisation=user.agent.organisation)

        context.update({
            'unassigned_leads_count': queryset.filter(category__isnull=True).count(),
        })
        return context

    def get_queryset(self):
        user = self.request.user
        if user.is_organisor:
            queryset = Category.objects.filter(
                organisation = user.userprofile,
            )
        else:
            queryset = Category.objects.filter(
                organisation = user.agent.organisation,
            )

        return queryset


class CategoryCreateView(OrgainsorAndLoginRequiredMixin, generic.CreateView):
    template_name = 'leads/create_category.html'
    form_class = CategoryModelForm

    def get_success_url(self):
        return reverse("leads:category-list")
    
    def form_valid(self, form):
        # TODO send email
        category = form.save(commit=False)
        category.organisation = self.request.user.userprofile
        category.save()
        return super(CategoryCreateView, self).form_valid(form)


class CategoryUpdateView(OrgainsorAndLoginRequiredMixin, generic.UpdateView):
    template_name = 'leads/update_category.html'
    form_class = CategoryModelForm

    def get_success_url(self):
        return reverse("leads:category-list")
    
    def get_queryset(self):
        user = self.request.user
        if user.is_organisor:
            queryset = Category.objects.filter(organisation=user.userprofile)
        else:
            queryset = Category.objects.filter(organisation=user.agent.organisation)
        
        return queryset
    
   
class CategoryDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = "leads/category_details.html"
    context_object_name = 'category'
    
    # def get_context_data(self, **kwargs):
    #     context = super(CategoryDetailView, self).get_context_data(**kwargs)

    #     leads = self.get_object().leads.all()

    #     context.update({
    #         'leads': leads,
    #     })
    #     return context
    
    def get_queryset(self):
        user = self.request.user
        if user.is_organisor:
            queryset = Category.objects.filter(organisation=user.userprofile)
        else:
            queryset = Category.objects.filter(organisation=user.agent.organisation)
        
        return queryset
    

class CategoryDeleteView(OrgainsorAndLoginRequiredMixin, generic.DeleteView):
    template_name = 'leads/category_delete.html'

    def get_success_url(self) -> str:
        return reverse('leads:category-list')
    
    def get_queryset(self):
        user = self.request.user

        if user.is_organisor:
            queryset = Category.objects.filter(organisation=user.userprofile)
        else:
            queryset = Category.objects.filter(organisation=user.agent.organisation)
            queryset = queryset.filter(agent__user=user)
        return queryset
