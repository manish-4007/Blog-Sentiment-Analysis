import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen
import pandas as pd

def extract_blog(blog_link):
    try:
        urlclient = urlopen(blog_link)
        blog_page  = urlclient.read()

    # Scrape the html of the page
        b_html = bs(blog_page,'html.parser')
        #Extract the topic content of the article
        if b_html.find_all("header" ):
            titlebox = b_html.find_all("header" )
            title = titlebox[0].h1.text

        else :
            titlebox = b_html.find('h1', {'class':"tdb-title-text"})
            title = titlebox.text

    #extract all the article text from the blog
        content_box = b_html.find_all("div", {'class': "td-post-content"})
        p_html = content_box[0].find_all("p")

    # Merge all the paragraph into a list
        paras = ""
        for i in p_html:
            paras += i.text+ " "
            
    except Exception as e:
        print( "\n\n", e, "\n")
        title = ""
        paras = ""
        
    return {"Title":title, "Article": paras}


def make_article_file(id, blog_url):
    print(blog_url)
    blog = extract_blog(blog_url)

    with open("files/"+str(int(id))+".txt", "w",encoding="utf-8") as file:
        file.write(str(blog))
        file.close()

input = pd.read_excel('./Input.xlsx')
input = input.set_index('URL_ID') 

    
#Iterating all the dataframe and get the link of the articles

for i in input.index:
    blog_url = input.loc[i][0]
    make_article_file(i, blog_url)