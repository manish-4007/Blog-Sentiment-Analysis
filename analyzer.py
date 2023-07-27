import pandas as pd

import logging
import re, os
from nltk import word_tokenize,sent_tokenize
from textstat.textstat import textstatistics
import string, re, ast

input = pd.read_excel('./Input.xlsx')
input = input.set_index('URL_ID') 
    
#----------------------------------- Text Analysis on this article

# 1.1 Cleaning using Stopwords Lists

#Combining all the stopwords from to folder into a list
stopwords = []
for i in os.listdir('Stopwords'):
    with open(os.getcwd()+'/Stopwords/' +i, "r") as file:
        lines = file.readlines()
        stopwords += lines
        file.close()
stopwords = [s.replace('\n', '') for s in stopwords]


#Check for the stopword in the article and remove it 
stopwords = [s.lower() for s in stopwords]

def remove_stopwords(text):
    text = text.split(" ")
    c=[]
    for i in text:
        if i.lower() not in stopwords:
            c.append(i.lower())
    return  " ".join(c)


# 1.2 Creating a dictionary of Positive and Negative words
def pos_neg_dir():
    pos = []
    neg = []
    for i in os.listdir('MasterDictionary'):
        with open(os.getcwd()+'/MasterDictionary/' +i, "r") as file:
            if i == "positive-words.txt":
                pos = file.readlines()
                file.close()
            elif i == "negative-words.txt":            
                neg = file.readlines()
                file.close()
    pos = [s.replace('\n', '') for s in pos]
    neg = [s.replace('\n', '') for s in neg]
    print("Positive = ",len(pos),"Negative = ", len(neg))

    pos = remove_stopwords(" ".join(pos)).split()
    neg= remove_stopwords(" ".join(neg)).split()
    print("\nAfter removing stopwords : \nPositive = ",len(pos),"negative = ",len(neg))

    #Creating dictionary for positve and negative
    return {"Positive": pos, "Negative": neg}

pos_neg = pos_neg_dir()


def preprocess_text(text):
    pre_processed = remove_stopwords(text)
    return pre_processed.translate(str.maketrans('', '', string.punctuation))

def complex_words(text): 
    words = word_tokenize(text)
    sentences = sent_tokenize(text)
    
    diff_words_set = set()
     
    for word in words:
        syllable_count = textstatistics().syllable_count(word)
        if word not in stopwords and syllable_count >= 2:
            diff_words_set.add(word)
 
    return len(diff_words_set)

def average_words(text):
    sentences = sent_tokenize(text)
    word_count=0
    for sent in sentences:
        word_count+= len(word_tokenize(sent))
    return word_count/len(sentences)

def count_personal_pronouns(text):
    # Define the regex pattern to match the personal pronouns
    pattern = r'\b(I|we|my|ours|us)\b'
    
    # Find all matches using the regex pattern
    matches = re.findall(pattern, text, re.IGNORECASE)
    matches = [i for i in matches if i != 'US']
    
    # Return the count of personal pronouns
    return len(matches)

#------------- Pre-processing of the article

# import the text-article one-by-one from the files and do pre-processing:

def read_aticle(file_name):
    
    with open(os.getcwd()+'/files/' +file_name, "r", encoding='utf-8') as file:
        data = file.read()
        blog = ast.literal_eval(data)
        file.close()
    return blog

for i in os.listdir('files'):
    id = int(i.split('.')[0])

    Positive_Score = 0
    Negative_Score = 0
    Polarity_Score = 0
    Subjectivity_Score = 0
    Avereage_Sentence_Length = 0
    per_complex_word = 0
    fog_index = 0
    Average_num_words = 0
    Complex_word_count = 0
    Word_count = 0
    syllable_count_per_word = 0
    pronoun_count = 0
    Avg_word_length = 0


    blog = read_aticle(i)
    print("\n ----------------------------------------------------------------------------------------")
    print(f"\n Analysing the article id [{id}] - {blog['Title']}\n ")
    print(" ----------------------------------------------------------------------------------------\n")

    if len(blog["Article"])> 0:
        pre_processed_text = preprocess_text(blog['Article'])

    # 1.3 Extracting Derived variables
        # Tokenize the text and do sentiment analysis on each word
        text_token = word_tokenize(pre_processed_text)
        pos=0
        neg = 0
        for w in text_token:
            if w in pos_neg["Positive"]:
                pos+=1
            elif w in pos_neg["Negative"]:
                neg-=1

    #------------------------------------Derived Variables
        Positive_Score = +pos
        Negative_Score = -neg
        Polarity_Score = (Positive_Score-Negative_Score)/((Positive_Score+Negative_Score) + 0.000001)
        Subjectivity_Score = (Positive_Score+Negative_Score)/((len(text_token))+0.000001)

        #2.  Analysis of Readiability
        text = blog["Article"]
        word_count = len(word_tokenize(text))
        sent_count = len(sent_tokenize(text))
        
        Avereage_Sentence_Length = word_count/sent_count 
        per_complex_word = complex_words(text)/word_count 
        fog_index = 0.4*(Avereage_Sentence_Length+per_complex_word)
        
    #------------ 3.  Average Number of Words Per Sentence
        Average_num_words = average_words(text)

    #------------ 4.  Complex Word Count
        Complex_word_count = complex_words(text)

    #------------ 5.   Word Count
        words_tokens = word_tokenize(pre_processed_text)
        Word_count = len(words_tokens)

    #------------ 6.  Syllable Count Per Word

        syllable_count = 0
        for w in words_tokens:
            syllable_count += textstatistics().syllable_count(w)
            
        syllable_count_per_word =  syllable_count/Word_count

    #------------ 7. Personal Pronouns
        pronoun_count = count_personal_pronouns(text)

    #------------ 8. Average Word Length
        Avg_word_length = len(pre_processed_text)/word_count
        
    print("\nDerived Variables are : -----------\n\nPositive_Score: ",Positive_Score)
    print("Negative_Score: ",Negative_Score)
    print("Polarity_Score: ",Polarity_Score)
    print("Subjectivity_Score: ",Subjectivity_Score)
    print("Avereage_Sentence_Length: ",Avereage_Sentence_Length)
    print("per_complex_word: ",per_complex_word)
    print("fog_index: ",fog_index)
    print("Average_num_words: ",Average_num_words)
    print("Complex_word_count: ",Complex_word_count)
    print("Word_count: ",Word_count)
    print("syllable_count_per_word: ",syllable_count_per_word)
    print("pronoun_count: ", pronoun_count)
    print("Avg_word_length: ", Avg_word_length)

    # Save the derived variable into output file
    # output = pd.DataFrame()

    input.loc[id,"POSITIVE SCORE"] = Positive_Score
    input.loc[id,"NEGATIVE SCORE"] = Negative_Score
    input.loc[id,"POLARITY SCORE"] = Polarity_Score
    input.loc[id,"SUBJECTIVITY SCORE"] = Subjectivity_Score
    input.loc[id,"AVG SENTENCE LENGTH"] = Avereage_Sentence_Length
    input.loc[id,"PERCENTAGE OF COMPLEX WORDS"] = per_complex_word
    input.loc[id,"FOG INDEX"] = fog_index
    input.loc[id,"AVG NUMBER OF WORDS PER SENTENCE"] = Average_num_words
    input.loc[id,"COMPLEX WORD COUNT"] = Complex_word_count
    input.loc[id,"WORD COUNT"] = Word_count
    input.loc[id,"SYLLABLE PER WORD"] = syllable_count_per_word
    input.loc[id,"PERSONAL PRONOUNS"] = pronoun_count
    input.loc[id,"AVG WORD LENGTH"] = Avg_word_length
    print(input.loc[id])
 
print(input.head(15))
input.to_excel("Output Data Structure.xlsx")