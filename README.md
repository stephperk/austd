# Austd
This is a Twilio/Flask application built to estimate the probability that a news article is "fake".
It also utilizes Bing's Spell Checker API to get number of typos and add it as a feature! The algorithm
is a Random Forest Classifier based on the sklearn open source code!!

...A product of the Global AI Hackathon NYC 2017...

## What Austd _Really_ Is

We don't want to call news "fake" or "real". This tool is really just a way for you to check the
_esimated reliability_ of your news article. It gives you a guess as to whether or not you can rely on it
along with a percentage of confidence. At the end of the day, you have to decide whether or not to
let your confirmation bias take you over.

### The Model

Our model is based on a few key features that are derived from the text and the title. It is _not_ based on
the text directly. This is on purpose, because then we fear that the topics within the text itself will have
more weight than the other features in terms of the wordsmithery of the text. This proved to be quite accurate
in the Random Forest model (see the notebook). Please contact us for more advice on future directions, however.
Our true knowledge exists in that we know that we know nothing!

As an added feature, we used OpenSources, a professionally curated list, to tag sources that have been previously identified as fake, false, extremely bias, generally satiric, and more.
Detailed methods for tagging are on: http://www.opensources.co/

## How To Use It

Go to our page! (this section will be updated once we have a link.)

Or text it! (this will be updated too.)

Enter a url to a news link!

You will get your answer back! plus a cute gif :)

## Future Directions

- Improve/enlarge training dataset. it is currently biased by the fact that the "real" news is all British.

- Develop a Human-in-the-loop role so that *verified* contributors can upvote or downvote articles.

- Include more features?

## Citations

Continuous Curation: [![OpenSources Data](https://img.shields.io/badge/Data-OpenSources-blue.svg)](http://opensources.co)

[Subjectivity Lexicon](http://mpqa.cs.pitt.edu/lexicons/subj_lexicon/) from the CS department at Pitt.

["Fake" News](https://www.kaggle.com/mrisdal/fake-news#_=_) from Kaggle.

[VADER](http://comp.social.gatech.edu/papers/icwsm14.vader.hutto.pdf) algorithm used to measure neutrality in titles.

["Real" news](http://mklab.iti.gr/project/web-news-article-dataset) from Multimedia Knowledge and Social Media Analytics Laboratory.
