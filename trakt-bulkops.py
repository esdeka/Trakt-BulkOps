from datetime import datetime
import os
import json
import requests

# File to store the credentials
CREDENTIALS_FILE = 'trakt_credentials.json'

# Functions
# credentials
def save_credentials(client_id, client_secret, username):
    """Save credentials to a JSON file."""
    credentials = {
        'client_id': client_id,
        'client_secret': client_secret,
        'username': username
    }
    with open(CREDENTIALS_FILE, 'w') as f:
        json.dump(credentials, f)
    print(f"Credentials saved to {CREDENTIALS_FILE}. You can delete or edit this file if needed.\n")

def load_credentials():
    """Load credentials from the JSON file if it exists."""
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, 'r') as f:
            return json.load(f)
    return None

def get_credentials():
    """Prompt user for credentials if not saved, otherwise load them."""
    credentials = load_credentials()

    if credentials:
        print(f"Loaded credentials from {CREDENTIALS_FILE}")
        return credentials['client_id'], credentials['client_secret'], credentials['username']
    else:
        # Ask user for credentials and save them
        client_id = input('Enter your Trakt client ID: ')
        client_secret = input('Enter your Trakt client secret: ')
        username = input('Enter your Trakt username: ')

        # Save the credentials
        save_credentials(client_id, client_secret, username)
        return client_id, client_secret, username

# fetch
def login_to_trakt():
    print('Authentication')
    print('Open the link in a browser and paste the pin')
    print('https://trakt.tv/oauth/authorize?response_type=code&client_id=%s&redirect_uri=urn:ietf:wg:oauth:2.0:oob' % client_id)
    print('')

    pin = str(input('Pin: '))

    session.headers.update({
        'Accept': 'application/json',
        'User-Agent': 'Betaseries to Trakt',
        'Connection': 'Keep-Alive'
    })

    post_data = {
        'code': pin,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob',
        'grant_type': 'authorization_code'
    }

    request = session.post(auth_get_token_url, data=post_data)
    response = request.json()

    print(response)
    print()

    session.headers.update({
        'Content-Type': 'application/json',
        'trakt-api-version': '2',
        'trakt-api-key': client_id,
        'Authorization': 'Bearer ' + response["access_token"]
    })

def get_history(type):
    results = []

    url_params = {
        'page': 1,
        'limit': 1000,
        'type': type
    }

    print('\nRetrieving history for %s' % type)

    while True:
        print(get_history_url.format(**url_params))
        resp = session.get(get_history_url.format(**url_params))

        if resp.status_code != 200:
            print(resp)
            continue

        results += resp.json()

        if int(resp.headers['X-Pagination-Page-Count']) != url_params['page']:
            url_params['page'] += 1
        else:
            break

    print('Done retrieving %s history' % type)
    return results


# act
def remove_duplicate(history, type):
    print('Removing %s duplicates' % type)

    entry_type = 'movie' if type == 'movies' else 'episode'

    entries = {}
    duplicates = []
    duplicates_json = []

    for i in history[::-1]:
        if i[entry_type]['ids']['trakt'] in entries:
            if not keep_per_day or i['watched_at'].split('T')[0] == entries.get(i[entry_type]['ids']['trakt']):
                duplicates.append(i['id'])
                duplicates_json.append(i)
        else:
            entries[i[entry_type]['ids']['trakt']] = i['watched_at'].split('T')[0]

    if len(duplicates) > 0:
        print('%s %s duplicates plays to be removed from %s/%s (%s/plays)' % (len(duplicates), type, len(entries), len(history), type))

        duplicates_log = f'{type}-duplicates-{datetime.now().strftime("%m%d%Y%H%M%S")}.json'
        with open(duplicates_log, 'w') as output:
                json.dump(duplicates_json, output, indent=4)
                print(f'To be removed duplicates saved in file {duplicates_log}')

        removeyn = input("Do you want to remove %s of %s? (y/n): "% (len(duplicates), type)).strip().lower() == 'y'
        if removeyn:
            session.post(sync_history_url, json={'ids': duplicates})
            print('%s %s duplicates removed!' % (len(duplicates), type))
    else:
        print('No %s duplicates found' % type)


def remove_plays_from_specific_date(history, type, date_to_remove):
    print()
    print('Searching for %s plays from %s' % (type, date_to_remove))

    entry_type = 'movie' if type == 'movies' else 'episode'
    plays_to_remove = []

    # Filter entries by date
    for i in history:
        watched_at = i['watched_at'].split('T')[0]
        if watched_at == date_to_remove:
            plays_to_remove.append(i)

    if len(plays_to_remove) > 0:
        while True:
            # Print the plays found to be removed with index
            print('%s %s plays found:' % (len(plays_to_remove), type))
            for idx, play in enumerate(plays_to_remove):
                watched_at = play['watched_at']
                play_id = play['id']

                if type == 'movies':
                    # Handle movie-specific details
                    movie_title = play['movie']['title']
                    release_year = play['movie'].get('year', 'Unknown Year')
                    # Print movie format
                    print(f"[{idx}] {watched_at} - {movie_title} ({release_year})")
                else:
                    # Handle episode-specific details
                    show_name = play['show']['title'] if 'show' in play else ''
                    season = play[entry_type]['season']
                    episode = play[entry_type]['number']
                    episode_title = play[entry_type]['title']
                    # Print episode format
                    print(f"[{idx}]\t{watched_at} - {show_name} - S{str(season).zfill(2)}E{str(episode).zfill(2)} - {episode_title}")

            # Ask for confirmation or specify which plays to keep
            print()
            print(" - Enter 'y' to remove all plays listed above from your history")
            print(" - Enter 'n' to cancel and exit")
            print(" - Enter '0 3 12' (example indexes) to specify what plays you want to keep, and print the list again to check it.")
            confirm = input("Choose an option: ").lower()

            if confirm == 'y':
                play_ids = [play['id'] for play in plays_to_remove]
                session.post(sync_history_url, json={'ids': play_ids})
                print('%s %s plays successfully removed!' % (len(play_ids), type))
                break
            elif confirm == 'n':
                print('Removal canceled.')
                break
            else:
                try:
                    # Parse the indexes the user wants to skip
                    skip_indexes = list(map(int, confirm.split()))
                    # Filter out the specified indexes from plays_to_remove
                    plays_to_remove = [play for idx, play in enumerate(plays_to_remove) if idx not in skip_indexes]

                    if len(plays_to_remove) == 0:
                        print('No plays left to remove. Exiting.')
                        break

                except ValueError:
                    print("Invalid input. Please enter 'y', 'n', or a list of indexes (e.g., '0 3 12').")
    else:
        print('No %s plays found from %s' % (type, date_to_remove))


if __name__ == '__main__':
    # Get or load credentials
    client_id, client_secret, username = get_credentials()

    # Don't edit the informations below
    trakt_api = 'https://api.trakt.tv'
    auth_get_token_url = '%s/oauth/token' % trakt_api
    get_history_url = '%s/users/%s/history/{type}?page={page}&limit={limit}' % (trakt_api, username)
    sync_history_url = '%s/sync/history/remove' % trakt_api
    session = requests.Session()

    login_to_trakt()

    # Ask for purpose
    print("\nSelect an operation:")
    print("[1] Bulk remove duplicate plays at any date")
    print("[2] Bulk remove plays from a specified date")
    operation = input("Enter the number of the operation (1 or 2): ").strip()

    # Ask for target
    print("\nDo you want to affect:")
    print("[1] Movies only")
    print("[2] Episodes only")
    print("[3] Both movies and episodes")
    content_type_choice = input("Enter your choice (1, 2, or 3): ").strip()

    # Set types based on user's selection
    if content_type_choice == '1':
        types = ['movies']
    elif content_type_choice == '2':
        types = ['episodes']
    elif content_type_choice == '3':
        types = ['movies', 'episodes']
    else:
        print("Invalid choice. Please enter '1', '2', or '3'.")
        exit()


    # Do
    if operation == '1':
        # Remove duplicates operation
        print("\nYou have selected: Remove duplicate plays")
        keep_per_day = input("Do you want to keep one entry per day? (y/n): ").strip().lower() == 'y'
        print("\nRemoving duplicates...\n")

        # Loop through types (movies, episodes)
        for type in types:
            print(" ***** MOVIES *****" if type == 'movies' else " ***** EPISODES *****")
            history = get_history(type)
            with open(f'{type}.json', 'w') as output:
                json.dump(history, output, indent=4)
                print(f'History saved in file {type}.json')

            remove_duplicate(history, type)

    elif operation == '2':
        # Bulk remove by specific date
        print("\nYou have selected: Bulk remove plays from a specific date")
        specific_date = input("Enter the date to remove plays from (YYYY-MM-DD): ").strip()
        print(f"\nRemoving plays from {specific_date}...\n")

        # Loop through types (movies, episodes)
        for type in types:
            print(" ***** MOVIES *****" if type == 'movies' else " ***** EPISODES *****")
            history = get_history(type)
            with open(f'{type}.json', 'w') as output:
                json.dump(history, output, indent=4)
                print(f'History saved in file {type}.json')

            # Remove plays from the specified date
            remove_plays_from_specific_date(history, type, specific_date)
    else:
        print("Invalid option. Please enter '1' or '2'.")
