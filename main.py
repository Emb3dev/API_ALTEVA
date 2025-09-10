from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
import urllib3

# Pour éviter les warnings de certificat SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = FastAPI()

BASE_URL = "https://www.m7.alteva.eu/emIsSIOn2?base=eesce"

# Modèle de payload avec un espace réservé pour le numéro de DI
DATA_TEMPLATE = (
    "WD_ACTION_=AJAXPAGE&EXECUTE=16&WD_CONTEXTE_=A122&"
    "WD_JSON_PROPRIETE_=%7B%22m_oChampsModifies%22%3A%7B%22A13%22%3Atrue%7D%7D&"
    "WD_BUTTON_CLICK_=A12&A13=NUMERODEDI&A14=1&A313=1&A314=0&A6=2&A124=1&"
    "A462=1&A209=0&A45=%3CTous%20les%20locaux%3E&A46=%3CTous%20les%20Centres%20Techniques%3E&"
    "A117=%3CTous%20les%20Centres%20Financiers%3E&A47=%3CToutes%20les%20arborescences%20libres%3E&"
    "A119=%3CTous%20les%20domaines%3E&A437=%3CTous%20les%20Intervenants%3E&A465=%3CTous%20les%20appelants%3E&"
    "A123=1&A131=5&A2=-1&A2_DEB=1&_A2_OCC=0&I76=1&I74=0,00&I75=0,00&I34=1&DATEDEB_CAL_MOIS=20250901"
)


def _extract_text(soup: BeautifulSoup, element_id: str):
    """Retourne le texte d'un élément identifié par son id."""
    tag = soup.find(id=element_id)
    return tag.get_text(strip=True) if tag else None


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


@app.get("/demande/{numero}")
def get_demande(numero: str, token: str):
    """Récupère les informations d'une demande d'intervention."""
    url = "https://www.m7.alteva.eu/emIsSIOn2/Page_Consultation_DI_NVMENU/aDEAAIxe2gIHAA"
    headers = {
        "accept": "*/*",
        "accept-language": "fr-FR,fr;q=0.7",
        "content-type": "application/x-www-form-urlencoded",
        "origin": "https://www.m7.alteva.eu",
        "priority": "u=0, i",
        "referer": f"https://www.m7.alteva.eu/emIsSIOn2/Page_Accueil_Tuiles/{token}",
        "sec-ch-ua": '\"Chromium\";v=\"140\", \"Not=A?Brand\";v=\"24\", \"Brave\";v=\"140\"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '\"Windows\"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "sec-gpc": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
    }
    cookies = {
        "DYN_SECURITE3168": "FE1DC6097822A2E7C338",
        "wbNavigateurLargeur": "1905",
    }
    data = DATA_TEMPLATE.replace("NUMERODEDI", numero)
    try:
        response = requests.post(
            url,
            headers=headers,
            cookies=cookies,
            data=data,
            verify=False,
            timeout=10,
        )
        response.raise_for_status()

        xml_soup = BeautifulSoup(response.text, "xml")
        corps = xml_soup.find("CORPS")
        if not corps:
            return {"error": "Structure de réponse inattendue"}

        html_soup = BeautifulSoup(corps.text, "html.parser")
        info = {
            "numero": _extract_text(html_soup, "zrl_1_A72"),
            "etat": _extract_text(html_soup, "zrl_1_A99"),
            "domaine": _extract_text(html_soup, "zrl_1_A76"),
            "objet": _extract_text(html_soup, "zrl_1_A93"),
            "local": _extract_text(html_soup, "zrl_1_A77"),
            "intervenant": _extract_text(html_soup, "zrl_1_A78"),
        }
        return info
    except Exception as e:
        return {"error": str(e)}
