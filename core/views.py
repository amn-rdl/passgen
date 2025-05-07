import random, string, json
from cryptography.fernet import Fernet as fer

from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required


from .models import User

DATA_PATH = "core/static/data/mdp.json"
CRYPTO_PATH = "core/static/data/fernet_key.txt"

def gen_key():
    with open(CRYPTO_PATH, "rb") as f:
        key = f.read().strip()
    fernet = fer(key)  
    return fernet
fernet = gen_key()


def pass_create(level):
    letters = string.ascii_letters
    spe = string.punctuation
    if level == 1:
        nb = 8
        pwd = "".join(random.choices(letters, k=nb-(nb*60//100))) + "".join(random.choices(spe, k=nb-(nb*40//100)))
        pwd = "".join(random.sample(pwd, k=nb)).encode()
        pwd = fernet.encrypt(pwd)
    elif level == 2:
        nb = 12
        pwd = "".join(random.choices(letters, k=nb-(nb*40//100))) + "".join(random.choices(spe, k=nb-(nb*60//100)))
        pwd = "".join(random.sample(pwd, k=nb)).encode()
        pwd = fernet.encrypt(pwd)
    return pwd.decode()

def pass_decode(pwd):
    pwd = fernet.decrypt(pwd).decode()
    return pwd
        
def index(request):
    user = request.user

    if request.method == 'POST':
        data = load_data()
        action = request.POST.get('action')

        if action == "save":
            password = request.POST.get('code')
            site = request.POST.get('url_site')
            usrnm_site = request.POST.get('usrnm_site').lower().replace(" ", ".")
            save_mdp(user, password, data, usrnm_site, site)
            passdecode = pass_decode(password)
        else:
            level = request.POST.get('level')
            if not str(level).isdigit():
                level = 2 
            else:
                level = int(level)
            password = pass_create(level)
            passdecode = pass_decode(password)

        return render(request, "index.html", {
            'action': action,
            'code': password,
            'decode': passdecode,
            'user': user,
        })

    return render(request, "index.html")

def save_mdp(user, password, data, username, site):
    userr= user.username
    if userr in data.keys():
        data[userr].append({
            site : {
                username: password
            }
        })
    else:
        data[userr] = [{
            site : {
                username : password
            }
        }]
    
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=3)

def delete_mdp(user, data, username, site):
    userr = user.username
    if userr in data:
        for bloc in data[userr]:
            if site in bloc and username in bloc[site]:
                data[userr].remove(bloc)
                break
        with open(DATA_PATH, "w") as f:
            json.dump(data, f, indent=3)

def edit_mdp(request, site, username):
    user = request.user
    data = load_data()
    userr = user.username
    
    bloc_to_edit = None
    for bloc in data.get(userr, []):
        if site in bloc and username in bloc[site]:
            bloc_to_edit = bloc
            break
    
    if request.method == "POST":
        new_site = request.POST.get("new_site") or site
        new_username = request.POST.get("new_username") or username
        new_password = request.POST.get("new_password")
        if not (new_site and new_username and new_password):
            return render(request, "change_mdp.html", {
                "user": user,
                "site": site,
                "username": username,
            })
        new_password_encrypted = fernet.encrypt(new_password.encode()).decode()
        data[userr].remove(bloc_to_edit)
        data[userr].append({
            new_site: {
                new_username: new_password_encrypted
            }
        })
        with open(DATA_PATH, "w") as f:
            json.dump(data, f, indent=3)
            
        return redirect("mypass")

    old_password = pass_decode(bloc_to_edit[site][username])
    return render(request, "change_mdp.html", {
        "user": user,
        "site": site,
        "username": username,
        "password": old_password,
    })
    
def load_data():
    with open(DATA_PATH, "r") as f:
            content = f.read()
            if content: 
                data = json.loads(content) 
            else:
                data = {}
    return data

def mdp_load(user):
    with open(DATA_PATH, "r") as f:
            content = f.read()
            data = json.loads(content) 

    liste_mdp = []
    liste_username = []
    liste_site = []
    userr = user.username
    if userr in data:
        for bloc in data[userr]:
            for site, pair in bloc.items():
                for username, password in pair.items():
                    liste_site.append(site)
                    liste_username.append(username)
                    liste_mdp.append(pass_decode(password))

    return liste_mdp, liste_username, liste_site

def mypass(request):
    user = request.user
    data = load_data()
    mdps, usernames, sites = mdp_load(user)
    tuple_mdp = zip(mdps, usernames, sites)
    action = request.POST.get('action')
    result = []
    found_site = False
    found_usrnm = False
    if request.method == 'POST':
        query = str(request.POST.get('q_cont')).lower().replace(" ","").replace("@", "")
        for i in range(len(usernames)):
            usrnm = usernames[i].lower().replace(" ","")
            if query == usrnm:
                found_usrnm = True
                searched = (usernames[i], sites[i], mdps[i])
                result.append(searched)
        for i in range(len(sites)):
            site = sites[i].lower().replace(" ","")
            if query == site:
                found_site = True
                searched = (usernames[i], sites[i], mdps[i])
                result.append(searched)
        
        if action == "delete":
            usrnm_del = request.POST.get("usrnm_del")
            site_del = request.POST.get("site_del")
            delete_mdp(user, data, usrnm_del, site_del)
            return redirect("mypass")
        
        elif action == "edit":
            usrnm_edit = request.POST.get("usrnm_edit")
            site_edit = request.POST.get("site_edit")
            return redirect('edit_mdp', site=site_edit, username=usrnm_edit)
        
    return render(request, "mypass.html", {
        'user': user,
        'tuple':tuple_mdp,
        'action': action,
        'searched':result,
        'search':result if found_usrnm or found_site else '',
        'found_usrnm':found_usrnm,
        'found_site':found_site,
    })

@login_required
def myaccount(request): 
    user = request.user
    return render(request, "myaccount.html", {"user": user})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        mdp = request.POST.get('mdp')

        user = authenticate(request, username=username, password=mdp)

        if user is not None:
            login(request, user) 
            return redirect('home') 
        else:
            return HttpResponse("Nom d'utilisateur ou mot de passe incorrect", status=401)
        
    return render(request, 'login.html')

def signin_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        firstname = request.POST.get('firstname')
        pp = request.FILES.get("pp")
        name = request.POST.get('name')
        email = request.POST.get('mail')
        mdp1 = request.POST.get('mdp1')
        mdp2 = request.POST.get('mdp2')
        if mdp1 == mdp2:
            user = User(
            username=username,
            email=email,
            last_name=name,
            first_name=firstname,
            pp=pp)
            user.set_password(mdp1)
            user.save()
            login(request, user)
            return redirect('home') 
        else:
            return HttpResponse("Mot de Passe differents", status=401)

    return render(request, "signin.html")

def logout_view(request):
    logout(request)
    return redirect('login') 

def change_info(request):
    user = request.user
    if request.method == "POST":
        lastname = request.POST.get("name")
        if lastname:
            user.last_name = lastname
           
        username = request.POST.get("username")
        if username:
            user.username = username

        firstname = request.POST.get("firstname")
        if firstname:
            user.first_name = firstname

        email = request.POST.get("email")
        if email:
            user.email = email
        pp = request.FILES.get("pp")
        if pp:
            user.pp = pp

        pwd = request.POST.get("pwd")
        print("Nouveau mot de passe reçu :", pwd)
        if pwd:
            user.set_password(pwd)

        user.save()
        return redirect("account")
    return render(request, "change_info.html", {"user": user})

def search(request):
    if request.method == 'POST':
        query = request.POST.get('q')
        pages = {
            'home': ['accueil', 'maisson', 'home', 'princiaple', 'debut', 'accuiel', 'acceuil', 'passgen'],
            'about': ['apropos', 'a propo', 'a propos', 'info', 'qui sommes nous', 'notre equipe', 'notresquipe'],
            'tips': ['conseil', 'conseils','astuce', 'trucs', 'aide', 'tip', 'tips','conseilles', 'trucs'],
            'account': ['compte', 'profil', 'moncompte', 'utilisateur', 'monprofi', 'moncopte', 'compteutilisateur'],
            'mypass': ['mdp', 'motdepasse', 'password', 'generermdp', 'generermotdepasse', 'pass'],
        }
            
        found_page = False

        for url, page_names in pages.items():
            for page in page_names:
                if query.lower() == page.lower():
                    found_page = True
                    return redirect(url)

        if not found_page:
            return redirect('noresult')
    
    return redirect("home")
    
def no_result(request):
    return render(request, "no_result.html")

def about(request):
    return render(request, "about.html")

def tips(request):
    return render(request, "tips.html")
