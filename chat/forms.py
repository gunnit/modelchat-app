from allauth.account.forms import SignupForm
from django import forms
from .models import CustomUser, DigitalPersona

USER_TYPE_CHOICES = (
    ('MODEL', 'Model'),
    ('FAN', 'Fan'),
)

class CustomSignupForm(SignupForm):
    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES, widget=forms.RadioSelect)

    def save(self, request):
        # First, use the original save method to save the user object
        user = super(CustomSignupForm, self).save(request)
        
        # Now, save the custom field (user_type) to the user object
        user.user_type = self.cleaned_data['user_type']
        user.save()

        # Return the user object
        return user

class UpdateProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'profile_image', 'age', 'bio', 'location']



class UpdateDigitalPersonaForm(forms.ModelForm):
    RESPONSE_SPEED_CHOICES = [
        ('fast', 'Fast'),
        ('medium', 'Medium'),
        ('slow', 'Slow'),
    ]

    RESPONSE_LENGTH_CHOICES = [
        ('short', 'Short'),
        ('medium', 'Medium'),
        ('long', 'Long'),
    ]

    RESPONSE_STYLE_CHOICES = [
        ('formal', 'Formal'),
        ('casual', 'Casual'),
        ('playful', 'Playful'),
    ]

    response_speed = forms.ChoiceField(choices=RESPONSE_SPEED_CHOICES, required=False)
    response_length = forms.ChoiceField(choices=RESPONSE_LENGTH_CHOICES, required=False)
    response_style = forms.ChoiceField(choices=RESPONSE_STYLE_CHOICES, required=False)

    class Meta:
        model = DigitalPersona
        fields = ['greeting_message', 'response_speed', 'response_length', 'response_style']
