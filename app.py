from flask import Flask, render_template, request
import csv
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import requests
from bs4 import BeautifulSoup
import re
app = Flask(__name__)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def upload_file():
    file = request.files['file']
    file.save("temp.csv")
    ids=[]
    d=dict()
    with open('temp.csv', 'r') as f:
      
        reader = csv.reader(f)
        for row in reader:
            print(row[0])
            ids.append(row[0])
    print(ids)
    r=main(ids,d)
    # do something with the file, e.g. save to disk
    # or process the data contained in the file
    return render_template('results.html',r=r)

driver = webdriver.Chrome()
driver.implicitly_wait(10)
res={}
#Author names
def get_authorname(j,d):
    driver.implicitly_wait(5)
    pydb=driver.find_element(By.XPATH, value='/html/body/div/div/div[1]/div[2]/div/div[3]/div[7]/div[5]/form/micro-ui/scopus-author-profile-page-control-microui/div[1]/div[1]/div/div[1]/div/h1/strong')
    author_name=pydb.text
    d[j]=list()
    d[j].append(author_name)
    #print(author_name)

#Citations
def get_citations(j,d):
    pydb=driver.find_element(By.XPATH, value='/html/body/div/div/div[1]/div[2]/div/div[3]/div[7]/div[5]/form/micro-ui/scopus-author-profile-page-control-microui/div[1]/div[1]/div/div[1]/section/div/div[1]/div/div/div[1]/span[1]')
    citations=pydb.text
    d[j].append(citations)
    #print(citations)

#Co-authors
def get_coauthors(j,d):
    pydb=driver.find_element(By.XPATH, value='/html/body/div/div/div[1]/div[2]/div/div[3]/div[7]/div[5]/form/micro-ui/scopus-author-profile-page-control-microui/div[1]/div[3]/div/div/div[1]/button[2]')
    co_authors=pydb.text
    d[j].append(co_authors)
    #print(co_authors)

#h-index
def get_hindex(j,d):
    driver.implicitly_wait(5)
    pydb=driver.find_element(By.XPATH, value='/html/body/div/div/div[1]/div[2]/div/div[3]/div[7]/div[5]/form/micro-ui/scopus-author-profile-page-control-microui/div[1]/div[1]/div/div[1]/section/div/div[3]/div/div/div[1]/span[1]')
    h_index=pydb.text
    d[j].append(h_index)
    #print(h_index)

#Number of documents
def get_numberofdocs(j,d):
    pydb=driver.find_element(By.XPATH, value='/html/body/div/div/div[1]/div[2]/div/div[3]/div[7]/div[5]/form/micro-ui/scopus-author-profile-page-control-microui/div[1]/div[1]/div/div[1]/section/div/div[2]/div/div/div[1]/span[1]')
    number_of_docs= pydb.text
    d[j].append(number_of_docs)
    #print(number_of_docs)

#Cited by
def citedby(j,d):
    #pydb=driver.find_element(By.XPATH, value='/html/body/div[1]/div/div[1]/div[2]/div/div[3]/div[7]/div[5]/form/micro-ui/scopus-author-profile-page-control-microui/div[1]/div[3]/div/div/div/div[1]/button[2]/span')
    pydb=driver.find_element(By.XPATH, value='/html/body/div/div/div[1]/div[2]/div/div[3]/div[7]/div[5]/form/micro-ui/scopus-author-profile-page-control-microui/div[1]/div[3]/div/div/div[2]/div[1]/div[1]/label[2]')
    cited_by= pydb.text
    d[j].append(cited_by)
    #print(cited_by)

#Snip_Score and hj index,SJR, Cite
def get_snip_score(source_ids):
    hj=[]
    
    driver.implicitly_wait(10)
    # url= "https://www.scopus.com/sourceid/21100817136"
    for src_id in source_ids:
        url= "https://www.scopus.com/sourceid/"+src_id
        #print(url)
        lol=driver.get(url)
        driver.maximize_window()
        score = None
        driver.implicitly_wait(10)
        try:
            score=driver.find_element(By.XPATH, value='/html/body/div[1]/div/div[1]/div/div/div[3]/section[1]/div[3]/div/div[3]/h2/span')

            #print(score.text)
            s=score.text
            hj.append(s)
        except NoSuchElementException:
            score='0'
            #print(score)
    su=0
    for i in hj:
        su=su+float(i)
    jindex=su
    return jindex
        
#Get all journal names to extract source ids
def get_all_journals(j,d):
    driver.implicitly_wait(10)
    url = "https://www.scopus.com/authid/detail.uri?authorId=" + j #id[j]
    #print('author is ', url)
    driver.get(url)
    driver.maximize_window()
    get_authorname(j,d)
    get_citations(j,d)
    get_coauthors(j,d)
    get_hindex(j,d)
    get_numberofdocs(j,d)
    citedby(j,d)
    journal=[]
    skill= driver.find_element(By.CSS_SELECTOR, "ul[class^='resultsList_']")
    c=0
    for i in skill.find_elements(By.TAG_NAME, 'li'):
        c=c+1
    #print(c)
    driver.implicitly_wait(10)
    for i in range(1,c+1):
        #s='/html/body/div/div/div[1]/div[2]/div/div[3]/div[7]/div[5]/form/micro-ui/scopus-author-profile-page-control-microui/div[1]/div[3]/div/div/div/div[2]/div[1]/div/div/div[2]/div/els-results-layout/div[1]/ul/li[{k}]/div/div[1]/div[3]'.format(k=i)
        s='/html/body/div/div/div[1]/div[2]/div/div[3]/div[7]/div[5]/form/micro-ui/scopus-author-profile-page-control-microui/div[1]/div[3]/div/div/div[2]/div[1]/div[2]/div[2]/div[2]/div/els-results-layout/div[1]/ul/li[{k}]/div/div[1]/div[3]'.format(k=i)
        k=driver.find_element(By.XPATH, value=s)
        j=k.find_element(By.TAG_NAME, 'span')
        journal.append(j.text)
    #print("all journals",journal)    
    return journal

#Extracting Journal names and source ids to get the snip score
def get_doc_names(ids,d):
    print(id)
    for j in range(len(ids)):
        res[ids[j]]={}
        journals= get_all_journals(ids[j],d)
        #print(journals)
        res[ids[j]]['journals']= journals
        driver.implicitly_wait(10)
        l=[]
        source_ids=[]
        for s in journals:
            if s!="":
                new_str= s.replace(" ", "+").replace(",+","%2C")
                l.append(new_str)
        #print(l)
        for i in l:
            url="https://www.scopus.com/suggest/title.uri?term="+i
           # print(url)
            lol=driver.get(url)
            driver.maximize_window()

            # extract source id's
            driver.implicitly_wait(5)
            srcID_page=driver.find_element(By.XPATH, value='/html/body/pre')
            txt=srcID_page.text
            colon_idx= txt.find('":', txt.find(':')+1)
            src_id=txt[(colon_idx+2):txt.find('}')]
            if src_id!='':
                source_ids.append(src_id)
            driver.implicitly_wait(10)
        #print(source_ids)
        hj=get_snip_score(source_ids)
        d[ids[j]].append(hj)
        #print(hj)
    return d


def main(ids,d):
    i=ids
    d=d
    r=get_doc_names(i,d)
    sr=sorted(r.items(), key=lambda x:x[1][6])
    sr=sr[::-1]
    sr=dict(sr)
    print(sr)
    return sr
@app.route('/single',methods=['POST'])
def single():

    input_text = request.form['personid']
    ids=[]
    d=dict()
    ids.append(input_text)
    r=main(ids,d)
    print(ids)
    return render_template('results.html',r=r)
@app.route('/process_id', methods=['POST'])
def process_id():
    id = request.form['id']
    ids=[]
    d=dict()
    ids.append(id)
    r=main(ids,d)
    print(ids)
    return render_template('results.html',r=r)
  
if __name__ == '_main_':
    app.run(debug=True)



