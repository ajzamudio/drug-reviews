from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import Context, loader
import requests
from bs4 import BeautifulSoup
import pandas
from subprocess import Popen
import warnings
import time
warnings.filterwarnings("ignore")
from . import tasks

def home(request):
    return render(request, 'home.html')

def result(request):
    try:
        keyword = request.GET['keyword']
        keyword = keyword.strip().lower() #social
        drug = request.GET['drug']
        drug = drug.strip().lower() #dextroamphetamine

        #get the last page number on website
        link= "https://www.drugs.com/comments/" + drug + ".html" + "/?page=20000"  #this converts to a link with the last page number
        r = requests.get(link, verify=False)
        c=r.content
        soup=BeautifulSoup(c,"html.parser")
        page_number=soup.find_all("li",{"class":"is-active"})
        page_number = page_number[0].find("span",{"aria-current":"page"}).text
        print("found %s page(s)" % page_number)
        l=[]

        #loop through each page and append data to a list
        for page in range(1,int(page_number)+1):
            try:
                print("reading %d of %s page(s)" % (page, page_number))
                r = requests.get("https://www.drugs.com/comments/" + drug + ".html" + "/?page=" + str(page), verify=False)
                c=r.content
                soup=BeautifulSoup(c,"html.parser")
                all=soup.find_all("div",{"class":"ddc-comment"})
                for item in all:
                    d={}
                    try:
                        d["Comment"] = str(item.find("p",{"class":"ddc-comment-content"}).text)
                    except:
                        d["Comment"] = "none"
                    try:
                        d["Rating"] = item.find("div",{"class":"rating-score"}).text
                    except:
                        d["Rating"] = "none"
                    try:
                        d["User Info"] = str(item.find("div",{"class":"ddc-comment-header ddc-comment-section"}).text)
                    except:
                        d["User Info"] = "none"
                    try:
                        d["Page Number"] = str(page)
                    except:
                        d["Page Number"] = "none"
                    if keyword in d["Comment"]:
                        l.append(d)
            except:
                null="null"
                print("error gathering page data")

        #add website data to excel file
        pandas.set_option('display.max_colwidth', -1)
        df=pandas.DataFrame(l)
        df = df[['Comment','Rating','User Info','Page Number']]
        df.sort_values(by='Rating', ascending=False)
        length = len(df.index)
        df=df.to_html()
    except:
        df="no data found for drug {} with keyword {}".format(drug,keyword)
        length="";link="https://www.drugs.com"
        print("error gathering dataframe")
        time.sleep(2)

    return render(request, 'result.html',{'df':df,'drug':drug,'keyword':keyword,'length':length, 'link':link})

#note