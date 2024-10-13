from django import forms

class TwoFactorAuthForm(forms.Form):
	code = forms.CharField(
		max_length=6,
		min_length=6,
		required=True,
	)
 
class BackupCodeForm(forms.Form):
    code = forms.CharField(
        max_length=8,
        min_length=8, 
        required=True,
    )