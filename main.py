from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
import urllib3

# Pour éviter les warnings de certificat SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = FastAPI()

BASE_URL = "https://www.m7.alteva.eu/emIsSIOn2?base=eesce"


@app.get("/")
def home():
    return {"message": "API pour récupérer le token eMission2"}


@app.get("/get_token")
def get_token():
    """
    Récupère le token dynamique contenu dans l'attribut 'action'
    du formulaire de la page de login eMission2.
    """
    try:
        # Récupère le HTML
        response = requests.get(BASE_URL, verify=False, timeout=10)
        response.raise_for_status()

        # Parse le HTML
        soup = BeautifulSoup(response.text, "html.parser")

        # Trouve le formulaire d'authentification
        form = soup.find("form", {"name": "PAGE_AUTHENTIFICATION"})
        if not form:
            return {"error": "Formulaire d'authentification introuvable"}

        action = form.get("action")
        if not action:
            return {"error": "Action introuvable dans le formulaire"}

        # Extraction du token (dernier segment de l'URL)
        token = action.split("/")[-1]

        return {
            "action_url": action,
            "token": token
        }

    except Exception as e:
        return {"error": str(e)}
