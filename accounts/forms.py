from django import forms
from .models import CustomUser
import pycountry


class RegisterForm(forms.Form):
    username = forms.CharField(
        max_length=100,
        label="Username",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username'
        })
    )
    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
    )
    role = forms.ChoiceField(
        label="Register As",
        choices=[('', 'Select Role'), ('patient', 'Patient'), ('practitioner', 'Practitioner')],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data


class LoginForm(forms.Form):
    username_or_email = forms.CharField(
        label="Username or Email",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username or email'
        })
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        username_or_email = cleaned_data.get('username_or_email')
        password = cleaned_data.get('password')

        if username_or_email and password:
            # Import here to avoid circular imports
            from django.contrib.auth import authenticate
            from .models import CustomUser
            
            # Try to authenticate with the provided value as both username and email
            user = authenticate(username=username_or_email, password=password)
            
            # If authentication fails, try to find by email and authenticate with username
            if not user:
                try:
                    # Find user by email
                    user_by_email = CustomUser.objects.get(email=username_or_email)
                    user = authenticate(username=user_by_email.username, password=password)
                except CustomUser.DoesNotExist:
                    user = None
                except CustomUser.MultipleObjectsReturned:
                    # If multiple users with same email (shouldn't happen with proper constraints)
                    user_by_email = CustomUser.objects.filter(email=username_or_email).first()
                    if user_by_email:
                        user = authenticate(username=user_by_email.username, password=password)
                    else:
                        user = None

            if not user:
                raise forms.ValidationError("Invalid username/email or password.")
            
            # Store the user instance for use in the view
            cleaned_data['user'] = user

        return cleaned_data



# accounts/forms.py
import pycountry
from django import forms
from .models import CustomUser

class ProfileForm(forms.ModelForm):
    # Country field using pycountry
    country = forms.ChoiceField(
        choices=[('', 'Select Country')] + [(country.alpha_2, country.name) for country in pycountry.countries],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'country-select'
        })
    )
    
    # Custom location field that combines with country
    city = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your city'
        })
    )
    
    class Meta:
        model = CustomUser
        fields = [
            'username', 'first_name', 'last_name', 
            'gender', 'phone', 'date_of_birth', 'profile_picture', 'bio'
        ]
        labels = {
            'username': 'Username',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'gender': 'Gender',
            'phone': 'Phone Number',
            'date_of_birth': 'Date of Birth',
            'profile_picture': 'Profile Picture',
            'bio': 'Bio',
        }
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter username'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter last name'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-select',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1 (555) 123-4567'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'placeholder': 'YYYY-MM-DD'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us a bit about yourself...'
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize location fields from existing location data
        if self.instance and self.instance.location:
            location_parts = self.instance.location.split(', ')
            if len(location_parts) > 1:
                self.fields['city'].initial = location_parts[0]
                self.fields['country'].initial = location_parts[1] if len(location_parts) > 1 else ''
        
        # Set gender choices
        self.fields['gender'].choices = [('', 'Select Gender')] + list(self.fields['gender'].choices)[1:]
    
    def save(self, commit=True):
        user = super().save(commit=False)
        # Combine city and country into location
        city = self.cleaned_data.get('city', '')
        country_code = self.cleaned_data.get('country', '')
        
        if city and country_code:
            country_name = dict(self.fields['country'].choices).get(country_code, '')
            user.location = f"{city}, {country_name}"
        elif city:
            user.location = city
        elif country_code:
            country_name = dict(self.fields['country'].choices).get(country_code, '')
            user.location = country_name
        else:
            user.location = ''
            
        if commit:
            user.save()
        return user

from django import forms
from .models import DoctorVerification

class DoctorVerificationForm(forms.ModelForm):
    class Meta:
        model = DoctorVerification
        fields = ['full_name', 'phone_number', 'hospital_name', 'license_number', 'document']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'hospital_name': forms.TextInput(attrs={'class': 'form-control'}),
            'license_number': forms.TextInput(attrs={'class': 'form-control'}),
            'document': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }




# Password Reset Forms
class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )

class PasswordResetForm(forms.Form):
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'New password'
        }),
        min_length=8
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password'
        })
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self):
        password = self.cleaned_data['password1']
        self.user.set_password(password)
        self.user.save()
        return self.user