from allauth.account.forms import SignupForm
from django import forms

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
