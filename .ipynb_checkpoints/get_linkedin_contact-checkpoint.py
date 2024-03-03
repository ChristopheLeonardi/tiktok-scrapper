def get_people(username, password, url):
    
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from bs4 import BeautifulSoup as bs
    
    people = []
    # Initialisation du navigateur
    driver = webdriver.Chrome()  # Assurez-vous d'avoir le driver approprié pour votre navigateur
    
    driver.get(url)
    
    # Attente que le bouton d'acceptation des cookies soit cliquable
    accept_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@action-type='ACCEPT']"))
    )
    
    accept_button.click()
    
    # Attente que les champs de saisie soient visibles et interactifs
    username_field = WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.ID, "username"))
    )
    password_field = WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.ID, "password"))
    )
    
    # Remplir les champs
    username_field.send_keys(username)
    password_field.send_keys(password)
    
    send_form = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='S’identifier']"))
    )
    send_form.click()
    
    try:
        while True:
            # Vérifie si la balise <span class="artdeco-button__text">Afficher plus de résultats</span> est présente
            try:
                show_more_button = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//span[@class='artdeco-button__text' and text()='Afficher plus de résultats']"))
                )
        
                # Faites défiler la page vers le bas après avoir cliqué sur le bouton "Afficher plus de résultats"
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
                # Attendez un court moment pour permettre le chargement des nouveaux éléments
                driver.implicitly_wait(3)
            except:
                break
    
        # Utilisez BeautifulSoup pour analyser le contenu de la page une fois qu'elle a été entièrement chargée
        soup = bs(driver.page_source, 'html.parser')
    
        # Trouvez tous les éléments li avec la classe .org-people-profile-card__card-spacing
        li_elements = soup.select(".org-people-profile-card__card-spacing .scaffold-finite-scroll__content ul li")
    
        people = []
    
        # Parcourez les éléments li pour extraire les données
        for li_element in li_elements:
            card = {}
            try:
                profile_title_element = li_element.find(class_='org-people-profile-card__profile-title')
                card["name"] = profile_title_element.text if profile_title_element else ""
            except:
                card["name"] = ""
    
            try:
                job_title_element = li_element.select_one(".artdeco-entity-lockup__subtitle .lt-line-clamp")
                card["job_title"] = job_title_element.text if job_title_element else ""
            except:
                card["job_title"] = ""
    
            try:
                profile_link_element = li_element.select_one(".artdeco-entity-lockup__title a")
                card["profile_link"] = profile_link_element["href"] if profile_link_element else ""
            except:
                card["profile_link"] = ""
    
            people.append(card)
    
    except Exception as e:
        print(f"Une exception s'est produite : {str(e)}")
        
    finally:
        # Fermez le navigateur à la fin du script
        driver.quit()
        return people

def create_dataframe(people, company, postes_cibles, termes_a_exclure):
    import pandas as pd

    # Nettoyez les espaces et les caractères de nouvelle ligne dans chaque valeur du dictionnaire
    for person in people:
        person['name'] = person['name'].strip().replace('\n', '')

        person['job_title'] = person['job_title'].replace('_', ' ')
        person['job_title'] = person['job_title'].strip().replace('\n', '')
        
        person['profile_link'] = person['profile_link'].split('?')[0]
    
    df = pd.DataFrame(people)
    
    # Supprimez les lignes où le nom est "Utilisateur LinkedIn"
    df = df[df['name'] != 'Utilisateur LinkedIn']
    df = df[df['job_title'] != '']
    df = df[df['job_title'] != '--']
    df = df[df['profile_link'] != '']
    
    # Créez une expression régulière en utilisant '|'.join pour combiner les termes en une seule expression
    regex_pattern = '|'.join(postes_cibles)
    exclure_pattern = '|'.join(termes_a_exclure)
    
    # Filtrer le DataFrame en utilisant str.contains avec l'expression régulière
    filtered_df = df[df['job_title'].str.contains(regex_pattern, case=False, na=False)]
    filtered_df = filtered_df[~filtered_df['job_title'].str.contains(exclure_pattern, case=False, na=False)]
    
    
    # Réinitialisez les index du DataFrame
    filtered_df.reset_index(drop=True, inplace=True)

    # Export des data
    filtered_df.to_excel("export/" + company + ".xlsx", index=False)


if __name__ == "__main__":
    
    import sys
    company = str(sys.argv[1])
    username = str(sys.argv[2])
    password = str(sys.argv[3])
    
    url = "https://www.linkedin.com/company/" + company + "/people/"
    
    postes_cibles = ["chef de projets", "cheffe de projets", "responsable", "directeur", "conservateur", "conservatrice", "curateur", "curatrice", "gestionnaire"]
    termes_a_exclure = ["Journaliste", "Chef opérateur", "Documentaliste", "comptabilité", "Ressources Humaines", "juridique", "investissements", "Affaires extérieures", "Budget", "Achats" , "Immobilier", "affaires" , "corporate" , "Ventes", "France Télévisions"]
    
    people = get_people(username, password, url)
    df = create_dataframe(people, company, postes_cibles, termes_a_exclure)

