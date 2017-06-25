import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegressionCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.cross_validation import train_test_split
from sklearn import metrics
from sklearn.cross_validation import cross_val_score
from patsy import dmatrices
import requests
import json
from json import JSONDecodeError
import urllib
from newspaper import Article
import re
from nltk.tokenize import word_tokenize
from stop_words import get_stop_words
from nltk.sentiment import vader
from newspaper.article import ArticleException

class GoldStandard:

        def __init__(self):

            #read in data
            self.data = pd.DataFrame.from_csv('data/training_data.csv')

            #get rid of NaNs
            replacements = {
               'title_neutrality': {
                  None: np.mean(self.data.title_neutrality)
            }}

            self.data= self.data.replace(replacements)

            #set seed
            np.random.seed(10101010)

            #read in subjectivity data
            self.subj_frame = self._read_in_subj_frame()

            #get stop words
            self.stop_words = get_stop_words('en')

            #create numeric labels
            labels_to_vec = np.where(self.data.fake_or_real == 'fake', 1, 0)
            self.data['label'] = labels_to_vec

            #instantiate model
            self.model = RandomForestClassifier()

            #set up vectors
            self.y, self.X = dmatrices('label ~ typo_counts + text_subjectivity + text_positivity + text_negativity + title_neutrality',
                             self.data, return_type="dataframe")

            #flatten y to vector
            self.y = np.ravel(self.y)

            #fit model
            self.model.fit(self.X, self.y)

            #read in sources for mostly biased/fake news
            self.sources = pd.DataFrame.from_csv('data/sources.csv',index_col=None)
            self.sources.columns = ['url'] + list(self.sources.columns)[1:]

            #account for human crap
            self.sources.url = [word.strip() for word in self.sources.url]
            self.sources.type = [word.strip() for word in self.sources.type]


        def predict_fakeness(self,url):

            ###### do stuff to create final vector ######

            #create article object
            try:
                article = Article(url,language='en')

            except ArticleException:
                return('not found')

            article.download()
            article.parse()

            #get number of typos
            n_typos = self._get_num_typos(article.text)

            #get subjectivity scores
            subjectivity_scores = self._get_subj_scores(article.text)

            #get vader intensity of title
            title_subjectivity_score = self._get_title_subjectivity(article.title)

            #create final vector
            #label is just a placeholder
            features_dict = {"typo_counts": n_typos,
                             "text_subjectivity": subjectivity_scores['text_subjectivity'],
                             "text_positivity": subjectivity_scores['text_positivity'],
                             "text_negativity": subjectivity_scores["text_negativity"],
                             "title_neutrality": title_subjectivity_score,
                             "label": 1}

            input_y, input_X = dmatrices(
                'label ~ typo_counts + text_subjectivity + text_positivity + text_negativity + title_neutrality',
                features_dict, return_type="dataframe")
            input_y = np.ravel(input_y)

            #get predictions and probabilities
            prediction = self.model.predict(input_X)
            probability = self.model.predict_proba(input_X)

            #check for matching with list of biased/fake sources
            fake_matches = self._check_against_sources(article.source_url)

            '''this changes the probability to be for sure fake if the site was tagged as fake'''
            if 'fake' in str(fake_matches).strip():
                prediction = [1.0]
                probability = [0.0, 1.0]
                self._add_data_to_training(features_dict)

            '''Set up stuff to return info on whether it matched a bias type'''

            #returning a value of 1 = too biased to trust, 0 = probably trustworthy
            return {"prediction": prediction, "probability": probability,
                    "tagged_bias":fake_matches}

        def _read_in_subj_frame(self):

            # read in subjectivity data
            with open('data/subjectivity_clues_hltemnlp05/subjclueslen1-HLTEMNLP05.tff') as tff:
                lines = tff.readlines()

            tff.close()

            subj_frame = pd.DataFrame(columns=['type', 'len', 'word1', 'pos1', 'stemmed1', 'polarity', 'priorpolarity'],
                                      index=range(len(lines)))

            i = 0
            for line in lines:

                row = []

                line = line.strip()
                line_items = line.split(sep=' ')

                item_dict = {}

                for item in line_items:

                    if '=' in item:
                        pref_suff = item.split('=')

                        item_dict[pref_suff[0]] = pref_suff[1]

                    for col in subj_frame.columns:
                        if col not in list(item_dict.keys()):
                            item_dict[col] = None

                try:
                    subj_frame.loc[i] = item_dict
                    i += 1
                except ValueError as e:
                    print(line, e)
                    break

            subj_frame.word1 = [word.strip() for word in subj_frame.word1]

            return(subj_frame)


        def _get_num_typos(self, article_text,api_key='4d1f19cfa84c47a7851a1dd01e72443f'):

            #set up parameters
            headers = {
                # Request headers
                'Content-Type': 'application/x-www-form-urlencoded',
                'Ocp-Apim-Subscription-Key': api_key,
            }

            params = urllib.parse.urlencode({
                # Request parameters
                #it only can do a limited number of characters so we will
                #just look at the first 1000 chars
                'text': article_text[:1000],
            })

            try:
                r = requests.post('https://api.cognitive.microsoft.com/bing/v5.0/spellcheck?%s' % params, "{body}",
                                  headers=headers)
                data = json.loads(r.text)
                return(len(data['flaggedTokens']))

            except (KeyError, JSONDecodeError):
                return(0)

        def _get_subj_scores(self, article_text):

            subj_score = 0
            neg_score = 0
            pos_score = 0

            text = str(article_text)

            tokens = word_tokenize(text)
            tokens = [token for token in tokens if token not in self.stop_words]

            intersection = []
            for token in tokens:
                if token.strip() in list(self.subj_frame.word1):
                    intersection.append(token.strip())
                    # print(token.strip())

            for item in intersection:

                subj_data = self.subj_frame.loc[self.subj_frame.word1 == str(item)]

                if 'strongsubj' in subj_data.type:
                    subj_score += 1

                else:
                    subj_score += .5

                if len(subj_data.priorpolarity) > 1:
                    pol_list = list(subj_data.priorpolarity)
                    pol_list = [s.strip() for s in pol_list]

                else:
                    pol_list = str(subj_data.priorpolarity).strip()

                if 'both' in pol_list:

                    neg_score += .5
                    pos_score += .5

                elif 'negative' in pol_list:
                    neg_score += 1

                elif 'positive' in pol_list:
                    pos_score += 1

                elif 'weakneg' in pol_list:
                    neg_score += .5

            subj_score = subj_score / (len(tokens) + 1)
            pos_score = pos_score / (len(tokens) + 1)
            neg_score = neg_score / (len(tokens) + 1)

            return({ "text_subjectivity": subj_score,
                     "text_positivity": pos_score,
                     "text_negativity": neg_score})



        def _get_title_subjectivity(self,article_title):

            analyzer = vader.SentimentIntensityAnalyzer()

            scores = analyzer.polarity_scores(str(article_title))

            return(scores['neu'])

        #returns the row from sources that matches the site website
        def _check_against_sources(self, article_url):

            #check for http
            if re.match(r'^https?://',str(article_url)):
                article_url = re.sub(r'^https?://','',article_url)

            #check for www
            if re.match(r'^www\.',str(article_url)):
                article_url = re.sub(r'^www\.','',article_url)

            for url in self.sources.url:
                if url.strip() in str(article_url) or str(article_url) in url.strip():
                    if len(str(article_url)) > 2:
                        print('matched')
                        return(self.sources.loc[self.sources.url == str(article_url).strip(),]['type'][0])
                    else:
                        return None

                else:
                    return None

        def _add_data_to_training(self, dict_to_add):

            data = self.data.append(dict_to_add)

            #set up vectors
            self.y, self.X = dmatrices('label ~ typo_counts + text_subjectivity + text_positivity + text_negativity + title_neutrality',
                             self.data, return_type="dataframe")

            #flatten y to vector
            self.y = np.ravel(self.y)

            #fit model
            self.model.fit(self.X, self.y)

            return None
