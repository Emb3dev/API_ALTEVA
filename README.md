# API_ALTEVA

## Running the server

From the project root, start the FastAPI server with:

```bash
cd /workspace/API_ALTEVA
uvicorn main:app --reload
```

If you run `uvicorn` from outside the project directory, include the full module path:

```bash
uvicorn API_ALTEVA.main:app
```

## Endpoints

- `/get_token` : récupère le token dynamique de la page de connexion.
- `/login` (POST) : envoie `user`, `password` et `token` pour authentifier l'utilisateur.
