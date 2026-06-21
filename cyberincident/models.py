from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Profile(models.Model):
    ROLE_CHOICES = [
        ('staff', 'Mfanyakazi'),
        ('ict', 'Mchambuzi wa ICT'),
        ('admin', 'Msimamizi'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff')
    hospital_id = models.CharField(max_length=20, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
    
    def get_full_name(self):
        return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username

class Incident(models.Model):
    CATEGORY_CHOICES = [
        ('phishing', 'Ulaghai wa Barua Pepe'),
        ('ransomware', 'Mashambulizi ya Ransomware'),
        ('unauthorized', 'Upatikanaji Bila Idhini'),
        ('malware', 'Virusi / Malware'),
        ('ddos', 'Mashambulizi ya DDoS'),
        ('insider', 'Tishio la Ndani'),
        ('data_breach', 'Uvujaji wa Data'),
        ('other', 'Nyingine'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Wazi / Mpya'),
        ('investigating', 'Inachunguzwa'),
        ('contained', 'Imezuiliwa'),
        ('resolved', 'Imetatuliwa'),
        ('closed', 'Imefungwa'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Ya Chini'),
        ('medium', 'Ya Kati'),
        ('high', 'Ya Juu'),
        ('critical', 'Muhimu Sana'),
    ]
    
    # Basic fields
    title = models.CharField(max_length=200, verbose_name='Kichwa')
    description = models.TextField(verbose_name='Maelezo')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name='Aina')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open', verbose_name='Hali')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium', verbose_name='Kiwango')
    
    # Relationships
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_incidents', verbose_name='Mripoti')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_incidents', verbose_name='Imepewa')
    
    # Additional information
    affected_systems = models.TextField(blank=True, null=True, verbose_name='Mifumo Iliyoathirika')
    impact_description = models.TextField(blank=True, null=True, verbose_name='Athari')
    root_cause = models.TextField(blank=True, null=True, verbose_name='Chanzo')
    
    # Timestamps
    reported_at = models.DateTimeField(auto_now_add=True, verbose_name='Tarehe ya Kuripoti')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Tarehe ya Sasisho')
    resolved_at = models.DateTimeField(blank=True, null=True, verbose_name='Tarehe ya Kutatuliwa')
    
    # Flags
    is_confidential = models.BooleanField(default=False, verbose_name='Siri')
    is_escalated = models.BooleanField(default=False, verbose_name='Imepelekwa Juu')
    
    def __str__(self):
        return f"#{self.id} - {self.title}"
    
    def get_status_color(self):
        colors = {
            'open': 'warning',
            'investigating': 'info',
            'contained': 'primary',
            'resolved': 'success',
            'closed': 'secondary',
        }
        return colors.get(self.status, 'secondary')
    
    def get_priority_color(self):
        colors = {
            'low': 'success',
            'medium': 'warning',
            'high': 'danger',
            'critical': 'danger',
        }
        return colors.get(self.priority, 'secondary')
    
    def get_status_display_sw(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)
    
    def get_category_display_sw(self):
        return dict(self.CATEGORY_CHOICES).get(self.category, self.category)
    
    def get_priority_display_sw(self):
        return dict(self.PRIORITY_CHOICES).get(self.priority, self.priority)
    
    class Meta:
        ordering = ['-reported_at']

class Evidence(models.Model):
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='evidences')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_evidences')
    file = models.FileField(upload_to='evidence/%Y/%m/%d/')
    file_name = models.CharField(max_length=255)
    file_size = models.IntegerField(help_text='Ukubwa wa faili katika bytes')
    file_type = models.CharField(max_length=50, help_text='Aina ya faili')
    description = models.CharField(max_length=255, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    
    def __str__(self):
        return self.file_name
    
    def get_file_size_display(self):
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} GB"
    
    def get_icon_class(self):
        icons = {
            '.pdf': 'fa-file-pdf text-danger',
            '.png': 'fa-file-image text-primary',
            '.jpg': 'fa-file-image text-primary',
            '.jpeg': 'fa-file-image text-primary',
            '.txt': 'fa-file-alt text-secondary',
            '.log': 'fa-file-alt text-secondary',
            '.csv': 'fa-file-csv text-success',
            '.xlsx': 'fa-file-excel text-success',
            '.zip': 'fa-file-archive text-warning',
            '.rar': 'fa-file-archive text-warning',
        }
        ext = '.' + self.file_type.split('/')[-1] if '/' in self.file_type else ''
        return icons.get(ext.lower(), 'fa-file')

class ResponseAction(models.Model):
    ACTION_CHOICES = [
        ('investigation', 'Uchunguzi'),
        ('containment', 'Uzuiaji'),
        ('eradication', 'Kuondoa Tishio'),
        ('recovery', 'Kurejesha Mifumo'),
        ('notification', 'Arifu kwa Wadau'),
        ('reporting', 'Kuripoti kwa Mamlaka'),
        ('patch', 'Kusasisha Programu'),
        ('backup', 'Kurejesha Backup'),
        ('training', 'Mafunzo kwa Wafanyakazi'),
        ('other', 'Nyingine'),
    ]
    
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='actions')
    performer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='performed_actions')
    action_type = models.CharField(max_length=20, choices=ACTION_CHOICES)
    action_text = models.TextField(help_text='Maelezo ya hatua iliyochukuliwa')
    timestamp = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True, help_text='Maelezo ya ziada')
    
    def __str__(self):
        return f"{self.get_action_type_display()} - {self.incident.title}"
    
    def get_action_type_display_sw(self):
        return dict(self.ACTION_CHOICES).get(self.action_type, self.action_type)
    
    def get_action_icon(self):
        icons = {
            'investigation': 'fa-search',
            'containment': 'fa-shield-alt',
            'eradication': 'fa-skull',
            'recovery': 'fa-undo',
            'notification': 'fa-bell',
            'reporting': 'fa-flag',
            'patch': 'fa-wrench',
            'backup': 'fa-database',
            'training': 'fa-graduation-cap',
            'other': 'fa-cog',
        }
        return icons.get(self.action_type, 'fa-circle')
    
    def get_action_color(self):
        colors = {
            'investigation': 'primary',
            'containment': 'warning',
            'eradication': 'danger',
            'recovery': 'success',
            'notification': 'info',
            'reporting': 'secondary',
            'patch': 'dark',
            'backup': 'primary',
            'training': 'light',
            'other': 'secondary',
        }
        return colors.get(self.action_type, 'secondary')
    
    class Meta:
        ordering = ['-timestamp']