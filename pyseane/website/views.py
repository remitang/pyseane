from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt

from .models import Pyseane_User, campagne_fish, target
from .forms import RegistrationForm, LoginForm, CampagneForm, EmailForm
from .module.Pywebcloner import clone
from .module.Emailsender import TryConnection, EmailSender
from .forms import CampagneUtilisateurForm


def home(request):
    if request.user.is_authenticated:
        campagnes = campagne_fish.objects.filter(utilisateur=request.user)
        if campagnes:
            return redirect(panel)
        else:
            return redirect(campagne_register)
    else:
        return redirect(login_user)


def cgu(request):
    if request.method == 'GET':
        return render(request, 'pages/cgu.html')
    else:
        return HttpResponse("Méthode non supportée.", status=405)


def contexteMessage(msg, color, form):
    context = {'message': msg, 'color': color, 'form': form}
    return context


def register(request):
    if request.method == 'GET':
        form = RegistrationForm()
        return render(request, 'pages/register.html', {'form': form})
    elif request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            accept_terms = form.cleaned_data['accept_terms']

            if len(username) < 3 or len(password) < 8:
                message = "Le nom d'utilisateur doit comporter au moins 3 caractères et le mot de passe au moins 8 caractères."
                color = "red"
                context = contexteMessage(message, color, form)
                status = 400
            elif accept_terms != True:
                message = "Vous devez accepter les Conditions Générales d'Utilisation."
                color = "red"
                context = contexteMessage(message, color, form)
                status = 400
            else:
                Pyseane_User.objects.create_user(username=username, email=email, password=password)
                message = "Inscription réussie ! Connectez-vous avec votre nouveau compte."
                color = "green"
                # TODO  faire un trycatch pour les erreurs
                context = contexteMessage(message, color, form)
                status = 201
            return render(request, 'pages/register.html', context, status=status)
        else:
            redirect(register)
    else:
        return HttpResponse("Méthode non supportée.", status=405)


def login_user(request):
    if request.user.is_authenticated:
        return redirect(home)
    elif request.method == 'GET':
        form = LoginForm()
        return render(request, 'pages/login.html', {'form': form})
    elif request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                response = redirect('login_user')
                response.delete_cookie('campagne_id')
                return response
            else:
                form.add_error(None, 'Nom d\'utilisateur ou mot de passe incorrect.')


def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect(login_user)


def campagne_register(request):
    if request.user.is_authenticated:
        if request.method == 'GET':
            form = CampagneForm()
            return render(request, 'pages/campagne.html', {'form': form})
        elif request.method == 'POST':
            form = CampagneForm(data=request.POST)
            if form.is_valid():
                nom_campagne = form.cleaned_data.get('name')
                url_campagne = form.cleaned_data.get('url')
                nouvelle_campagne = campagne_fish.objects.create(
                    utilisateur=request.user,
                    nom=nom_campagne,
                    url=url_campagne.split("?")[0]
                )
                res = clone(nouvelle_campagne.id, url_campagne)
                if res:
                    # TODO trycatch ici
                    nouvelle_campagne.save()
                return redirect(panel)
        return HttpResponse("Méthode non supportée.", status=405)
    else:
        redirect(home)


@csrf_exempt
def detail_campagne(request, id):
    target_id = request.GET.get('follow')
    campagnes = campagne_fish.objects.get(id=id)

    if request.method == 'GET':
        if target_id:
            try:
                ma_target = target.objects.get(id_email_uuid=target_id)
                if not ma_target.has_open:
                    ma_target.has_read = True  # TODO trouver un moyen de faire du suivie de mail
                    ma_target.has_open = True
                    ma_target.save()
            except Exception:
                return render(request, "pages/pages_fishing/" + str(campagnes.id) + ".html")
        return render(request, "pages/pages_fishing/" + str(campagnes.id) + ".html")

    elif request.method == 'POST':
        try:
            ma_target = target.objects.get(id_email_uuid=target_id)
            if not ma_target.has_logged:
                ma_target.has_logged = True
                ma_target.save()
        except Exception:
            return render(request, "pages/pages_fishing/" + str(campagnes.id) + ".html")
        return render(request, "pages/pages_fishing/" + str(campagnes.id) + ".html")
    else:
        return HttpResponse("Méthode non supportée.", status=405)


def panel(request):
    if request.user.is_authenticated:
        campagne_id = request.COOKIES.get('campagne_id', 'null')

        # Récupérer la campagne actuellement sélectionnée
        if campagne_id == "null":
            selected_campagne = campagne_fish.objects.filter(utilisateur=request.user).first()
            if selected_campagne:
                response = redirect("panel")
                response.set_cookie('campagne_id', str(selected_campagne.id))
                return response
            else:
                return redirect(campagne_register)

        if 'campagne' in request.GET:
            form = CampagneUtilisateurForm(request.user, campagne_id, request.GET)
            if form.is_valid():
                selected_campagne = form.cleaned_data['campagne']
                response = redirect("panel")
                response.set_cookie('campagne_id', str(selected_campagne.id))
                return response
        else:
            form = CampagneUtilisateurForm(request.user, campagne_id)

        selected_campagne = campagne_fish.objects.get(id=campagne_id)

        nb_tar = target.objects.filter(campagne=selected_campagne).count()
        nb_tar_has_open = target.objects.filter(campagne=selected_campagne, has_open=True).count()
        nb_tar_has_read = target.objects.filter(campagne=selected_campagne, has_read=True).count()
        nb_tar_has_logged = target.objects.filter(campagne=selected_campagne, has_logged=True).count()

        if int(nb_tar) != 0:
            pourcentage_1 = int((int(nb_tar_has_read) / int(nb_tar)) * 100)
        else:
            pourcentage_1 = 0
        if int(nb_tar_has_read) != 0:
            pourcentage_2 = int((int(nb_tar_has_open) / int(nb_tar_has_read)) * 100)
        else:
            pourcentage_2 = 0
        if int(nb_tar_has_open) != 0:
            pourcentage_3 = int((int(nb_tar_has_logged) / int(nb_tar_has_open)) * 100)
        else:
            pourcentage_3 = 0

        context = {
            'username': request.user.username,
            'email': request.user.email,
            'selected_campagne': selected_campagne,
            'form': form,
            'all_campagnes': campagne_fish.objects.filter(utilisateur=request.user),
            'nb_target': nb_tar,
            'nb_target_has_read': nb_tar_has_read,
            'nb_target_has_open': nb_tar_has_open,
            'nb_target_has_logged': nb_tar_has_logged,
            'pourcentage_1': pourcentage_1,
            'pourcentage_2': pourcentage_2,
            'pourcentage_3': pourcentage_3,
        }

        if request.user.username == selected_campagne.utilisateur.username:
            return render(request, 'pages/panel.html', context)
        else:
            return HttpResponse("Vous n'avez pas le droit de voir ceci.", status=403)
    else:
        return redirect(home)


def email(request):
    if request.user.is_authenticated:
        campagne_id = request.COOKIES.get('campagne_id', 'null')
        if campagne_id != "null":
            # TODO try catch pour gerer si id invalide
            selected_campagne = campagne_fish.objects.get(id=campagne_id)
        else:
            selected_campagne = campagne_fish.objects.filter(utilisateur=request.user).first()
            response = redirect("/panel/email")
            response.set_cookie('campagne_id', str(selected_campagne.id))
            return response

        if 'campagne' in request.GET:
            form_menu = CampagneUtilisateurForm(request.user, campagne_id, request.GET)
            if form_menu.is_valid():
                selected_campagne = form_menu.cleaned_data['campagne']
                response = redirect(email)
                response.set_cookie('campagne_id', str(selected_campagne.id))
                return response
        else:
            form_menu = CampagneUtilisateurForm(request.user, campagne_id)

        if request.method == 'POST':
            print("ok")
            form = EmailForm(request.POST)

            print("non ok")
            if form.is_valid():
                mailtype = form.cleaned_data['mailtype']
                mail = form.cleaned_data['mail']
                password = form.cleaned_data['password']
                name = form.cleaned_data['name']
                receiver = form.cleaned_data['receiver'].replace('\r', '').split('\n')
                subject = form.cleaned_data['subject']
                content = form.cleaned_data['content']

                server = TryConnection(mailtype, mail, password)
                if (server != None):
                    sended = EmailSender(server, str(selected_campagne.id), mailtype, name, receiver, subject, content)

                    for id in sended:
                        nouvelle_target = target.objects.create(
                            id_email_uuid=id,
                            campagne=selected_campagne,
                        )
                        nouvelle_target.save()
                return redirect(email)

            print("non valid")
        else:
            form = EmailForm()
        targets_for_campagne = target.objects.filter(campagne=selected_campagne)

        context = {
            'username': request.user.username,
            'email': request.user.email,
            'selected_campagne': selected_campagne,
            'targets_for_campagne': targets_for_campagne,
            'form': form,  # Ajoutez le formulaire au contexte
            'form_menu': form_menu,
        }

        if request.user.username == selected_campagne.utilisateur.username:
            return render(request, 'pages/email.html', context)
        else:
            return HttpResponse("Vous n'avez pas le droit de voir ceci.", status=403)
    else:
        return redirect(home)


def gestion_campagne(request):
    if request.user.is_authenticated:
        campagne_id = request.COOKIES.get('campagne_id', 'null')

        if campagne_id != "null":
            # TODO try catch pour gerer si id invalide
            selected_campagne = campagne_fish.objects.get(id=campagne_id)
        else:
            selected_campagne = campagne_fish.objects.filter(utilisateur=request.user).first()
            response = redirect("/panel/campagnes")
            response.set_cookie('campagne_id', str(selected_campagne.id))
            return response

        if 'campagne' in request.GET:
            form = CampagneUtilisateurForm(request.user, campagne_id, request.GET)
            if form.is_valid():
                selected_campagne = form.cleaned_data['campagne']
                response = redirect(gestion_campagne)
                response.set_cookie('campagne_id', str(selected_campagne.id))
                return response
        else:
            form = CampagneUtilisateurForm(request.user, campagne_id)

        context = {
            'username': request.user.username,
            'email': request.user.email,
            'selected_campagne': selected_campagne,
            'form': form,
        }
        if request.user.username == selected_campagne.utilisateur.username:
            return render(request, 'pages/gestion_campagne.html', context)
        else:
            return HttpResponse("Vous n'avez pas le droit de voir ceci.", status=403)
    else:
        return redirect(home)
