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
    du formulaire de la page de login eMission2 et retourne les cookies
    renvoyés par le serveur.
    """
    try:
        # Récupère le HTML
        response = requests.get(BASE_URL, verify=False, timeout=10)
        response.raise_for_status()

        # Récupère les cookies renvoyés par le serveur
        cookies = response.cookies.get_dict()
        set_cookie = response.headers.get("set-cookie")

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
            "token": token,
            "cookies": cookies,
            "set_cookie": set_cookie,
        }

    except Exception as e:
        return {"error": str(e)}


@app.post("/login")
def login(user: str, password: str, token: str):
    """Envoie les identifiants et retourne la réponse ainsi que les cookies."""
    url = f"https://www.m7.alteva.eu/emIsSIOn2/Page_Authentification/{token}"
    data = {
        "WD_JSON_PROPRIETE_": "{\"m_oProprietesSecurisees\":{},\"m_oChampsModifies\":{\"A22\":true,\"A23\":true},\"m_oVariablesProjet\":{},\"m_oVariablesPage\":{}}",
        "WD_BUTTON_CLICK_": "A25",
        "WD_ACTION_": "",
        "A22": user,
        "A23": password,
        "A13_DATA": "true,1",
        "A24": "1",
    }
    try:
        response = requests.post(
            url,
            data=data,
            verify=False,
            timeout=10,
        )
        response.raise_for_status()

        # Récupère les cookies renvoyés par le serveur
        cookies = response.cookies.get_dict()
        set_cookie = response.headers.get("set-cookie")

        return {
            "response": response.text,
            "cookies": cookies,
            "set_cookie": set_cookie,
        }
    except Exception as e:
        return {"error": str(e)}
