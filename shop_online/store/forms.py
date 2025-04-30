from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Profile, Review




# SignUpForm for user registration
class SignUpForm(forms.ModelForm):
    email = forms.EmailField(required=True)  # Email field, required for registration
    password1 = forms.CharField(widget=forms.PasswordInput)  # Password field, will be used for the user's password
    password2 = forms.CharField(widget=forms.PasswordInput)  # Confirmation password field, to match password1
    

    class Meta:
        model = User  # Specifies that this form is related to the User model
        fields = ('username', 'email', 'password1', 'password2')  # Fields that will appear in the registration form

    # Method to check if the passwords match
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:  # If password1 and password2 are different, raise an error
            raise forms.ValidationError("Passwords don't match!")
        return password2



    # Save method to hash the user's password and save the user object
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user



# ProfileForm for user profile editing (in this case, setting the user's city)
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile  # Specifies that this form is related to the Profile model
        fields = ['city', 'phone_number', 'birth_date', 'address']  
    birth_date = forms.DateField(input_formats=['%Y-%m-%d'], widget=forms.DateInput(attrs={'type': 'date'}))



class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Your Name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Your Email'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Your Message'})) 

# Review forms
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'text']  # Access to the fields of the Review model

    rating = forms.ChoiceField(choices=[(i, str(i)) for i in range(1, 6)], widget=forms.RadioSelect)  # Rate the product from 1 to 5
    text = forms.CharField(widget=forms.Textarea, required=True)  # Text field for the review