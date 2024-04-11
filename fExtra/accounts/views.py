from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q, Count
from django.http import JsonResponse, Http404, HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic import ListView, UpdateView

from .forms import MagistrateRegistrationForm, UserRegisterForm, UserUpdateForm
from .models import User, MagistrateParent

User = get_user_model()

class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'accounts/user_list.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            # messages.error(request, _('You do not have permission to view this page.'))
            return HttpResponseRedirect(reverse('home'))
        return super().dispatch(request, *args, **kwargs)

    def get_active_status_filter(self):
        is_active_str = self.request.GET.get('is_active')
        if is_active_str is not None:
            return is_active_str.lower() in ['true', '1', 't']
        return None

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            magistrates_list = [{
                'id': mag.id,
                'profile_image_url': self.get_image_url(mag),
                'first_name': mag.first_name,
                'last_name': mag.last_name,
                'email': mag.email,
                'role': mag.role,
                'parents_count': mag.parents_count
            } for mag in context['magistrates']]

            parents_list = [{
                'id': parent.id,
                'profile_image_url': self.get_image_url(parent),
                'first_name': parent.first_name,
                'last_name': parent.last_name,
                'email': parent.email,
                'magistrates_assigned': [
                    mag.magistrate.last_name for mag in parent.magistrates_assigned.all()
                    if mag.magistrate.is_active or not parent.is_active
                ]  #inclusion parent & magistrat actives
            } for parent in context['parents_filtered']]

            return JsonResponse({'magistrates': magistrates_list, 'parents': parents_list})
        else:
            return super().render_to_response(context, **response_kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        is_active = self.get_active_status_filter()

        magistrates_query = User.objects.filter(
            Q(is_staff=True) | Q(is_superuser=True) | Q(role='admin') | Q(role='magistrate')
        )
        parents_query = User.objects.exclude(id__in=magistrates_query.values('id')).prefetch_related('magistrates_assigned__magistrate')

        if is_active is not None:
            magistrates_query = magistrates_query.filter(is_active=is_active)
            parents_query = parents_query.filter(is_active=is_active)

        context['magistrates'] = magistrates_query.annotate(parents_count=Count('parents_assigned'))

        if self.request.user.role == 'magistrate':
            context['parents_filtered'] = parents_query.filter(magistrates_assigned__magistrate=self.request.user).distinct()
        else:
            context['parents_filtered'] = parents_query

        return context


    def get_image_url(self, user):
        if user.profile_image and hasattr(user.profile_image, 'url'):
            return self.request.build_absolute_uri(user.profile_image.url)
        else:
            return self.request.build_absolute_uri(settings.MEDIA_URL + 'profile_images/default.jpg')


class UserUpdateView(UserPassesTestMixin, UpdateView):
    model = User
    template_name = 'accounts/user_update.html'
    success_url = reverse_lazy('accounts:user_list')
    form_class = UserUpdateForm


    def get_form_kwargs(self):
        kwargs = super(UserUpdateView, self).get_form_kwargs()
        kwargs['request_user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        user = form.save(commit=False)

        if 'is_active_toggle' in self.request.POST:
            user.is_active = not user.is_active
        user.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _('There was a problem updating your profile. Please check the form for errors.'))
        return super().form_invalid(form)

    def test_func(self):
        user_to_update = self.get_object()
        request_user = self.request.user
        if not self.has_permission(user_to_update, request_user):
            messages.error(self.request, _('You do not have permission to update this profile.'))
            return False
        return True

    def get_user_to_update(self):
        return get_object_or_404(User, pk=self.kwargs.get('pk'))

    def has_permission(self, user_to_update, request_user):
        # admin update all except other admin
        if request_user.is_superuser:
            return not user_to_update.is_superuser or user_to_update == request_user

        if request_user.is_magistrate:
            if user_to_update == request_user:
                return True
            return MagistrateParent.objects.filter(magistrate=request_user, parent=user_to_update).exists()

        if request_user.is_parent:
            return user_to_update == request_user

        return False  # default deny

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if not self.has_permission(obj, self.request.user):
            raise Http404(_("You do not have permission to update this profile."))
        return obj



@login_required
@permission_required('accounts.add_user', raise_exception=True)
@user_passes_test(lambda u: u.is_superuser, login_url='/login/')
def register_magistrate(request):
    if request.method == 'POST':
        form = MagistrateRegistrationForm(request.POST)
        if form.is_valid():
            magistrate = form.save()
            messages.success(request, _('Magistrate "%s" registered successfully.' % magistrate.email))
            return redirect(reverse('accounts:user_list'))
    else:
        form = MagistrateRegistrationForm()
    return render(request, 'registration/register_magistrate.html', {'form': form})


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'parent'
            user.national_number_raw = form.cleaned_data['national_number']
            formatted_number = form.cleaned_data['national_number'][:2] + '.' + form.cleaned_data['national_number'][2:4] + '.' + form.cleaned_data['national_number'][4:6] + '-' + form.cleaned_data['national_number'][6:9] + '.' + form.cleaned_data['national_number'][9:]
            user.national_number = formatted_number
            user.save()

            if not request.user.is_authenticated:
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                messages.success(request, _("Your account has been created! You are now logged in."))
                return redirect('home')

            else:
                if request.user.role == 'magistrate':
                    MagistrateParent.objects.create(magistrate=request.user, parent=user)

                messages.success(request, _("The parent account has been successfully created."))
                return redirect('/accounts/list/')

    else:
        form = UserRegisterForm()
    return render(request, 'registration/register.html', {'form': form})


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'registration/password_reset.html'
    email_template_name = 'registration/password_reset_mail.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly. " \
                      "If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('home')


class PasswordResetConfirmationView(PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirmation.html'
    post_reset_login = False
    success_url = reverse_lazy('accounts:login')

