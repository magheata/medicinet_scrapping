import networkx as nx
from bs4 import BeautifulSoup
import requests
import multiprocessing

paper_link = 'https://www.medicinenet.com'

diseasesWithSymptoms = {}

def getDiseases(diseasesForSymptom):
    diseases = []
    for diseaseForSymptom in diseasesForSymptom:
        diseaseForSymptomText = diseaseForSymptom.text
        if "(" in diseaseForSymptomText:
            diseaseForSymptomText = diseaseForSymptomText.split("(")[0]
        if ":" in diseaseForSymptomText:
            diseaseForSymptomText = diseaseForSymptomText.split(":")[0]
        if not "?" in diseaseForSymptomText and not "When" in diseaseForSymptomText:
            diseases.append(diseaseForSymptomText)
    return diseases

def getDiseasesForSymptom(symptomSoup):
    diseasesForSymptom = []
    diseases = symptomSoup.find('div', class_="indexDCList")
    if not diseases:
        diseases = symptomSoup.find('ul', class_="condlist")
    if diseases:
        diseasesForSymptom = diseases.find_all('h2', itemprop="alternativeHeadline")
    return diseasesForSymptom

symptomsWordsToAvoid = ["Symptoms", "Signs"]
diseasesWordsToAvoid = ["?", "When", "Symptoms", "Signs"]

def getDiseasesForSymptomsLink(symptoms, diseasesWithSymptoms):
    for symptom in symptoms:
        symptomLinks = symptom.find_all('a')
        for symptomLink in symptomLinks:
            symptom = symptomLink.text
            if not "Symptoms" in symptom and not "Signs" in symptom:
                #print(symptom)
                symptomPage = requests.get(symptomLink['href'])
                symptomSoup = BeautifulSoup(symptomPage.content, 'html.parser')
                diseasesForSymptom = getDiseasesForSymptom(symptomSoup)
                if diseasesForSymptom:
                    diseases = getDiseases(diseasesForSymptom)
                    for disease in diseases:
                        if disease in diseasesWithSymptoms:
                            symptomsList = diseasesWithSymptoms[disease]
                            symptomsList.append(symptom)
                        else:
                            diseasesWithSymptoms[disease] = [symptom]

def getData(link):
    diseasesWithSymptoms = {}
    realLink = link.find('a')['href']
    symptomPage = requests.get(paper_link + realLink)
    symptompsSoup = BeautifulSoup(symptomPage.content, 'html.parser')
    pageSymptoms = symptompsSoup.find('div', class_="AZ_results")
    symptoms = pageSymptoms.find_all('li')
    getDiseasesForSymptomsLink(symptoms, diseasesWithSymptoms)

if __name__ == '__main__':
    paper_link_aux = 'https://www.medicinenet.com/symptoms_and_signs/alpha_a.htm'
    page = requests.get(paper_link_aux)
    soup = BeautifulSoup(page.content, 'html.parser')
    totalSymptomsDiv = soup.find_all('div', id="A_Z")[0]
    totalSymptomsLinks = totalSymptomsDiv.find_all('li')
    jobs = []
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    for link in totalSymptomsLinks:
        print(f"Ahora empieza en link {link}")
        p = multiprocessing.Process(target=getData(link))
        jobs.append(p)
        p.start()

    results = []
    for proc in jobs:
        proc.join()
        print("Ahora ha acabado 1 link")
        #results.append(return_dict.value)

    print(results)