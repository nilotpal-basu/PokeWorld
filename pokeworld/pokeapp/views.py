from django.shortcuts import render, redirect
from .models import Trainer,Pokemon,PokemonCaught
from django.contrib import messages
import random
from django.core.files.storage import FileSystemStorage
import requests
import os

def classify_image_with_api(image_path):
    with open(image_path, 'rb') as f:
        response = requests.post('http://localhost:5000/predict', files={'image': f})
    return response.json()['class_id']

def index(request):
    if not request.session.get('trainer_logged_in'):
        return redirect('/login')
    
    username = request.session.get('trainer_username')
    trainer = Trainer.objects.get(username=username)
    profile_pic = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{trainer.img_number}.png"

    return render(request, 'index.html', {'user': trainer,'pp': profile_pic})

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        try:
            user = Trainer.objects.get(username=username)
            if user.password == password:
                request.session['trainer_logged_in'] = True 
                request.session['trainer_username'] = username
                return redirect('/')
            else:
                error_message = "Incorrect password"
                return render(request, 'login.html', {'error_message':error_message})
        except:
            error_message = "User does not exist"
            return render(request, 'login.html', {'error_message':error_message})
    return render(request, 'login.html')

def user_signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        repeatPassword = request.POST['repeatPassword']

        if Trainer.objects.filter(username=username).exists():
            error_message = "Username is already taken"
            return render(request, 'signup.html', {'error_message':error_message})

        if password == repeatPassword :
            try:
                user = Trainer.objects.create(
                    username = username,
                    email = email,
                    password = password,
                    img_number = random.randrange(0,1025))
                user.save()
                request.session['trainer_logged_in'] = True 
                request.session['trainer_username'] = username
                return redirect('/')
            except:
                error_message = "Error creating user"
                return render(request, 'signup.html', {'error_message':error_message})

        else :
            error_message = "Passwords don't match"
            return render(request, 'signup.html', {'error_message':error_message})
    return render(request, 'signup.html')

def user_logout(request):
    request.session.flush()
    return redirect('/login')

def leaderboard_view(request):
    if not request.session.get('trainer_logged_in'):
        return redirect('/login')

    username = request.session.get('trainer_username')
    trainer = Trainer.objects.get(username=username)

    if request.method == 'POST':
        new_tier = request.POST.get('trainer_tier')
        trainer.trainer_tier = new_tier
        trainer.save()
        return redirect('/leaderboard')
    
    selected_tier = request.GET.get('tier', 'All')

    if selected_tier == 'All':
        trainers = Trainer.objects.all().order_by('-poke_caught')[:5]
    else:
        trainers = Trainer.objects.filter(trainer_tier=selected_tier).order_by('-poke_caught')[:5]

    pokemons = Pokemon.objects.all().order_by('-num_caught')[:5]

    return render(request, 'leaderboard.html', {'trainers': trainers, "user":trainer, "pokemons":pokemons})

def catch_pokemon(request):
    if not request.session.get('trainer_logged_in'):
        return redirect('/login')

    username = request.session.get('trainer_username')
    trainer = Trainer.objects.get(username=username)

    # Choose a random Pokémon
    total_pokemon = Pokemon.objects.count()
    if total_pokemon == 0:
        return render(request, 'catch_game.html', {'error': 'No Pokémon in the database.'})

    random_pokemon = Pokemon.objects.get(label=random.randint(0,999))
    poke_name = random_pokemon.name.lower()

    # Get image from PokéAPI
    poke_url = f'https://pokeapi.co/api/v2/pokemon/{poke_name}'
    response = requests.get(poke_url)
    image_url = ''
    if response.status_code == 200:
        data = response.json()
        image_url = data['sprites']['other']['official-artwork']['front_default']

    # Save info in session
    request.session['catch_pokemon_label'] = random_pokemon.label
    request.session['guess_attempts'] = 0

    return render(request, 'catch_game.html', {
        'silhouette_url': image_url,
        'trainer': trainer
    })

def submit_guess(request):
    if request.method == 'POST':
        username = request.session.get('trainer_username')
        pokemon_label = request.session.get('catch_pokemon_label')
        guess = request.POST.get('guess', '').strip().lower()

        if not username or not pokemon_label:
            return redirect('/catch/')  # Something went wrong, reset

        try:
            trainer = Trainer.objects.get(username=username)
            pokemon = Pokemon.objects.get(label=pokemon_label)
        except (Trainer.DoesNotExist, Pokemon.DoesNotExist):
            return redirect('/catch/')

        # Track guess attempts in session
        attempts = request.session.get('guess_attempts', 0) + 1
        request.session['guess_attempts'] = attempts

        # Get Pokémon data from PokéAPI for rendering
        api_url = f"https://pokeapi.co/api/v2/pokemon/{pokemon.name.lower()}"
        response = requests.get(api_url)
        silhouette_url = ''
        cry_url = ''
        if response.status_code == 200:
            data = response.json()
            silhouette_url = data['sprites']['other']['official-artwork']['front_default']
            cry_url = data.get('cries', {}).get('latest', '')

        if guess == pokemon.name.lower():
            # Only update caught if not already caught
            if not PokemonCaught.objects.filter(trainer=trainer, pokemon=pokemon).exists():
                PokemonCaught.objects.create(trainer=trainer, pokemon=pokemon)
                trainer.poke_caught += 1
                pokemon.num_caught += 1
                if(trainer.poke_caught==100): trainer.trainer_tier = "Elite"
                elif(trainer.poke_caught==300): trainer.trainer_tier = "Master"
                trainer.save()
                pokemon.save()

            # Reset for new catch
            request.session['guess_attempts'] = 0
            request.session['catch_pokemon_label'] = None

            return render(request, 'catch_success.html', {
                'name': pokemon.name.capitalize(),
                'image_url': silhouette_url,
                'cry_url': cry_url,
                'caught': True
            })

        elif attempts >= 2:
            # Reset and show failure
            request.session['guess_attempts'] = 0
            request.session['catch_pokemon_label'] = None

            return render(request, 'catch_success.html', {
                'name': pokemon.name.capitalize(),
                'image_url': silhouette_url,
                'cry_url': cry_url,
                'caught': False
            })

        else:
            # Render same guessing page with one more chance
            messages.warning(request, "Wrong guess! You have one more try.")
            return render(request, 'catch_game.html', {
                'silhouette_url': silhouette_url,
                'guess_attempts': attempts
            })

    return redirect('/catch/')

def pokedex_upload(request):
    if not request.session.get('trainer_logged_in'):
        return redirect('/login')

    if request.method == 'POST' and request.FILES.get('pokemon_image'):
        image = request.FILES['pokemon_image']
        fs = FileSystemStorage(location='media/pokemon_images')
        filename = fs.save(image.name, image)
        full_image_path = os.path.abspath(os.path.join(fs.location, filename))

        predicted_label = classify_image_with_api(full_image_path)
        predicted_name = Pokemon.objects.get(label=predicted_label).name

        return redirect(f'/pokedex/{predicted_name.lower()}/')

    return render(request, 'pokedex_upload.html')

def classify_pokemon(request, pokemon_name):
    if not request.session.get('trainer_logged_in'):
        return redirect('/login')

    try:
        pokemon = Pokemon.objects.get(name__iexact=pokemon_name)
    except Pokemon.DoesNotExist:
        return render(request, 'pokedex_upload.html', {
            'error': 'Pokémon not found in database.'
        })

    # Get info from PokéAPI
    api_url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower()}"
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        description_resp = requests.get(data['species']['url']).json()
        flavor_entries = [
            entry['flavor_text'].replace('\n', ' ').replace('\f', ' ')
            for entry in description_resp['flavor_text_entries']
            if entry['language']['name'] == 'en'
        ]
        description = " ".join(flavor_entries[:2]) if flavor_entries else "No description available."
        abilities = [a['ability']['name'] for a in data['abilities']]
        types = [t['type']['name'] for t in data['types']]
        moves = [m['move']['name'] for m in data['moves'][:9]]
        image_url = data['sprites']['other']['official-artwork']['front_default']
        cry_url = data['cries']['latest'] if 'cries' in data and 'latest' in data['cries'] else ''

        return render(request, 'pokedex_result.html', {
            'image_url': image_url,
            'name': pokemon.name.capitalize(),
            'description': description,
            'moves': moves,
            'cry_url': cry_url,
            'types': types,
            'abilities': abilities,
        })

    return render(request, 'pokedex_upload.html', {
        'error': 'Failed to fetch data from PokéAPI.'
    })

def trainer_profile(request):
    username = request.session.get('trainer_username')
    trainer = Trainer.objects.get(username=username)

    # Get recent caught Pokémon (latest 6, changeable)
    caught_entries = PokemonCaught.objects.filter(trainer=trainer).order_by('-caught_at')[:6]

    # Optional search result
    search_query = request.GET.get('search', '').strip().lower()
    searched_pokemon = None
    has_caught = None

    if search_query:
        try:
            searched_pokemon = Pokemon.objects.get(name__iexact=search_query)
            has_caught = PokemonCaught.objects.filter(trainer=trainer, pokemon=searched_pokemon).exists()
        except Pokemon.DoesNotExist:
            searched_pokemon = None
            has_caught = False

    return render(request, 'trainer_profile.html', {
        'trainer': trainer,
        'recent_catches': caught_entries,
        'search_query': search_query,
        'searched_pokemon': searched_pokemon,
        'has_caught': has_caught,
    })
