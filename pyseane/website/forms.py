from django import forms
from .models import campagne_fish


class RegistrationForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control form-control-lg', 'minlength': 3}),
        required=True
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control form-control-lg'}),
        required=True
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg', 'minlength': 8}),
        required=True
    )
    accept_terms = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        required=True
    )


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
        required=True
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg'}),
        required=True
    )


class CampagneForm(forms.Form):
    name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control form-control-lg'}),
        required=True
    )
    url = forms.URLField(
        label='URL',
        required=True,
        widget=forms.URLInput(attrs={'class': 'form-control form-control-lg'})
    )


class CampagneUtilisateurForm(forms.Form):
    def __init__(self, utilisateur, selected_campagne_id, *args, **kwargs):
        super(CampagneUtilisateurForm, self).__init__(*args, **kwargs)

        # Filtrer les campagnes avant d'appeler super().__init__()
        campagnes = campagne_fish.objects.filter(utilisateur=utilisateur)
        selected_camp = campagnes.get(id=selected_campagne_id)

        choice_camp = campagnes.exclude(id=selected_campagne_id)

        self.fields['campagne'] = forms.ModelChoiceField(
            queryset=choice_camp,
            empty_label=selected_camp.nom,  # Ajouter cette ligne
            widget=forms.Select(attrs={
                'class': 'form-control custom-select',  # Ajouter des classes de style personnalisé
                'style': 'font-size: 16px; height: 38px; width: 200px;',  # Ajouter des styles personnalisés
                'onchange': 'this.form.submit();',
            }),
            label=''
        )


class EmailForm(forms.Form):
    MAIL_TYPE_CHOICES = [
        ("1", "qYdDfdgYKEUZcc@outlook.fr"),
        ("0", "Mon propre email")
    ]
    CONTENT_TEMPLATE = [
        ("0", "Mon propre texte"),
        ("1", "Netflix")
    ]
    mailtype = forms.CharField(label='Mail envoyeur', widget=forms.Select(attrs={'class': 'form-control form-control-lg template-dropdown mx-left form-mailtype'},choices=MAIL_TYPE_CHOICES),)
    mail = forms.CharField(label='Mail', required=False, max_length=100, initial='',widget=forms.TextInput(attrs={'class': 'form-control name-form'}))
    password = forms.CharField(label='Password', required=False, max_length=100, widget=forms.PasswordInput(attrs={'class': 'form-control name-form'}), initial='' )
    name = forms.CharField(label='Nom à afficher', max_length=100, required=True, initial='' ,widget=forms.TextInput(attrs={'class': 'form-control name-form' , 'style' : 'height:4vw'}))
    receiver = forms.CharField(label='Liste des cibles', widget=forms.Textarea(attrs={'class': 'clear-on-click content-form receiver-form'}), required=True, initial='Un mail par ligne exemple :\njon.doe@google.fr\nalice.bob@google.fr')
    template = forms.CharField(
    label='Mail template',
    widget=forms.Select(attrs={'class': 'form-control form-control-lg template-dropdown mx-left'}, choices=CONTENT_TEMPLATE),
    )
    subject = forms.CharField(label='Corps', max_length=100, required=True, initial='', widget=forms.TextInput(attrs={'class': 'form-control subject-form', 'style' : 'height:4vw'}))

    content = forms.CharField(label='Contenu', widget=forms.Textarea(attrs={'class': 'content-form'}), required=True, initial='')
