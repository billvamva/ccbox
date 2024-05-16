from ccbox.authentication import Authentication

if __name__ == "__main__":
        auth = Authentication()
        auth_user = auth.login("username", "password123")
        print("Authentication successful:", auth_user)


