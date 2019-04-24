#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 14:39:13 2019

@author: shannonhagerty
"""

# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import config
import requests

def getAuthIDFromName(FirstName,LastName,Affiliation='brandeis university'):
    """This function takes three arguments 1) First name of person, 
    2) Last Name of Person, and 3)University affiliation which is 
    brandeis university by default.  The function querys Scopus API and returns an int
    authorID and int total document count in scopus for the faculty. It 
    only makes a match if only one person with that affiliation is found, if 
    more than one person found then authID an Scopus ID is set to 0"""

    query='authlast({'+LastName+'}) and authfirst({'+FirstName+'}) and affil({'+Affiliation+'})'
    query_params = {'query':query}
    baseurl = 'http://api.elsevier.com/content/search/author'
    response = requests.get(baseurl, headers=config.apiKey, params = query_params)
    data = response.json()
    authResults=data['search-results']['entry']
    resultCount = data['search-results']['opensearch:totalResults']
    
    if int(resultCount) != 1:        
        print("Perfect Match Not Found "+FirstName+' '+ LastName)
        authID = '0'
        documentCount= '0'
    else: 
        authID = authResults[0]['dc:identifier'].split(':')[1]
        documentCount=data['search-results']['entry'][0]['document-count']
    return authID, documentCount

def getArticleInfo(ScopusID):
    """ This function has one agrument, ScopusID which is associated with each
    paper in Scopus Database, it then queries Scopus API and returns 5 
    variables 1)a list of authors, 2) a string the article title, 3) year 
    published, 4) Name of Journal holding publication, 5) A mostly fully 
    constructed citation, it returns zeroes for everything if ScopusID is 0"""
    if ScopusID == 0:
        Year='0'
        Journal = '0'
        citation = '0'
    else:
        
        articleURL = 'http://api.elsevier.com/content/abstract/scopus_id/{'+str(ScopusID)+'}'
        response=requests.get(articleURL, headers=config.apiKey)
        data= response.json()
        authors = data['abstracts-retrieval-response']['authors']['author']
        coredata = data['abstracts-retrieval-response']['coredata']
        authList = ''
        for k in range(len(authors)): 
            name = authors[k]['preferred-name']['ce:indexed-name']
            if k == (len(authors)-1):
                authList=authList+name
            else:
                authList= authList+name+', '
        if 'prism:coverDate' in coredata:
            Year=coredata['prism:coverDate'][0:4]
        else:
            Year=''

        if 'prism:publicationName' in coredata:
            Journal = coredata['prism:publicationName']
        else:
            Journal = ''

        if 'prism:issueIdentifier' in coredata:
            issue = coredata['prism:issueIdentifier']
        else:
            issue = ''
    
        if 'dc:title' in coredata:
            title = coredata['dc:title']
        else:
            title = ''
    
        if 'prism:volume' in coredata:
            volume = coredata['prism:volume']
        elif 'prism:issn' in coredata: 
            volume =coredata['prism:issn']
        else:
            volume = '' 
        if 'prism:doi' in coredata:
            doi=coredata['prism:doi']
        else: 
            doi=''

    citation = authList + '. '+Year+'. '+title+'. '+Journal+'. '+volume+'('+issue+') DOI:'+doi
        
    return authList, title, Year, Journal, citation

def getCitedRefsJournalName(ScopusID):
    """ This function takes a scopus ID (i.e. the unique id number for an article
    in Scopus) and query's the Scoupus API to get journal titles for articles
    cited in the reference section of the paper. The function returns a list 
    of the journal articles"""
    journalsCitedList = []
    paperID = ScopusID
    URL = 'http://api.elsevier.com/content/abstract/scopus_id/{'+str(paperID)+'}'
    response=requests.get(URL, headers=config.apiKey, params={'view':'REF', })
    data = response.json()
    references=data['abstracts-retrieval-response']['references']['reference']
    TotalRefCount = int(data['abstracts-retrieval-response']['references']['@total-references'])
    RefsRetrieved = len(references)
    for i in range(len(references)):
        journalsCitedList.append(data['abstracts-retrieval-response']['references']['reference'][i]['sourcetitle'])
    while TotalRefCount != RefsRetrieved:
        URL = 'http://api.elsevier.com/content/abstract/scopus_id/{'+str(paperID)+'}'
        response=requests.get(URL, headers=config.apiKey, params={'view':'REF', 'startref':RefsRetrieved+1})
        data = response.json()
        references=data['abstracts-retrieval-response']['references']['reference']        
        RefsRetrieved+=len(references)
        for j in range(len(references)):
            journalsCitedList.append(data['abstracts-retrieval-response']['references']['reference'][j]['sourcetitle'])
    return journalsCitedList


def GetPaperIDsFromAuthID(authID):
    """This function uses Author Id to query Scopus API and returns a list of
    ScopusID values assigned to each paper the author has in Scopus, if author
    ID is 0 then the list returned will just have one 0 value"""
    if authID == '0':
        scopeList = [0]
    else:
        searchURL = 'http://api.elsevier.com/content/search/scopus?query=AU-ID('+authID+')&field=dc:identifier&count=200'
        response=requests.get(searchURL, headers=config.apiKey)
        data = response.json()
        totalPapers=int(data['search-results']['opensearch:totalResults'])
        scopeList =[x['dc:identifier'].split(':')[1] for x in data['search-results']['entry']]
        PapersRetrieved=len(scopeList)
        while totalPapers != PapersRetrieved:
            searchURL = 'http://api.elsevier.com/content/search/scopus?query=AU-ID('+authID+')&field=dc:identifier&count=200&start='+str(PapersRetrieved)
            response=requests.get(searchURL, headers=config.apiKey)
            data = response.json()
            addList =[x['dc:identifier'].split(':')[1] for x in data['search-results']['entry']]
            scopeList+=addList
            PapersRetrieved += len(addList)
    return scopeList

