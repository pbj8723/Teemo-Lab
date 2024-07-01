import os
import requests
import time
import requests
import datetime

import pandas as pd
import numpy as np
from loguru import logger

from dotenv import load_dotenv

load_dotenv()
divisions = ['I', 'II', 'III', 'IV']
tiers = ["PLATINUM", "GOLD"]
discord_webhook = "https://discord.com/api/webhooks/1255501685657178124/7IOCZ9Ve3kl4YRdYYWZm8LeMVUTR8GXyimHQNjw8dvlSJHTO01WA43AG78F6vPe5MpPy"

def discord_send_message(text):
    now = datetime.datetime.now()
    message = {"content": f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] {str(text)}"}
    requests.post(discord_webhook, data=message)
    print(message)
    



def get_puuid(summoner_id):
    url = f"https://kr.api.riotgames.com/lol/summoner/v4/summoners/{summoner_id}?api_key=RGAPI-3d9657af-91f0-4112-9cd3-c9079a296834"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()['puuid']

def get_match_id(puuid):
    url = f"https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=20&api_key=RGAPI-3d9657af-91f0-4112-9cd3-c9079a296834"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def get_match_info(match_id):
    url = f"https://asia.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key=RGAPI-3d9657af-91f0-4112-9cd3-c9079a296834"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def transform_match_info(match_info, save_dirs):
    for match in [match_info]:
        match_id = match['metadata']['matchId']
        game_info = {}
        participants=match['metadata']['participants']
        for key in match['info']:
            if key.startswith('game'):
                game_info[key] = match['info'][key]
        p_dfs = []
        for i, participant in enumerate(match['info']['participants']):
            p = pd.DataFrame.from_dict(participant, orient='index')
            p_dfs.append(p)
        concated = pd.concat(p_dfs, axis=1).T
        concated.attrs['match_id'] = match_id
        concated.attrs['game_info'] = game_info
        concated.to_csv(f"{save_dirs[0]}/{match_id}.csv")


def retry_until_success(func, max_retries=1000, *args, **kwargs):
    """
    Repeatedly calls a function until it successfully returns a valid response or max_retries is reached.

    :param func: The function to be called.
    :param max_retries: Maximum number of retries before giving up.
    :param delay: Delay in seconds between retries.
    :param args: Positional arguments for the function.
    :param kwargs: Keyword arguments for the function.
    :return: The response from the function if successful, else None.
    """
    attempt = 0
    delay=5
    while attempt < max_retries:
        try:
            response = func(*args, **kwargs)
            # Assuming a valid response is non-None and not an exception
            if response is not None:
                return response
            else:
                print(f"Attempt {attempt + 1}: Function returned None. Retrying...")
        except Exception as e:
            print(f"Attempt {attempt + 1}: Function raised an exception:. Retrying...")

        attempt += 1
        time.sleep(delay)
        delay += 10
        if delay > 150:
            delay = 150
    
    print("Maximum retries reached. Function did not return a successful response.")
    return None


if __name__ == '__main__':
    from pathlib import Path
    summoner_id_dir = Path("exports/summoner_ids/")

    for tier in tiers:
        for division in divisions:
            discord_send_message(f"Processing {tier} {division}")
            save_dirs = [f"exports/match_infos/{tier}_{division}", f"exports/match_challenges/{tier}_{division}"]
            os.makedirs(save_dirs[0], exist_ok=True)
            os.makedirs(save_dirs[1], exist_ok=True)
            with open(summoner_id_dir / f"{tier}_{division}_summoner_ids.txt", 'r') as f:
                data = f.read() 
                summoner_ids = data.split("\n")
                
                discord_send_message(f"Processing {len(summoner_ids)} summoner ids")
                for summoner_id in summoner_ids:
                    puuid = retry_until_success(get_puuid, 1000, summoner_id)
                    specific_match_ids = retry_until_success(get_match_id, 1000, puuid)
                
                    for match_id in specific_match_ids:
                        match_info = retry_until_success(get_match_info, 1000, match_id)
                        transform_match_info(match_info, save_dirs)

            discord_send_message(f"Done processing {tier} {division}")