# -*- coding: utf8 -*-

# Copyright (C) <2018>  <MAGNIER Paul>

#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License.

#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.

#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.



from datetime import *
import settings
import json, sys, requests
import log
import dateparser #pip install dateparser
from difflib import SequenceMatcher
from newspaper import Article
import importlib



class newsHandler:
    
    def __init__(self):
        
        self.urls = []

    # News API : https://newsapi.org/docs/get-started
    # Article : https://newspaper.readthedocs.io/en/latest/
    # Beware Newspaper3k use python 3

    # ------------ Mains methodes --------------- 

    def newsFetch(self, slots, intentname, type=None):
        
        q = ''
        sources = ''
        domains = ''
        category = ''
        from_parameter = ''
        to = ''

        sourceRaw = ''
        text = ''

        #print("urls : ")
        #print(self.urls)

        if slots.get('newsApiSources',None):
            sourceRaw = slots.get('newsApiSources',None).get('value','')

        print(sourceRaw)
        if len(self.urls) != 0 and sourceRaw != "":
            url = self.mostRelevantUrl(self, sourceRaw)
            article = Article(url)
            article.download()
            article.parse()

            #article.download()
            #article.parse()
            text = 'Voici votre article : ' + article.text

        else:
            self.urls = []

            country = 'country={}&'.format('fr')
            sortBy = 'sortBy={}&'.format('publishedAt')
            language = 'language={}&'.format('fr')
            pageSize = 'pageSize={}&'.format('5')
            page = 'page={}&'.format('1')
            
            if slots.get('querry',None):
                value = slots.get('querry',None).get('value','')
                q = 'q={}&'.format(value)
            
            if slots.get('newsApiSources',None):
                value = slots.get('newsApiSources',None).get('value','')
                sources = 'sources={}&'.format(value)
        
            if slots.get('newsApiCategory',None):
                value = slots.get('newsApiCategory',None).get('value','')
                category = 'category={}&'.format(value)  #business entertainment general health science sports technology
                if not type:
                    type = 'top-headlines'
                    
            if slots.get('newsApiCountry',None):
                value = slots.get('newsApiCountry',None).get('value','')
                if value in COUNTRY_CODE:
                    country = 'country={}&'.format(value)
                else:
                    country = ''
                    if q == '':
                        q = 'q={}&'.format(CODE_COUTNRY[value])
                if not type:
                    type = 'top-headlines'
                    
            if slots.get('newsApiSortBy',None):
                value = slots.get('newsApiSortBy',None).get('value','')
                sortBy = 'sortBy={}&'.format('publishedAt') # relevancy, popularity, publishedAt(default)

            if not type:
                type = 'everything?'

            timeMin = None
            timeMax = None
            if slots.get("start_datetime", None):
                dateAndGranularity = Date.extract_date(self, slots, 'False')
                if dateAndGranularity.get('dateStart',None) == dateAndGranularity.get('dateTo',None):
                    timeMin = dateAndGranularity.get('dateStart',None)
                    from_parameter = 'from={}&'.format(timeMin)
                    timeMax = None
                    to = ''
                    granularity = dateAndGranularity.get('granularity',None)
                else:
                    timeMin = dateAndGranularity.get('dateStart',None)
                    from_parameter = 'from={}&'.format(timeMin)
                    timeMax = dateAndGranularity.get('dateTo',None)
                    to = 'to={}&'.format(timeMin)
                    granularity = dateAndGranularity.get('granularity',None)
        
            variables = {'q':q, 'sources':sources, 'domains':domains, 'category':category, 'from_parameter':from_parameter, 'to':to, 'country':country, 'sortBy':sortBy, 'language':language, 'pageSize':pageSize, 'page':page}
            
            text = newsHandler.requestsNews(self, variables, type)

        #print("urls : ")
        #print(self.urls)

        return text
    
    @staticmethod
    def requestsNews(self, variables, type):
        
        q = variables.get('q','')
        sources = variables.get('sources','')
        domains = variables.get('domains','') 
        category = variables.get('category','') 
        from_parameter = variables.get('from_parameter','') 
        to = variables.get('to','') 
        country = variables.get('country','') 
        sortBy = variables.get('sortBy','') 
        language = variables.get('language','') 
        pageSize = variables.get('pageSize','') 
        page = variables.get('page','') 
        
        apiKey = 'apiKey={}'.format(settings.NEWS_API)
        
        if type == 'top-headlines':
            #This endpoint provides live top and breaking headlines for a country, specific category in a country, single source, or multiple sources. You can also search with keywords. Articles are sorted by the earliest date published first. This endpoint is great for retrieving headlines for display on news tickers or similar.
            
            if country == '' or category == '' or sources == '' or q == '':
                country = 'country={}&'.format('fr')

            url = 'https://newsapi.org/v2/top-headlines?' + country + category + sources + q + pageSize + page + apiKey
            
        
        elif type == 'everything?':
            #Search through millions of articles from over 30,000 large and small news sources and blogs. This includes breaking news as well as lesser articles. This endpoint suits article discovery and analysis, but can be used to retrieve articles for display, too.
            
            if category == '' or sources == '' or q == '':
                q =  'q={}&'.format('France')
            
            url = 'https://newsapi.org/v2/everything?'+ q + sources + domains + from_parameter + to + language + sortBy + pageSize + page + apiKey
            
        log.info(url)
        reponse = requests.get(url)
        reponseToProcess = reponse.json()
        text = newsHandler.responseToText(self, reponseToProcess, variables, type)
        
        #print text
        return text
    
    @staticmethod
    def responseToText(self, reponse, variables, type):
        
        #importlib.reload(sys)
        #sys.setdefaultencoding('utf8')
        
        text = ''
        status = ''
        articles = None
        self.urls = []
        
        q = variables.get('q','').replace("q=","")
        sources = variables.get('sources','').replace("sources=","")
        category = variables.get('category','').replace("category=","")
        country = variables.get('country','').replace("country=","")

        q.replace("&","")
        sources.replace("&","")
        category.replace("&","")
        country.replace("&","")
        
        if reponse.get('status', None):
            status = reponse.get('status', None)
        
        if q != '' or sources != '' or category != '':
            sur = ''
            if q != '':
                sur = 'sur ' + q
            elif sources != '':
                sur = 'depuis la soruce ' + sources
            elif category != '':
                sur = 'sur la catégorie ' + category
            
            if type == 'everything?':
                text = 'Voici les résultats sur votre recherche {}...'.format(sur)
            else:
                text = 'Voici les derniers gros titres {}...'.format(sur)
        else:
            text = 'Les 5 derniers gros titres en France sont les suivants : '
        
        if status == 'error':
            text = 'La récupération des informations a échoué.'
            return text
        else:
            articles = reponse.get('articles', None) #json.loads()
            for article in articles:
                articleText = ''
                author = article.get('author','')
                if article.get('source',None):
                    source = article.get('source',None).get('name','')
                    source = self.supprDomain(source)
                else:
                    source = '' 
                titre = article.get('title','')
                description = article.get('description','')
                if "..." in description:
                    description = description + " ."
                url = article.get('url','')
                
                articleText = 'Article du {}... Intitulé : {}... {}'.format(source, titre, description)
                
                text = text + articleText + "\n"
                
                self.urls.append({'titre':titre,'url':url, 'source':source})

            text = self.formatJSONText(text)

            return text
            
        return text


    # ------------ Annexes methodes --------------- 

    @staticmethod
    def supprDomain(text):
        modifyText = ""
        modifyText = text.replace(".fr", "")
        modifyText = modifyText.replace(".com", "")
        modifyText = modifyText.replace(".net", "")
        modifyText = modifyText.replace(".org", "")

        return modifyText

    @staticmethod
    def formatJSONText(text):

        modifyText = ""
        modifyText = text.replace('\\', "\\\\")
        modifyText = modifyText.replace('"', '\\"')
        #modifyText = modifyText.replace("\n", "")

        return modifyText

    
    @staticmethod
    def similarities(a, b):
        return SequenceMatcher(None, a, b).ratio()

    @staticmethod
    def mostRelevantUrl(self, sourceRaw):

        maxRatio = 0.5
        url = ''

        for source in self.urls:
            #print(maxRatio)
            if self.similarities(sourceRaw, source['source']) > maxRatio:
                #print(sourceRaw, source['source'])
                #print(self.similarities(sourceRaw, source['source']))
                maxRatio = self.similarities(sourceRaw, source['source'])
                url = source['url']
                
        
        print("url")
        print(url)  
        return url


        # ------------ Annexes var --------------

COUNTRY_CODE = ["ae","ar","at","au","be","bg",
"br","ca","ch","cn","co","cu","cz","de","eg",
"fr","gb","gr","hk","hu","id","ie","il","in",
"it","jp","kr","lt","lv","ma","mx","my","ng",
"nl","no","nz","ph","pl","pt","ro","rs","ru",
"sa","se","sg","si","sk","th","tr","tw","ua",
"us","ve","za","AE","AR","AT","AU","BE","BG",
"BR","CA","CH","CN","CO","CU","CZ","DE","EG",
"FR","GB","GR","HK","HU","ID","IE","IL","IN",
"IT","JP","KR","LT","LV","MA","MX","MY","NG",
"NL","NO","NZ","PH","PL","PT","RO","RS","RU",
"SA","SE","SG","SI","SK","TH","TR","TW","UA",
"US","VE","ZA",]

CODE_COUTNRY = {"AD":"Andorre",
"AE":"Émirats arabes unis",
"AF":"Afghanistan",
"AG":"Antigua-et-Barbuda",
"AI":"Anguilla",
"AL":"Albanie",
"AM":"Arménie",
"AO":"Angola",
"AQ":"Antarctique",
"AR":"Argentine",
"AS":"Samoa américaines",
"AT":"Autriche",
"AU":"Australie",
"AW":"Aruba",
"AX":"Îles Åland",
"AZ":"Azerbaïdjan",
"BA":"Bosnie-Herzégovine",
"BB":"Barbade",
"BD":"Bangladesh",
"BE":"Belgique",
"BF":"Burkina Faso",
"BG":"Bulgarie",
"BH":"Bahreïn",
"BI":"Burundi",
"BJ":"Bénin",
"BL":"Saint-Barthélemy",
"BM":"Bermudes",
"BN":"Brunei",
"BO":"Bolivie",
"BQ":"Pays-Bas caribéens",
"BR":"Brésil",
"BS":"Bahamas",
"BT":"Bhoutan",
"BV":"Île Bouvet",
"BW":"Botswana",
"BY":"Biélorussie",
"BZ":"Belize",
"CA":"Canada",
"CC":"Îles Cocos",
"CD":"République démocratique du Congo",
"CF":"République centrafricaine",
"CG":"République du Congo",
"CH":"Suisse",
"CI":"Côte d'Ivoire",
"CK":"Îles Cook",
"CL":"Chili",
"CM":"Cameroun",
"CN":"Chine",
"CO":"Colombie",
"CR":"Costa Rica",
"CU":"Cuba",
"CV":"Cap-Vert",
"CW":"Curaçao",
"CX":"Île Christmas",
"CY":"Chypre (pays)",
"CZ":"Tchéquie",
"DE":"Allemagne",
"DJ":"Djibouti",
"DK":"Danemark",
"DM":"Dominique",
"DO":"République dominicaine",
"DZ":"Algérie",
"EC":"Équateur (pays)",
"EE":"Estonie",
"EG":"Égypte",
"EH":"République arabe sahraouie démocratique",
"ER":"Érythrée",
"ES":"Espagne",
"ET":"Éthiopie",
"FI":"Finlande",
"FJ":"Fidji",
"FK":"Malouines",
"FM":"Micronésie (pays)",
"FO":"Îles Féroé",
"FR":"France",
"GA":"Gabon",
"GB":"Royaume-Uni",
"GD":"Grenade (pays)",
"GE":"Géorgie (pays)",
"GF":"Guyane",
"GG":"Guernesey",
"GH":"Ghana",
"GI":"Gibraltar",
"GL":"Groenland",
"GM":"Gambie",
"GN":"Guinée",
"GP":"Guadeloupe",
"GQ":"Guinée équatoriale",
"GR":"Grèce",
"GS":"Géorgie du Sud-et-les îles Sandwich du Sud",
"GT":"Guatemala",
"GU":"Guam",
"GW":"Guinée-Bissau",
"GY":"Guyana",
"HK":"Hong Kong",
"HM":"Îles Heard-et-MacDonald",
"HN":"Honduras",
"HR":"Croatie",
"HT":"Haïti",
"HU":"Hongrie",
"ID":"Indonésie",
"IE":"Irlande (pays)",
"IL":"Israël",
"IM":"Île de Man",
"IN":"Inde",
"IO":"Territoire britannique de l'océan Indien",
"IQ":"Irak",
"IR":"Iran",
"IS":"Islande",
"IT":"Italie",
"JE":"Jersey",
"JM":"Jamaïque",
"JO":"Jordanie",
"JP":"Japon",
"KE":"Kenya",
"KG":"Kirghizistan",
"KH":"Cambodge",
"KI":"Kiribati",
"KM":"Comores (pays)",
"KN":"Saint-Christophe-et-Niévès",
"KP":"Corée du Nord",
"KR":"Corée du Sud",
"KW":"Koweït",
"KY":"Îles Caïmans",
"KZ":"Kazakhstan",
"LA":"Laos",
"LB":"Liban",
"LC":"Sainte-Lucie",
"LI":"Liechtenstein",
"LK":"Sri Lanka",
"LR":"Liberia",
"LS":"Lesotho",
"LT":"Lituanie",
"LU":"Luxembourg (pays)",
"LV":"Lettonie",
"LY":"Libye",
"MA":"Maroc",
"MC":"Monaco",
"MD":"Moldavie",
"ME":"Monténégro",
"MF":"Saint-Martin",
"MG":"Madagascar",
"MH":"Îles Marshall (pays)",
"MK":"République de Macédoine (pays)",
"ML":"Mali",
"MM":"Birmanie",
"MN":"Mongolie",
"MO":"Macao",
"MP":"Îles Mariannes du Nord",
"MQ":"Martinique",
"MR":"Mauritanie",
"MS":"Montserrat",
"MT":"Malte",
"MU":"Maurice (pays)",
"MV":"Maldives",
"MW":"Malawi",
"MX":"Mexique",
"MY":"Malaisie",
"MZ":"Mozambique",
"NA":"Namibie",
"NC":"Nouvelle-Calédonie",
"NE":"Niger",
"NF":"Île Norfolk",
"NG":"Nigeria",
"NI":"Nicaragua",
"NL":"Pays-Bas",
"NO":"Norvège",
"NP":"Népal",
"NR":"Nauru",
"NU":"Niue",
"NZ":"Nouvelle-Zélande",
"OM":"Oman",
"PA":"Panama",
"PE":"Pérou",
"PF":"Polynésie française",
"PG":"Papouasie-Nouvelle-Guinée",
"PH":"Philippines",
"PK":"Pakistan",
"PL":"Pologne",
"PM":"Saint-Pierre-et-Miquelon",
"PN":"Îles Pitcairn",
"PR":"Porto Rico",
"PS":"Palestine",
"PT":"Portugal",
"PW":"Palaos",
"PY":"Paraguay",
"QA":"Qatar",
"RE":"La Réunion",
"RO":"Roumanie",
"RS":"Serbie",
"RU":"Russie",
"RW":"Rwanda",
"SA":"Arabie saoudite",
"SB":"Salomon",
"SC":"Seychelles",
"SD":"Soudan",
"SE":"Suède",
"SG":"Singapour",
"SH":"Sainte-Hélène, Ascension et Tristan da Cunha",
"SI":"Slovénie",
"SJ":"Svalbard et ile Jan Mayen",
"SK":"Slovaquie",
"SL":"Sierra Leone",
"SM":"Saint-Marin",
"SN":"Sénégal",
"SO":"Somalie",
"SR":"Suriname",
"SS":"Soudan du Sud",
"ST":"Sao Tomé-et-Principe",
"SV":"Salvador",
"SX":"Saint-Martin",
"SY":"Syrie",
"SZ":"Swaziland",
"TC":"Îles Turques-et-Caïques",
"TD":"Tchad",
"TF":"Terres australes et antarctiques françaises",
"TG":"Togo",
"TH":"Thaïlande",
"TJ":"Tadjikistan",
"TK":"Tokelau",
"TL":"Timor oriental",
"TM":"Turkménistan",
"TN":"Tunisie",
"TO":"Tonga",
"TR":"Turquie",
"TT":"Trinité-et-Tobago",
"TV":"Tuvalu",
"TW":"Taïwan / (République de Chine (Taïwan))",
"TZ":"Tanzanie",
"UA":"Ukraine",
"UG":"Ouganda",
"UM":"Îles mineures éloignées des États-Unis",
"US":"États-Unis",
"UY":"Uruguay",
"UZ":"Ouzbékistan",
"VA":"Saint-Siège (État de la Cité du Vatican)",
"VC":"Saint-Vincent-et-les-Grenadines",
"VE":"Venezuela",
"VG":"Îles Vierges britanniques",
"VI":"Îles Vierges des États-Unis",
"VN":"Viêt Nam",
"VU":"Vanuatu",
"WF":"Wallis-et-Futuna",
"WS":"Samoa",
"YE":"Yémen",
"YT":"Mayotte",
"ZA":"Afrique du Sud",
"ZM":"Zambie",
"ZW":"Zimbabwe",}

"""status
string
If the request was successful or not. Options: ok, error. In the case of error a code and message property will be populated.

totalResults
int
The total number of results available for your request. Only a limited number are shown at a time though, so use the page parameter in your requests to page through them.

articles
array[article]
The results of the request.

source
object
The identifier id and a display name name for the source this article came from.

author
string
The author of the article

title
string
The headline or title of the article.

description
string
A description or snippet from the article.

url
string
The direct URL to the article.

urlToImage
string
The URL to a relevant image for the article.

publishedAt
string
The date and time that the article was published, in UTC (+000)"""
