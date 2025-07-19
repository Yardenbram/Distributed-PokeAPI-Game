import requests
import boto3
import random
import json  # Optional: used for pretty-printing JSON if needed

# Set up DynamoDB connection details
DYNAMODB_TABLE_NAME = "PokemonCollection"  # Make sure this matches the table you created
REGION_NAME = "your-aws-region"  # For example: "eu-central-1" or "us-east-1"

# Initialize the DynamoDB resource using the IAM role attached to the EC2 instance
dynamodb = boto3.resource('dynamodb', region_name=REGION_NAME)
table = dynamodb.Table(DYNAMODB_TABLE_NAME)

POKEAPI_BASE_URL = "https://pokeapi.co/api/v2/"

def get_random_pokemon_name():
    """Pulls a random Pokémon name from the public PokeAPI."""
    try:
        response = requests.get(f"{POKEAPI_BASE_URL}pokemon?limit=10000")  # Fetches a wide list of Pokémon
        response.raise_for_status()
        data = response.json()
        pokemon_list = data['results']
        random_pokemon = random.choice(pokemon_list)
        return random_pokemon['name']
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch Pokémon list: {e}")
        return None

def get_pokemon_details(pokemon_name):
    """Fetch detailed information for a given Pokémon by name."""
    try:
        response = requests.get(f"{POKEAPI_BASE_URL}pokemon/{pokemon_name}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Unable to retrieve data for Pokémon '{pokemon_name}': {e}")
        return None

def save_pokemon_to_db(pokemon_data):
    """Store selected Pokémon data into the DynamoDB table."""
    try:
        item = {
            'pokemon_name': pokemon_data['name'],
            'id': pokemon_data['id'],
            'height': pokemon_data['height'],
            'weight': pokemon_data['weight'],
            'types': [t['type']['name'] for t in pokemon_data['types']],
            'abilities': [a['ability']['name'] for a in pokemon_data['abilities']],
            'base_experience': pokemon_data.get('base_experience'),
            'sprite_front_default': pokemon_data['sprites']['front_default'] if 'front_default' in pokemon_data['sprites'] else None
        }
        table.put_item(Item=item)
        print(f"Successfully saved '{pokemon_data['name']}' to the database.")
    except Exception as e:
        print(f"Error saving data to DynamoDB: {e}")

def get_pokemon_from_db(pokemon_name):
    """Look up a Pokémon in the DynamoDB table by name."""
    try:
        response = table.get_item(Key={'pokemon_name': pokemon_name})
        return response.get('Item')
    except Exception as e:
        print(f"Database lookup failed for Pokémon: {e}")
        return None

def display_pokemon_details(pokemon_details):
    """Output the Pokémon's information in a readable format."""
    if not pokemon_details:
        print("No details found for the selected Pokémon.")
        return

    print("\n--- Pokémon Profile ---")
    print(f"Name: {pokemon_details.get('pokemon_name', 'N/A').capitalize()}")
    print(f"ID: {pokemon_details.get('id', 'N/A')}")
    print(f"Height: {pokemon_details.get('height', 'N/A')}")
    print(f"Weight: {pokemon_details.get('weight', 'N/A')}")
    print(f"Types: {', '.join([t.capitalize() for t in pokemon_details.get('types', ['N/A'])])}")
    print(f"Abilities: {', '.join([a.capitalize() for a in pokemon_details.get('abilities', ['N/A'])])}")
    print(f"Base XP: {pokemon_details.get('base_experience', 'N/A')}")
    if pokemon_details.get('sprite_front_default'):
        print(f"Image URL: {pokemon_details['sprite_front_default']}")
    print("------------------------\n")

def main():
    while True:
        choice = input("Would you like to get a random Pokémon? (yes/no): ").lower()

        if choice == 'yes':
            pokemon_name = get_random_pokemon_name()
            if not pokemon_name:
                continue

            print(f"Pokémon selected: {pokemon_name.capitalize()}")

            # Check whether this Pokémon already exists in the database
            db_pokemon = get_pokemon_from_db(pokemon_name)

            if db_pokemon:
                print(f"'{pokemon_name.capitalize()}' is already stored in DynamoDB.")
                display_pokemon_details(db_pokemon)
            else:
                print(f"'{pokemon_name.capitalize()}' not found in DB. Fetching and saving details...")
                api_pokemon_details = get_pokemon_details(pokemon_name)
                if api_pokemon_details:
                    save_pokemon_to_db(api_pokemon_details)
                    display_pokemon_details(api_pokemon_details)

        elif choice == 'no':
            print("See you next time! Hope you enjoyed your Pokémon journey.")
            break
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")

if __name__ == "__main__":
    main()
