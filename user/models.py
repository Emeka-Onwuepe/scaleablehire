from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin




# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self, email,full_name,role='staff',team=None,
                    password=None, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password,full_name='Creator', **extra_fields):
        extra_fields.setdefault('staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin', True)
        return self.create_user(email=email,full_name=full_name, password=password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):

    ROLE_MANAGER = 'manager'
    ROLE_TEAM_LEAD = 'team_lead'
    ROLE_STAFF = 'staff'
    ROLE_CHOICES = [
        (ROLE_MANAGER, 'Manager'),
        (ROLE_TEAM_LEAD, 'Team Lead'),
        (ROLE_STAFF, 'Staff'),
    ]

    full_name = models.CharField(max_length=200)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    team = models.ForeignKey('dashboard.Team', null=True, blank=True, on_delete=models.SET_NULL)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)


    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f'{self.full_name} ({self.role})'

    @property
    def is_manager(self):
        return self.role == self.ROLE_MANAGER

    @property
    def is_team_lead(self):
        return self.role == self.ROLE_TEAM_LEAD

    @property
    def is_staff_role(self):
        return self.role == self.ROLE_STAFF
    
    def has_perm(self, perm, obj=None):
        if self.is_admin and self.staff:
            return True

    # remember to set appropriate permissions.
    def has_module_perms(self, app_label):
        if self.is_admin and self.staff:
           return True
        
    @property
    def is_staff(self):
        return self.staff
    

    