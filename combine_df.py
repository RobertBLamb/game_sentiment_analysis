import pandas as pd
import os.path

from transformers import AutoTokenizer
from transformers import AutoModelForSequenceClassification
from scipy.special import softmax
import re
# variables to choose which part of the script activates
load_steam_df = False
load_metacritic_df = False
add_source_platform = False
merger = False
load_daily_df = False
trim_dates = False
get_review_sentiment = False
del_null_sentiment = False
make_lowercase = False
remove_misc_characters = False
count_words = False
convert_sentiment_to_float = False
make_weekly_df = False
load_weekly_df = True
drop_rows = False

df_1 = None
df_2 = None
daily_df = None
weekly_df = None

df_path_1 = "df_path_1"
df_path_2 = "df_path_2"
daily_df_path = "daily_df_path"
weekly_df_path = "weekly_df_path"


# load in steam DF: DONE
if load_steam_df:
    if os.path.exists(df_path_1):
        df_1 = pd.read_pickle(df_path_1)

    # add new columns to steam DF to become compatible with MC DF
    if add_source_platform:
        if not 'platform' in df_1.columns:
            df_1['platform'] = 'PC'
        if not 'data_source' in df_1.columns:
            df_1['data_source'] = 'Place'

# load MC DF: DONE
if load_metacritic_df:
    if os.path.exists(df_path_2):
        df_2 = pd.read_pickle(df_path_2)

# merge two DFs into one daily (original format) DF: DONE
if merger:
    if df_2.any and df_1.any:
        daily_df = pd.concat([df_2, df_1],ignore_index=True)

        # save this file as it will be a good baseline to go forward from
        daily_df.to_pickle(daily_df_path)
        print(daily_df.shape)
        print(daily_df.describe())

# load daily df:DONE
if load_daily_df:
    if os.path.exists(daily_df_path):
        daily_df = pd.read_pickle(daily_df_path)

# trim off all reviews from before the first steam one: DONE
if trim_dates:
    filtered_df = daily_df[daily_df['data_source'] == 'Steam']
    starting_date = filtered_df['review_date'].min()

    mask = daily_df['review_date'] >= starting_date
    daily_df = daily_df[mask]
    daily_df.to_pickle(daily_df_path)

# run the sentiment analysis package on reviews: DONE
if get_review_sentiment:
    if not "neg_sentiment" in daily_df.columns:
        daily_df['neg_sentiment'] = None
        daily_df['neu_sentiment'] = None
        daily_df['pos_sentiment'] = None

        MODEL = f"cardiffnlp/twitter-roberta-base-sentiment"
        tokenizer = AutoTokenizer.from_pretrained(MODEL)
        model = AutoModelForSequenceClassification.from_pretrained(MODEL)

        def polarity_scores_roberta(example):
            encoded_text = tokenizer(example, return_tensors='pt')
            output = model(**encoded_text)
            scores = output[0][0].detach().numpy()
            scores = softmax(scores)
            scores_dict = {
                'neg_sentiment' : scores[0],
                'neu_sentiment' : scores[1],
                'pos_sentiment' : scores[2]
            }
            return scores_dict
        num_broken = 0
        for index, row in daily_df.iterrows():
            try:
                text = row['review_text']
                roberta_result = polarity_scores_roberta(text)
                daily_df.loc[index, 'neg_sentiment'] = roberta_result['neg_sentiment']
                daily_df.loc[index, 'neu_sentiment'] = roberta_result['neu_sentiment']
                daily_df.loc[index, 'pos_sentiment'] = roberta_result['pos_sentiment']
            except:
                    num_broken += 1
        print(num_broken)
        daily_df.to_pickle(daily_df_path)

# check for blank sentiment and remove those rows: DONE
if del_null_sentiment:
    if len(daily_df[daily_df['neu_sentiment'].isna()]) > 0:
        daily_df = daily_df.dropna(subset='neu_sentiment')
    daily_df.to_pickle(daily_df_path)

# for the review_text column transform all words to lowercase: DONE
if make_lowercase:
    for index, row in daily_df.iterrows():
        daily_df.at[index, 'review_text'] = row['review_text'].lower()
    daily_df.to_pickle(daily_df_path)

# remove unnecessary characters from review_text and replaces them with spaces i.e. !,.?/[]{}()\|: DONE
if remove_misc_characters:
    pattern = r"[^a-zA-Z0-9'*&$%/-_]"

    for index, row in daily_df.iterrows():
        daily_df.at[index, 'review_text'] = re.sub(pattern, ' ', row['review_text'])

    daily_df.to_pickle(daily_df_path)

# make sure that sentiment is in float format and not an object: DONE
if convert_sentiment_to_float:
    daily_df['neg_sentiment'] = daily_df['neg_sentiment'].astype(float) 
    daily_df['neu_sentiment'] = daily_df['neu_sentiment'].astype(float) 
    daily_df['pos_sentiment'] = daily_df['pos_sentiment'].astype(float) 
    daily_df.to_pickle(daily_df_path)

# group by week: DONE
if make_weekly_df:
    # make direct copy of daily df
    weekly_df = daily_df

    # turn dates into int values
    weekly_df["week"] = weekly_df['review_date'].dt.isocalendar().week
    weekly_df["year"] = weekly_df['review_date'].dt.isocalendar().year

    # get the number of reviews that each word appears in
    def word_freq(reviews):
        num_words_to_track = 40
        words_to_ignore_list = ['the', 'to', 'and', 'a', 'of', 'is', 'for', 'i', 'this', 'it','in', 'that', 'with', 'you', 'we', 
                            'but', 'not', 'they', 'on', 'are', 'all', 'be', 'my', 'has', 'as', 'so','or', 'can', 'at', 'just',
                            'their', 'from', 'was', 'your','one', 'will', 'if', 'now', 'more', 'an', 'no', "it's", 'been', 'its',
                            'out', 'do', 'up', 'by', 'even', "i'm", 'when', 'there', 'about', 'make', "i've", 'who', 'than',
                            'go', 'many','once','too','did',"can't",'things','am','could','something','say','may','let','know',
                            'number', 'somehow',"couldn't",'three',"what's",'till','happens','kinda','willing','tho','whatever',
                            "wasn't",'whether','aside',"you've",'gave','he','looks','happen','list','someone',"they've",'u',
                            "we're",'ways',"we've","i'd",'shall','oh','tell','goes','cause',"let's",'true','ah',"i'll",
                            "haven't",'looking','came','lots','both',"didn't",'cant','side',"that's",'yes','use','able','come',
                            'those','me','what','had','were','around', 'im','please','else',"won't",'get','back','game','still',
                            'some','our','them','though','does',"isn't",'gets','sure','must','each',"there's",'left',"they're",
                            "you'll","aren't",'because','doing','into','see','down','made','being','got','lot','getting','these',
                            'here','makes',"doesn't",'having','same','dont','put','yet','own','bring','seem','show','edit','ones','t',
                            "you're",'itself','2024','lets','boys','stay','yeah','yourself','comes','&','/','within','e','wont',
                            'otherwise','6th','gives','none','o','movie',':d','taken','etc','pull','set','ive','waiting',
                            'themselves', '/','example', 'edit:','man','re','taking','non','yourself',"game's",'guys',':',
                            'fellow','2',"don't",'really','managed','only','also','us','ever','how','then','keep','which',
                            'need','going','thing','take','s','try','truly','3','trying','liber','far','seen','however','bringing',
                            'totally','putting','knows','superearth','d','anyway','=','gamer','order:','p','8','upon','gotta',
                            'called','throughout','n','de','fully','oil','guess','further', '9','thats',"wouldn't",'close','ago',
                            'happened','later','given','m','allowing','onto','form','word','la','have','democracy','helldivers',
                            'much','over','never','well','live','long','where','should','co','spread','thank','divers','gaming',
                            'day','steam','enough', 'tea','1','almost','said','point','earth','dive','review','part','after',
                            'liberty','freedom','every','other','want','while','right','any','actually','hell','very',
                            'won','like','super','would','shooter','way','most','play','games','playing','good','time',
                            'people','ed','s','players','player','against','until','fight','order','good','fun','recommend',
                            'played']
        words_to_ignore = set(words_to_ignore_list)
        word_count = {}

        for review in reviews:
            # change string to list
            cur_review_words = set()
            review = review.split()

            # if word is allowed add to set
            for word in review:
                if word not in words_to_ignore:
                    cur_review_words.add(word)

            # add each word in set to frequency counter
            for word in cur_review_words:
                word_count[word] = word_count.get(word, 0) + 1
        
        word_count = dict(sorted(word_count.items(), key = lambda x: x[1], reverse = True)[:num_words_to_track])

        return word_count

    weekly_df = weekly_df.groupby(['week','year']).agg(
        recommendation = ('recommendation', 'mean'),
        review_count = ('recommendation', 'count'),
        common_words = ('review_text', word_freq),
        play_time = ('play_time', 'mean'),
        neg_sentiment = ("neg_sentiment", 'mean'),
        neu_sentiment = ("neu_sentiment", 'mean'),
        pos_sentiment = ("pos_sentiment", 'mean')
    ).reset_index()

    weekly_df.to_pickle(weekly_df_path)

# load weekly DF: DONE
if load_weekly_df:
    if os.path.exists(weekly_df_path):
        weekly_df = pd.read_pickle(weekly_df_path)    
        print(weekly_df.head(20))

# using to delete rows without enough data: DONE
if drop_rows:
    weekly_df = weekly_df[weekly_df['week']!=34]
    weekly_df.to_pickle(weekly_df_path)