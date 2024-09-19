import instaloader as il
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from database import Database
from requests_ip_rotator import ApiGateway
import requests

class InstagramCrawler:
    def __init__(self, username, password, sessionfile, URI, AUTH):
        self.gateway = ApiGateway("https://www.instagram.com") 
        self.L = il.Instaloader(session=requests.Session().mount("https://www.instagram.com", self.gateway))
        self.username = username
        self.password = password
        self.sessionfile = sessionfile
        self._login()
        self.db = Database(URI, AUTH)
        
    def _login(self):
        try:
            #self.L.load_session_from_file(self.username, self.sessionfile)
            self.L.login(self.username, self.password)
        except Exception as e:
            print(f"Errore durante il caricamento della sessione: {e}")
            exit(1)

    def get_followees(self, username, current_depth, max_depth, sleep_time):
        if current_depth > max_depth:
            return

        try:
            profile = il.Profile.from_username(self.L.context, username)
        except Exception as e:
            print(f"Errore durante il recupero del profilo {username}: {e}")
            return

        futures = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            try:
                followees = list(profile.get_followees())
            except Exception as e:
                print(f"Errore durante il recupero dei followees di {username}: {e}")
                return

            with tqdm(total=len(followees), desc=f"Processing {username}") as pbar:
                for followee in followees:
                    followee_info = {
                        'username': followee.username,
                        'is_business': followee.is_business_account,
                        'is_verified': followee.is_verified,
                        'business_category': followee.business_category_name
                    }

                    futures.append(executor.submit(self._process_followee, followee_info, username, current_depth, max_depth, sleep_time))
                    pbar.update(1)

                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        print(f"Errore durante l'elaborazione di un futuro: {e}")

    def _process_followee(self, followee_info, username, current_depth, max_depth, sleep_time):
        try:
            self.db.create_user(followee_info)
            self.db.create_follow(username, followee_info['username'])
        except Exception as e:
            print(f"Errore durante l'operazione del database: {e}")

        if not followee_info['is_business']:
            self.get_followees(followee_info['username'], current_depth + 1, max_depth, sleep_time)

        time.sleep(sleep_time)

    def get_followers(self, username, sleep_time):
        try:
            profile = il.Profile.from_username(self.L.context, username)
        except Exception as e:
            print(f"Errore durante il recupero del profilo {username}: {e}")
            return

        futures = []

        try:
            followers = list(profile.get_followers())
        except Exception as e:
            print(f"Errore durante il recupero dei followers di {username}: {e}")
            return

        with ThreadPoolExecutor(max_workers=10) as executor:
            with tqdm(total=len(followers), desc=f"Processing {username}'s followers") as pbar:
                for follower in followers:
                    follower_info = {
                        'username': follower.username,
                        'is_business': follower.is_business_account,
                        'is_verified': follower.is_verified,
                        'business_category': follower.business_category_name
                    }

                    futures.append(executor.submit(self._process_follower, follower_info, username, sleep_time))
                    pbar.update(1)

                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        print(f"Errore durante l'elaborazione di un futuro: {e}")

    def _process_follower(self, follower_info, username, sleep_time):
        try:
            self.db.create_user(follower_info)
            self.db.create_follow(follower_info['username'], username)
        except Exception as e:
            print(f"Errore durante l'operazione del database: {e}")

        time.sleep(sleep_time)

    def run(self, target_username, max_depth, sleep_time):
        try:
            self.db.create_user({
                'username': target_username,
                'is_business': False,
                'is_verified': False,
                'business_category': None
            })
        except Exception as e:
            print(f"Errore durante la creazione dell'utente: {e}")

        try:
            self.get_followers(target_username, sleep_time)
        except Exception as e:
            print(f"Errore durante il recupero dei followers: {e}")

        try:
            self.get_followees(target_username, 1, max_depth, sleep_time)
        except Exception as e:
            print(f"Errore durante il recupero della lista dei followees: {e}")

        # Chiudi la connessione al database
        self.db.close()