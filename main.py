from crawler import InstagramCrawler

if __name__ == "__main__":
    # Imposta i parametri
    max_depth = 2
    sleep_time = 2  # Tempo di attesa tra le richieste in secondi
    target_username = "lore.vacca03"
    sessionfile = "sessionfile.txt"

    URI = "bolt://localhost:7687"
    AUTH = ("vacca", "vacca")

    crawler = InstagramCrawler("shityeah5", "Password24!", sessionfile, URI, AUTH)
    crawler.run(target_username, max_depth, sleep_time)

    print("Crawler completato")