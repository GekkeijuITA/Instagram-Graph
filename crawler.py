import instaloader as il
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

L = il.Instaloader()

# Effettua il login
L.login("u6vwo85vkf", "YoweFe24!")

# Funzione per ottenere la lista di followees con un intervallo di attesa
def get_followees(username, current_depth, max_depth, sleep_time):
    if current_depth > max_depth:
        return []
    
    profile = il.Profile.from_username(L.context, username)
    follow_list = []
    
    for followee in profile.get_followees():
        follow_list.append({
            'username': followee.username,
            'is_business': followee.is_business_account,
            'is_verified': followee.is_verified,
            'business_category': followee.business_category_name
        })
        
        # Introduci un intervallo di attesa tra le richieste
        time.sleep(sleep_time)
    
    return follow_list

# Funzione per gestire la ricorsione multithreaded con indicatore di progresso
def followees_list_multithread(username, current_depth, max_depth, sleep_time):
    if current_depth > max_depth:
        return []

    profile = il.Profile.from_username(L.context, username)
    follow_list = []
    futures = []

    # Crea un ThreadPoolExecutor per esplorare i seguiti in parallelo
    with ThreadPoolExecutor(max_workers=5) as executor:
        followees = list(profile.get_followees())
        
        # Aggiungi un indicatore di progresso
        with tqdm(total=len(followees), desc=f"Processing {username}") as pbar:
            for followee in followees:
                follow_list.append({
                    'username': followee.username,
                    'is_business': followee.is_business_account,
                    'is_verified': followee.is_verified,
                    'business_category': followee.business_category_name
                })
                futures.append(executor.submit(get_followees, followee.username, current_depth + 1, max_depth, sleep_time))
                
                # Aggiorna l'indicatore di progresso
                pbar.update(1)
            
            # Raccogli i risultati dalle chiamate parallele
            for future in as_completed(futures):
                follow_list.extend(future.result())
                # Aggiorna l'indicatore di progresso
                pbar.update(1)

    return follow_list

# Imposta i parametri
max_depth = 1
sleep_time = 2  # Tempo di attesa tra le richieste in secondi
profile = il.Profile.from_username(L.context, "lore.vacca03")

# Ottieni i seguiti fino a un massimo di max_depth livelli usando il multithreading
follow_list = followees_list_multithread(profile.username, 1, max_depth, sleep_time)

# Output formattato
for followee_info in follow_list:
    print(f"Username: {followee_info['username']}, Business: {followee_info['is_business']}, Verified: {followee_info['is_verified']}, Category: {followee_info['business_category']}")
