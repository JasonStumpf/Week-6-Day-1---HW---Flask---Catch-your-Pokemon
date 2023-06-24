from app import app
from .models import Pokemon, User
from flask import render_template, request, redirect, flash
from flask_login import current_user
import requests

@app.route('/')
def home():
    return render_template('index.html')

pokemon_data_dict = {}

@app.route('/pokemon/', methods=['POST'])
def pokemon():
    pokemon_name = request.form['pokemon_name']
    if pokemon_name in pokemon_data_dict:
        pokemon_data = pokemon_data_dict[pokemon_name]
        flash(f'Wild {pokemon_name.title()} appeared!', 'success')
    else:
        pokemon_data = get_data(pokemon_name)
        pokemon_data_dict[pokemon_name] = pokemon_data
        flash(f'New Pokemon Discovered: {pokemon_name.title()}!', 'success')
    return render_template('pokemon.html', data=pokemon_data, pokemon_dict=pokemon_data_dict)

def get_data(pokemon_name):
    response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower()}")
    if response.ok:
        pokemon = response.json()
        poke_info = {
            'Name' : pokemon['name'].title(),
            'Ability' : pokemon['abilities'][0]['ability']['name'].title(),
            'Sprite' : pokemon['sprites']['front_default'],
            'HP-Base Stat' : pokemon['stats'][0]['base_stat'],
            'Attack-Base-Stat' : pokemon['stats'][1]['base_stat'],
            'Defense-Base-Stat' : pokemon['stats'][2]['base_stat']
        }
        new_pokemon = Pokemon(
            name=poke_info['Name'],
            ability=poke_info['Ability'],
            sprite=poke_info['Sprite'],
            hp=poke_info['HP-Base Stat'],
            attack=poke_info['Attack-Base-Stat'],
            defense=poke_info['Defense-Base-Stat']
            )
        new_pokemon.save_poke()
        return new_pokemon

@app.route('/catch/<int:pokemon_id>', methods=['GET', 'POST'])
def catch(pokemon_id):
    poke_name = Pokemon.query.get(pokemon_id)
    if poke_name not in current_user.catching:
        current_user.catch(poke_name)
        poke_name.caught_by = current_user.id
    return redirect('/team/')

@app.route('/release/<int:pokemon_id>', methods=['GET', 'POST'])
def release(pokemon_id):
    pokemon = Pokemon.query.get(pokemon_id)
    current_user.release(pokemon)
    return redirect('/team/')

@app.route('/team/')
def team():
    pokemon_list = current_user.catching.limit(6).all()
    return render_template('team.html', p_list=pokemon_list)
