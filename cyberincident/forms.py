from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Incident, Evidence, ResponseAction, Profile

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Barua pepe'}))
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Jina la kwanza'}))
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Jina la ukoo'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Jina la mtumiaji'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Neno siri'}), label='Neno Siri')
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Thibitisha neno siri'}), label='Thibitisha Neno Siri')
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}), label='Jukumu')
    department = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Idara'}), label='Idara')
    hospital_id = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Namba ya kitambulisho'}), label='Namba ya Kitambulisho')
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Barua pepe hii tayari imesajiliwa.')
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Jina la mtumiaji tayari lipo.')
        return username
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # Unda profile
            Profile.objects.create(
                user=user,
                role=self.cleaned_data.get('role', 'staff'),
                department=self.cleaned_data.get('department', ''),
                hospital_id=self.cleaned_data.get('hospital_id', ''),
                is_active=True
            )
        return user

class IncidentForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = ['title', 'description', 'category', 'priority', 'affected_systems', 'impact_description', 'is_confidential']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Kichwa cha tukio'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Maelezo kamili ya tukio'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'affected_systems': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Mifumo iliyoathirika (mfano: Server ya barua pepe)'}),
            'impact_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Athari za tukio (mfano: Kukosa huduma kwa saa 2)'}),
            'is_confidential': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'title': 'Kichwa',
            'description': 'Maelezo',
            'category': 'Aina ya Tukio',
            'priority': 'Kiwango cha Dharura',
            'affected_systems': 'Mifumo Iliyoathirika',
            'impact_description': 'Athari',
            'is_confidential': 'Tukio la Siri',
        }

class IncidentUpdateForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = ['title', 'description', 'category', 'priority', 'status', 'assigned_to', 'affected_systems', 'impact_description', 'root_cause', 'is_confidential']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
            'affected_systems': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'impact_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'root_cause': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_confidential': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit assigned_to to ICT and Admin users
        ict_users = User.objects.filter(profile__role__in=['ict', 'admin'])
        self.fields['assigned_to'].queryset = ict_users
        self.fields['assigned_to'].empty_label = '-- Hapana --'

class EvidenceForm(forms.ModelForm):
    class Meta:
        model = Evidence
        fields = ['file', 'description']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Maelezo mafupi ya faili (Hiari)'}),
        }
        labels = {
            'file': 'Faili',
            'description': 'Maelezo',
        }

class ResponseActionForm(forms.ModelForm):
    class Meta:
        model = ResponseAction
        fields = ['action_type', 'action_text', 'notes', 'is_completed']
        widgets = {
            'action_type': forms.Select(attrs={'class': 'form-control'}),
            'action_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Maelezo ya hatua iliyochukuliwa...'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Maelezo ya ziada (Hiari)'}),
            'is_completed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'action_type': 'Aina ya Hatua',
            'action_text': 'Maelezo',
            'notes': 'Maelezo ya Ziada',
            'is_completed': 'Imekamilika',
        }