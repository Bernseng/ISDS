import pandas as pd
import numpy as np
import re
import requests
from bs4 import BeautifulSoup
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import nltk
from nltk import FreqDist
import seaborn as sns

with open('stopord.txt', encoding='utf8') as f:
    stopord = f.read().splitlines()
stop_word = nltk.corpus.stopwords.words('danish') + stopord

def fetching_occupation(uri):

    url = f'http://ec.europa.eu/esco/api/resource/occupation?uri={uri}&language=da'

    response = requests.get(url)

    result = response.json()

    job_title = result['title']
    joblist = []

    for i in range(1000):
        try:
            essential_skill = result['_links']['hasEssentialSkill'][i]['title']
            optional_skill = result['_links']['hasOptionalSkill'][i]['title']
        except:
            break

        job = {
        'job_title' : job_title,
        'essential_skill': essential_skill,
        'optional_skill' : optional_skill
        }   
        joblist.append(job)

        

        jobs = pd.DataFrame(data=joblist, columns=['job_title', 'essential_skill', 'optional_skill'])

        # jobs = jobs.set_index(['title'], append=True).swaplevel(0,1)

    return jobs

def UG(page, tag):
    
    headers = {'User-Agent':'kjp538@alumni.ku.dk'}
    
    url = f"https://www.ug.dk/search/{tag}?page={page}"
    
    r = requests.get(url, headers)

    soup = BeautifulSoup(r.content.decode("utf-8"), "html.parser")
    
    divs = soup.find_all("div", class_="node node-uddannelse node-teaser clearfix")

    list_of_articles = []

    for i in range(len(divs)):
        list_of_articles.append(divs[i].find('a')['href'])
    
    list_of_articles_final = []
    for link in list_of_articles:
        if '/kandidatuddannelser/' in link:
            list_of_articles_final.append(link)

    return list_of_articles_final

def extract_UG(link):

    headers = {'User-Agent':'kjp538@alumni.ku.dk'}

    url = 'http://ug.dk' + link

    r = requests.get(url, headers)

    soup = BeautifulSoup(r.content.decode("utf-8"), "html.parser")
    
    divs_intro = soup.find_all("div", class_="pane-content")

    temp_intro = soup.find_all('p')

    divs_main = soup.find_all("div", class_="field-content")

    temp_main = soup.find_all('li')
    
    main_text = []
    main_text.append(temp_main)
    main_text.append(temp_intro)
    main_text = ' '.join(str(i) for i in main_text)


    return main_text

def clean_text(text):
    # text.split(' ')
    # text = text.replace('[','').replace(']', '')
    text = text.lower()
    text = re.sub("^\d+\s|\s\d+\s|\s\d+$|[^a-zA-ZæøåÆøå]+|(<li>)|(</li>)|</p>|<p>|\xa0|<ul>|</ul>|'|-| +|,| ,|</a>|<a>|<a|[.]|[:]|\n|[?]", " ", text)
    # text = re.sub("[^a-zA-Z0-9 -]", '', text)
    # text = re.sub("(<li>)|(</li>)|</p>|<p>|\xa0|<ul>|</ul>|'|-| +|,| ,|</a>|<a>|<a|[.]|[:]|\n|[?]", '', text)
    text = re.sub(" +", " ", text)
    return text
    
def extract_UG(link):

    headers = {'User-Agent':'kjp538@alumni.ku.dk'}

    url = 'http://ug.dk' + link

    r = requests.get(url, headers)

    soup = BeautifulSoup(r.content.decode("utf-8"), "html.parser")

    divs_intro = soup.find_all("div", class_="region region-content")
    for item in divs_intro:
        intro = item.find_all("p")[0:6]
        indhold = item.find_all('ul')[0:1]
        outro = item.find_all('p')[19:22]
    
    text = ' '.join([str(i) for i in intro]) + ' '.join([str(i) for i in indhold]) + ' '.join([str(i) for i in outro])
    text = clean_text(text)
    return text

def write_text(list_name, list_):
    with open(f"{list_name}.txt", "w", encoding='utf-8') as fp:
        for item in list_:
            fp.write("%s " % item)
    fp.close() 

def extract_ku(fag):
    
    headers = {'User-Agent':'bwt973@alumni.ku.dk'}
    
    url = f"https://studier.ku.dk/kandidat/{fag}/faglig-profil-og-job/"
    
    r = requests.get(url, headers)

    soup = BeautifulSoup(r.content.decode("utf-8"), "html.parser")
    
    return soup

def transform_ku(soup):

    divs = soup.find_all("div", class_="col-xs-12 col-sm-8 col-md-6 main-content")

    text_ku =[]

    for i in range(len(divs)):
        text_ku.append(divs[i].find_all("p"))

    divs2 = soup.find_all("div", class_="col-xs-12 col-sm-8 col-md-6 main-content")

    for i in range(len(divs2)):
        text_ku.append(divs2[i].find_all("ul"))
    
    return text_ku

def extract_au(fag):
    
    headers = {'User-Agent':'tps798@alumni.ku.dk'}
    
    url = f"https://bachelor.au.dk/{fag}"
    
    r = requests.get(url, headers)

    soup = BeautifulSoup(r.content.decode("utf-8"), "html.parser")
    
    return soup

def extract_aau(fag):
    
    headers = {'User-Agent':'bwt973@alumni.ku.dk'}
    
    url = f"https://www.aau.dk/uddannelser/kandidat/{fag}"
    
    r = requests.get(url, headers)

    soup = BeautifulSoup(r.content.decode("utf-8"), "html.parser")
    
    return soup

def make_a_list(series):

    new_list = []

    list1 = series.to_list()

    for item in list1:
        new_list.append(clean_text(item))

    new_final_df = pd.DataFrame(data=new_list)

    return new_final_df

def generate_better_wordcloud(data, size):
    cloud = WordCloud(scale=3,
                      max_words=100, #Maximum words in the WordCloud
                      colormap='ocean', #Color of the WordCloud
                      background_color='white',
                      max_font_size=28,
                      mask=None,
                      relative_scaling=0.5,
                      stopwords=stop_word, #Setting StopWords equal to the updated
                      collocations=False).generate(data)
    plt.figure(figsize=size)
    plt.imshow(cloud)
    plt.axis('off') #No axis 
    plt.show()

def frequency_plot(data):
    plot = FreqDist(data).most_common(20)
    all_fdist = pd.Series(dict(plot))
    fig, ax = plt.subplots(figsize=(10,10))
    sns.barplot(x=all_fdist.values, y=all_fdist.index, ax=ax, color='navy', ci=None)
    plt.ylabel('Words', fontsize=14)
    plt.xlabel('Count', fontsize=14)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=16) #rotation=30
    plt.show()