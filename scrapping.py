import time
import networkx as nx
from bs4 import BeautifulSoup
import requests
import multiprocessing

paper_link = 'https://www.medicinenet.com'

diseasesWithSymptoms = {}
results = []


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
    return diseasesWithSymptoms

def multiprocessing_func(x, return_list):
    #time.sleep(2)
    #getData(x)
    return_list.append(getData(x))

if __name__ == '__main__':
    paper_link_aux = 'https://www.medicinenet.com/symptoms_and_signs/alpha_a.htm'
    page = requests.get(paper_link_aux)
    soup = BeautifulSoup(page.content, 'html.parser')
    totalSymptomsDiv = soup.find_all('div', id="A_Z")[0]
    totalSymptomsLinks = totalSymptomsDiv.find_all('li')
    processes = []
    manager = multiprocessing.Manager()
    results_list = manager.list()

    for link in totalSymptomsLinks:
        print(f"Ahora empieza en link {link}")
        p = multiprocessing.Process(target=multiprocessing_func, args=(link, results_list))
        processes.append(p)
        p.start()

    for proc in processes:
        proc.join()
        print("Ahora ha acabado 1 link")

    d1 = {k: v for e in results_list for (k, v) in e.items()}

    print(f"Este es el diccionario resultante: \n\n {d1}")