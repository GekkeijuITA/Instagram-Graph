from neo4j import GraphDatabase, Query
from neo4j.exceptions import Neo4jError

class Database:
    def __init__(self, uri, auth):
        try:
            with GraphDatabase.driver(uri, auth=auth) as driver:
                driver.verify_connectivity()
                self.driver = driver
                self.session = self.driver.session(database="neo4j")
        except Neo4jError as e:
            print(f"Errore di connessione: {e}")
            raise

    def close(self):
        try:
            self.driver.close()
            self.session.close()
        except Neo4jError as e:
            print(f"Errore durante la chiusura della connessione: {e}")

    """
        user: {
            username,
            is_business,
            is_verified,
            business_category
        }
    """
    def create_user(self, user):
        try:
            query = Query(
                """
                MERGE (u:User {username: $username})
                ON CREATE SET u.is_business = $is_business, u.is_verified = $is_verified, u.business_category = $business_category
                RETURN u
                """
            )

            result = self.session.run(query, username=user["username"], is_business=user["is_business"], is_verified=user["is_verified"], business_category=user["business_category"])
            record = result.single()
            if record and record.get("u"):
                pass
            else:
                pass
        except Neo4jError as e:
            print(f"Errore durante la creazione dell'utente: {e}")

    def delete_user(self, username):
        try:
            query = Query(
                "MATCH (u:User {username: $username}) DETACH DELETE u"
            )

            self.session.run(query, username=username)
        except Neo4jError as e:
            print(f"Errore durante l'eliminazione dell'utente: {e}")

    def create_follow(self, follower, followee):
        try:
            query = Query(
                """
                MATCH (s:User {username: $follower})
                MERGE (t:User {username: $followee})
                ON CREATE SET t.is_business = False, t.is_verified = False, t.business_category = NULL
                MERGE (s)-[:FOLLOWS]->(t)
                RETURN s, t
                """
            )

            result = self.session.run(query, follower=follower, followee=followee)
            record = result.single()
            if record:
                if record.get("t"):
                    pass
                else:
                    pass
            else:
                pass
        except Neo4jError as e:
            print(f"Errore durante la creazione del follow: {e}")

    def delete_follow(self, user, followee):
        try:
            query = Query(
                """
                MATCH (s:User {username: $user})
                MATCH (t:User {username: $followee})
                DELETE s[:FOLLOWS]->t
                RETURN s, t
                """
            )

            result = self.session.run(query, user=user, followee=followee)
            if result.single().get("t"):
                pass
            else:
                pass
        except Neo4jError as e:
            print(f"Errore durante l'eliminazione del follow: {e}")
