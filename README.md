Trakt BulkOps: bulk remove plays
===========  
This Python script allows users to easily interact with the [Trakt API](https://trakt.tv/b/api-docs) to perform bulk operations on their watch history (movies and episodes).

### Operations implemented
Currently, the operations implemented involve removing plays.
 - Remove duplicate plays:
   - Keep the oldest one
   - Keep one entry per day (remove duplicates within the same day)
 - Remove all plays from a specific date
   - Optionally keep some of them


### Features
- Asks the user at startup all the required data, options, and guides throughout the process, no need to edit the script
- Store Trakt credentials in a dedicated json file
- Prints plays to be removed before applying any changes and asks for confirmation
- Allows the user to optionally choose which plays to keep from the list



### Examples

For instance if you have the following plays in your account:

```
[0] - 2024-10-02T14:26:50.000Z - JoJo's Bizarre Adventure - S01E24
[1] - 2024-10-02T14:26:50.000Z - JoJo's Bizarre Adventure - S01E25
[2] - 2024-10-02T10:31:01.000Z - JoJo's Bizarre Adventure - S01E26
[3] - 2024-10-02T10:35:26.000Z - JoJo's Bizarre Adventure - S02E01
[4] - 2024-10-14T10:26:38.000Z - JoJo's Bizarre Adventure - S02E01
[5] - 2024-10-14T10:26:39.000Z - JoJo's Bizarre Adventure - S02E01
```

- If running the script to remove duplicates will remove the plays [4] and [5] since they are newer duplicates of [3], the oldest one.
- If removing duplicates with the option of keeping one per day, the script will only remove the play [5] since it is a duplicate of [4] for the same day.
- If running the script to remove all plays for the date `2024-10-02`, plays [0],[1],[2],[3] will be removed. In this case, the user is asked the following:
```
Enter 'y' to remove all, 'n' to cancel, or specify indexes to skip (e.g., '0 3 12'): 
```
Therefore, the user can enter e.g. `3 4` to keep entries [3] and [4] in the account. The _to-remove_ list will be printed again, listing [0],[1],[2],[5], and the user can confirm deletion of the remaining entries.

Based on the operation chosen, if there are no duplicates or there are no entries for the specified date, the script will do nothing.

In any case, the script backups your history in local json files (movies.json and episodes.json) before doing anything.
  
## Getting Started  
### Requirements
You will need python3 and pip installed and in your path.
Then install requirements by running the following at the root of the project:
```
pip3 install -r requirements.txt
```

Alternatively, if you are on NixOS or have the Nix package manager, you can simply enter the development shell with python and the required packages by running:
```
nix-shell shell.nix
```


### Trakt.tv  
  
Go [register a new Trakt.tv API app](https://trakt.tv/oauth/applications/new). And fill the form with this information (other fields are optional):  
  
```  
Name: trakt-bulkops
Redirect uri: urn:ietf:wg:oauth:2.0:oob  
```
  
Next, go to [your API applications](https://trakt.tv/oauth/applications) and click on the one named `trakt-bulkops`.
  You will need the `Client ID` and the `Client Secret` from that page.  

### The script  
Finally, run the script:
```  
python3 trakt-bulkops.py  
```
At the first run, it will ask for your `client_id` and `client_secret` that you obtained on your trakt.tv API application page, and the `username` variable with your Trakt.tv username (you can find it in your settings: https://trakt.tv/settings). These credentials will be stored in the `trakt_credentials.json` file, which can be edited or removed to reset the authentication.

The script will guide you with the next steps. Depending on your selection, follow the prompts to either delete duplicates or bulk remove plays by date. It asks if you want to apply it to either movies, episodes, or both, etc, and provides feedback on the operation performed.

## Credits 

Based on https://github.com/TheFacc/Trakt-BulkOps which is based on https://github.com/anthony-foulfoin/trakt-tv-duplicates-removal which is based on https://gist.github.com/blaulan/50d462696bce5da9225b8d596a8c6fb4
