import pandas as pd
import re
import os
import pymysql
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sklearn.metrics.pairwise
pymysql.install_as_MySQLdb()
from sqlalchemy import create_engine
import mysql.connector
os.getcwd()
os.chdir("/usr/08-Job recommendation system")
pd.set_option("display.max_columns", 50)



# O*NET Data
## Read and clean up O*net data
### Title: job title
### Element Name: related major 

data_onet = pd.read_excel("Knowledge.xlsx")
data_onet = data_onet[["Title", "Element Name"]]
data_onet = data_onet.drop_duplicates()
data_onet = data_onet.groupby('Title')["Element Name"].apply(','.join).reset_index()
data_onet
### Different job have same related majors, and one job related with around 30 majors, data is not accurate.



# Build Model
## Perform TFIDF on Major(Element Name)
### TFIDF is a technique to quantify a word in documents, we generally compute a weight to each word which signifies the importance of the word in the document. The higher the value is, means the more important this word is in the document.

vect = TfidfVectorizer()
tfidf_matrix = vect.fit_transform(datarelated['Element Name'])
df1 = pd.DataFrame(tfidf_matrix.toarray(), columns = vect.get_feature_names())
print(df1)

## Perform Assosiation Rule to get the top 10 related job with major
### Get all the common words from major column and job description column, then find the most important or related top 10 jobs based on the sum of TFIDF in major column multiply TFIDF in job description column, the higher the sum value is, the more relevant job is with the major.

intersect_cols = set(df1.columns).intersection(set(df2.columns))

d = dict()
for j in range(len(df1)):
    a = []
    for i in range(len(df2)):
        a.append(sum(df1[intersect_cols].iloc[j] * df2[intersect_cols].iloc[i]))
    top10 = [a.index(_) for _ in sorted(a, reverse=True)[:10]]
    d[j] = top10
    print(j)


# Job Hero
## Read and clean up Job Hero data
### Because the O*NET data is too general and not accurate. We crawl the job requiremnt with major from Job Hero website.
### Links: job link on job here
### Job: job tile
### Intro:job description
### Info.1, Unnamed5,6,,8,9 : other uncleaned info including job requirement, job resposibility.

data_job_hero = pd.read_csv('jobherotext.csv',encoding = "ISO-8859-1")
data_job_hero.head()

## Using Regress Expression extract job required major and degree
majors = []
for text in data_job_hero.Info:
    majors.append([(_[0], _[-2]) for _ in re.findall(r"(bachelor|master|high school diploma)(.*?)(degree)(\s)(in)(.*?)( and |\.|\;|\:)", text)])

jobmajor = pd.DataFrame({'Links':list(data_job_hero.Links),
              'Job':list(data_job_hero.Job),
              'Intro':list(data_job_hero.Intro),
              'Info':list(data_job_hero.Info),
              'Major':majors,
         
                   })
print(jobmajor)
jobmajor.to_csv("jobmajor.csv",index=None)



# Build model on Job Here data
## Perform TF-IDF on Major

vect = TfidfVectorizer()
tfidf_matrix = vect.fit_transform(data5['Major'])
df1 = pd.DataFrame(tfidf_matrix.toarray(), columns = vect.get_feature_names())
print(df1)

## Perform TFIDF on Job Description(Intro)

vect = TfidfVectorizer()
tfidf_matrix = vect.fit_transform(data5['Intro'])
df2 = pd.DataFrame(tfidf_matrix.toarray(), columns = vect.get_feature_names())
print(df2)

## Perform Assosiation Rule to get the top 10 related job with major
### Get all the common words from major column and job description column, then find the most important or related top 10 jobs based on the sum of TFIDF in major column multiply TFIDF in job description column, the higher the sum value is, the more relevant job is with the major.

intersect_cols = set(df1.columns).intersection(set(df2.columns))
d2 = dict()
for j in range(len(df1)):
    a = []
    for i in range(len(df2)):
        a.append(sum(df1[intersect_cols].iloc[j] * df2[intersect_cols].iloc[i]))
    top10 = [a.index(_) for _ in sorted(a, reverse=True)[:10]]
    d2[j] = top10
    print(j)



## Using model result to append top 10 related jobs into data

d2_job = dict()
for k, v in d2.items():
    jobs = [data5.iloc[_]['Job'] for _ in v]
    jobs2 = []
    for _ in jobs:
        if _ == '3D Artist':
            jobs2.append(None)
        else:
            jobs2.append(_)
    d2_job[k] = jobs2

list(d2_job.values()).__len__()

jobrecommend=[]
for j in range(0,1692):
    for i in d2[j]:
        if i == 0:
            jobrecommend.append('')
        else:
            jobrecommend.append(data5['Job'][i])

jobrecommendation = pd.DataFrame({'Links':list(data4.Links),
              'Job':list(data4.Job),
              'Intro':list(data4.Intro),
              'Info':list(data4.Info),
              'Major':majors,
              'Job_Recommend':list(d_job.values()),
                   })
print(jobrecommendation)



# Save result into csv file
jobrecommendation.to_csv("jobrecommend.csv",index=None)









