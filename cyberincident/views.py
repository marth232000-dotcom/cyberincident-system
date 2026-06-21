from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.utils import timezone
from .models import Incident, Evidence, ResponseAction, Profile
from .forms import IncidentForm, IncidentUpdateForm, EvidenceForm, ResponseActionForm, UserRegistrationForm

# ========== AUTHENTICATION VIEWS ==========

def index(request):
    return render(request, 'index.html')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                # Hakikisha profile imeundwa
                profile, created = Profile.objects.get_or_create(
                    user=user,
                    defaults={
                        'role': form.cleaned_data.get('role', 'staff'),
                        'department': form.cleaned_data.get('department', ''),
                        'is_active': True
                    }
                )
                login(request, user)
                messages.success(request, 'Akaunti imeundwa kikamilifu! Karibu CIRS.')
                return redirect('dashboard')
            except Exception as e:
                messages.error(request, f'Kosa: {str(e)}')
                return render(request, 'register.html', {'form': form})
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Karibu tena, {user.get_full_name() or user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Jina la mtumiaji au neno siri si sahihi!')
    return render(request, 'login.html')

@login_required
def user_logout(request):
    logout(request)
    messages.info(request, 'Umefanikiwa kutoka. Tutaonana tena!')
    return redirect('login')

# ========== DASHBOARD VIEW ==========

@login_required
def dashboard(request):
    user = request.user
    incidents = Incident.objects.filter(reporter=user)
    
    # Hakikisha profile ipo
    try:
        profile = user.profile
        is_admin = profile.role == 'admin'
        is_ict = profile.role in ['ict', 'admin']
    except:
        # Unda profile kwa auto
        Profile.objects.create(user=user, role='staff', department='Unknown', is_active=True)
        is_admin = False
        is_ict = False
    
    context = {
        'total_incidents': incidents.count(),
        'open_incidents': incidents.filter(status='open').count(),
        'investigating_incidents': incidents.filter(status='investigating').count(),
        'resolved_incidents': incidents.filter(status='resolved').count(),
        'recent_incidents': incidents.order_by('-reported_at')[:5],
        'is_admin': is_admin,
        'is_ict': is_ict,
        'all_incidents': Incident.objects.all().count() if is_ict else 0,
        'assigned_incidents': Incident.objects.filter(assigned_to=user).count() if is_ict else 0,
    }
    return render(request, 'dashboard.html', context)

# ========== INCIDENT VIEWS (CRUD) ==========

@login_required
def incident_list(request):
    try:
        profile = request.user.profile
        is_ict = profile.role in ['ict', 'admin']
    except:
        is_ict = False
    
    if is_ict:
        incidents = Incident.objects.all()
    else:
        incidents = Incident.objects.filter(reporter=request.user)
    
    # Search
    q = request.GET.get('q', '')
    if q:
        incidents = incidents.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(affected_systems__icontains=q)
        )
    
    # Filter
    status = request.GET.get('status', '')
    if status:
        incidents = incidents.filter(status=status)
    
    priority = request.GET.get('priority', '')
    if priority:
        incidents = incidents.filter(priority=priority)
    
    paginator = Paginator(incidents.order_by('-reported_at'), 10)
    page = request.GET.get('page', 1)
    incidents_page = paginator.get_page(page)
    
    context = {
        'incidents': incidents_page,
        'total_count': incidents.count(),
        'is_ict': is_ict,
    }
    return render(request, 'incident_list.html', context)

@login_required
def incident_detail(request, pk):
    incident = get_object_or_404(Incident, id=pk)
    
    try:
        profile = request.user.profile
        is_ict = profile.role in ['ict', 'admin']
    except:
        is_ict = False
    
    # Check permission
    if not is_ict and incident.reporter != request.user:
        messages.error(request, 'Huna ruhusa ya kuona tukio hili.')
        return redirect('incident_list')
    
    evidences = incident.evidences.all()
    actions = incident.actions.all().order_by('-timestamp')
    
    context = {
        'incident': incident,
        'evidences': evidences,
        'actions': actions,
        'is_ict': is_ict,
    }
    return render(request, 'incident_detail.html', context)

@login_required
def incident_create(request):
    if request.method == 'POST':
        form = IncidentForm(request.POST)
        if form.is_valid():
            incident = form.save(commit=False)
            incident.reporter = request.user
            incident.save()
            messages.success(request, f'Tukio "{incident.title}" limeundwa kikamilifu!')
            return redirect('incident_detail', pk=incident.id)
    else:
        form = IncidentForm()
    return render(request, 'incident_create.html', {'form': form})

@login_required
def incident_update(request, pk):
    incident = get_object_or_404(Incident, id=pk)
    
    try:
        profile = request.user.profile
        is_ict = profile.role in ['ict', 'admin']
    except:
        is_ict = False
    
    # Check permission
    if not is_ict and incident.reporter != request.user:
        messages.error(request, 'Huna ruhusa ya kuhariri tukio hili!')
        return redirect('incident_list')
    
    if request.method == 'POST':
        form = IncidentUpdateForm(request.POST, instance=incident)
        if form.is_valid():
            incident = form.save(commit=False)
            incident.updated_at = timezone.now()
            if incident.status == 'resolved' and not incident.resolved_at:
                incident.resolved_at = timezone.now()
            elif incident.status != 'resolved':
                incident.resolved_at = None
            incident.save()
            messages.success(request, f'Tukio "{incident.title}" limehaririwa kikamilifu!')
            return redirect('incident_detail', pk=incident.id)
    else:
        form = IncidentUpdateForm(instance=incident)
    
    context = {'form': form, 'incident': incident}
    return render(request, 'incident_update.html', context)

@login_required
def incident_delete(request, pk):
    incident = get_object_or_404(Incident, id=pk)
    
    try:
        profile = request.user.profile
        is_ict = profile.role in ['ict', 'admin']
    except:
        is_ict = False
    
    # Check permission
    if not is_ict and incident.reporter != request.user:
        messages.error(request, 'Huna ruhusa ya kufuta tukio hili!')
        return redirect('incident_list')
    
    if request.method == 'POST':
        title = incident.title
        incident.delete()
        messages.success(request, f'Tukio "{title}" limefutwa kikamilifu!')
        return redirect('incident_list')
    
    return render(request, 'incident_delete.html', {'incident': incident})

# ========== EVIDENCE VIEWS (CRUD) ==========

@login_required
def evidence_upload(request, incident_id):
    incident = get_object_or_404(Incident, id=incident_id)
    
    try:
        profile = request.user.profile
        is_ict = profile.role in ['ict', 'admin']
    except:
        is_ict = False
    
    # Check permission
    if not is_ict and incident.reporter != request.user:
        messages.error(request, 'Huna ruhusa ya kupakia ushahidi kwa tukio hili!')
        return redirect('incident_detail', pk=incident_id)
    
    if request.method == 'POST':
        form = EvidenceForm(request.POST, request.FILES)
        if form.is_valid():
            evidence = form.save(commit=False)
            evidence.incident = incident
            evidence.uploaded_by = request.user
            file_obj = request.FILES['file']
            evidence.file_name = file_obj.name
            evidence.file_size = file_obj.size
            evidence.file_type = file_obj.content_type
            evidence.save()
            messages.success(request, f'Ushahidi "{evidence.file_name}" umepakiwa kikamilifu!')
            return redirect('incident_detail', pk=incident_id)
    else:
        form = EvidenceForm()
    
    return render(request, 'evidence_upload.html', {'form': form, 'incident': incident})

@login_required
def evidence_delete(request, pk):
    evidence = get_object_or_404(Evidence, id=pk)
    incident_id = evidence.incident.id
    
    try:
        profile = request.user.profile
        is_ict = profile.role in ['ict', 'admin']
    except:
        is_ict = False
    
    # Check permission
    if not is_ict and evidence.uploaded_by != request.user:
        messages.error(request, 'Huna ruhusa ya kufuta ushahidi huu!')
        return redirect('incident_detail', pk=incident_id)
    
    if request.method == 'POST':
        file_name = evidence.file_name
        evidence.delete()
        messages.success(request, f'Ushahidi "{file_name}" umefutwa kikamilifu!')
        return redirect('incident_detail', pk=incident_id)
    
    return render(request, 'evidence_delete.html', {'evidence': evidence})

# ========== RESPONSE VIEWS (CRUD) ==========

@login_required
def response_create(request, incident_id):
    incident = get_object_or_404(Incident, id=incident_id)
    
    try:
        profile = request.user.profile
        is_ict = profile.role in ['ict', 'admin']
    except:
        is_ict = False
    
    if not is_ict:
        messages.error(request, 'Huna ruhusa ya kuongeza hatua!')
        return redirect('incident_detail', pk=incident_id)
    
    if request.method == 'POST':
        form = ResponseActionForm(request.POST)
        if form.is_valid():
            response = form.save(commit=False)
            response.incident = incident
            response.performer = request.user
            response.save()
            messages.success(request, 'Hatua imeongezwa kikamilifu!')
            return redirect('incident_detail', pk=incident_id)
    else:
        form = ResponseActionForm()
    
    return render(request, 'response_create.html', {'form': form, 'incident': incident})

@login_required
def response_update(request, pk):
    response = get_object_or_404(ResponseAction, id=pk)
    
    try:
        profile = request.user.profile
        is_ict = profile.role in ['ict', 'admin']
    except:
        is_ict = False
    
    if not is_ict:
        messages.error(request, 'Huna ruhusa ya kuhariri hatua hii!')
        return redirect('incident_detail', pk=response.incident.id)
    
    if request.method == 'POST':
        form = ResponseActionForm(request.POST, instance=response)
        if form.is_valid():
            form.save()
            messages.success(request, 'Hatua imehaririwa kikamilifu!')
            return redirect('incident_detail', pk=response.incident.id)
    else:
        form = ResponseActionForm(instance=response)
    
    context = {'form': form, 'response': response}
    return render(request, 'response_update.html', context)

@login_required
def response_delete(request, pk):
    response = get_object_or_404(ResponseAction, id=pk)
    incident_id = response.incident.id
    
    try:
        profile = request.user.profile
        is_ict = profile.role in ['ict', 'admin']
    except:
        is_ict = False
    
    if not is_ict:
        messages.error(request, 'Huna ruhusa ya kufuta hatua hii!')
        return redirect('incident_detail', pk=incident_id)
    
    if request.method == 'POST':
        response.delete()
        messages.success(request, 'Hatua imefutwa kikamilifu!')
        return redirect('incident_detail', pk=incident_id)
    
    return render(request, 'response_delete.html', {'response': response})

# ========== ADMIN VIEWS ==========

@login_required
def user_management(request):
    try:
        profile = request.user.profile
        is_admin = profile.role == 'admin'
    except:
        is_admin = False
    
    if not is_admin:
        messages.error(request, 'Huna ruhusa ya kuona ukurasa huu!')
        return redirect('dashboard')
    
    users = User.objects.all().select_related('profile')
    
    # Search
    q = request.GET.get('q', '')
    if q:
        users = users.filter(
            Q(username__icontains=q) |
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(email__icontains=q)
        )
    
    # Filter by role
    role = request.GET.get('role', '')
    if role:
        users = users.filter(profile__role=role)
    
    context = {
        'users': users,
        'role_choices': Profile.ROLE_CHOICES,
    }
    return render(request, 'user_management.html', context)

@login_required
def toggle_user_status(request, user_id):
    try:
        profile = request.user.profile
        is_admin = profile.role == 'admin'
    except:
        is_admin = False
    
    if not is_admin:
        messages.error(request, 'Huna ruhusa!')
        return redirect('dashboard')
    
    user = get_object_or_404(User, id=user_id)
    if user == request.user:
        messages.error(request, 'Huwezi kubadilisha hali yako mwenyewe!')
        return redirect('user_management')
    
    user_profile = user.profile
    user_profile.is_active = not user_profile.is_active
    user_profile.save()
    user.is_active = user_profile.is_active
    user.save()
    
    status = 'imewashwa' if user_profile.is_active else 'imezimwa'
    messages.success(request, f'Akaunti ya {user.username} ime{status} kikamilifu.')
    return redirect('user_management')

@login_required
def delete_user(request, user_id):
    try:
        profile = request.user.profile
        is_admin = profile.role == 'admin'
    except:
        is_admin = False
    
    if not is_admin:
        messages.error(request, 'Huna ruhusa!')
        return redirect('dashboard')
    
    user = get_object_or_404(User, id=user_id)
    if user == request.user:
        messages.error(request, 'Huwezi kujifuta mwenyewe!')
        return redirect('user_management')
    
    username = user.username
    user.delete()
    messages.success(request, f'Akaunti ya {username} imefutwa kikamilifu.')
    return redirect('user_management')

# ========== REPORTS VIEW ==========

@login_required
def reports(request):
    try:
        profile = request.user.profile
        is_ict = profile.role in ['ict', 'admin']
    except:
        is_ict = False
    
    if not is_ict:
        messages.error(request, 'Huna ruhusa ya kuona ripoti!')
        return redirect('dashboard')
    
    incidents = Incident.objects.all()
    
    context = {
        'total_incidents': incidents.count(),
        'by_category': incidents.values('category').annotate(count=Count('id')),
        'by_status': incidents.values('status').annotate(count=Count('id')),
        'by_priority': incidents.values('priority').annotate(count=Count('id')),
        'recent_incidents': incidents.order_by('-reported_at')[:10],
    }
    return render(request, 'reports.html', context)