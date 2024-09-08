import pandas as pd
import os.path
import matplotlib.pyplot as plt
from collections import Counter
from statsmodels.stats.proportion import proportions_ztest
from scipy import stats
import math

load_weekly_df = True
load_daily_df = False

make_sentiment_plots = False
make_other_plots = False
make_key_count_plot = False
make_sentiment_review_plots = False
check_frequent_words = True

z_proportion_test = False
t_mean_test = False

weekly_df_path = "weekly_df_path"
weekly_df = None

daily_df_path = "daily_df_path"
daily_df = None

# prepares the dataframe thats been grouped into weeks
if load_weekly_df:
    if os.path.exists(weekly_df_path):
        weekly_df = pd.read_pickle(weekly_df_path)

# make scatter plots showing sentiemnt overtime
if make_sentiment_plots and load_weekly_df:
    plt.figure(figsize=(12,4))

    plt.subplot(1,3,1)
    plt.scatter(weekly_df['week'], weekly_df['neg_sentiment'], color='blue', marker='o')  # 'X' on x-axis, 'Y' on y-axis
    plt.xlabel('weeks')
    plt.ylabel('negative sentiment')
    plt.title('negative sentitmant over time')
    plt.grid(True)

    plt.subplot(1,3,2)
    plt.scatter(weekly_df['week'], weekly_df['neu_sentiment'], color='blue', marker='o')  # 'X' on x-axis, 'Y' on y-axis
    plt.xlabel('weeks')
    plt.ylabel('neutral sentiment')
    plt.title('neutral sentitmant over time')
    plt.grid(True)

    plt.subplot(1,3,3)
    plt.scatter(weekly_df['week'], weekly_df['pos_sentiment'], color='blue', marker='o')  # 'X' on x-axis, 'Y' on y-axis
    plt.xlabel('weeks')
    plt.ylabel('positive sentiment')
    plt.title('positive sentitmant over time')
    plt.grid(True)

    plt.tight_layout()
    plt.show()

#checks to see if other trends exist, more plots
if make_other_plots and load_weekly_df:
    plt.figure(figsize=(12,4))

    plt.subplot(1,3,1)
    plt.scatter(weekly_df['week'], weekly_df['review_count'], color='blue', marker='o')  # 'X' on x-axis, 'Y' on y-axis
    plt.xlabel('weeks')
    plt.ylabel('review_count')
    plt.title('num reviews per week')
    plt.grid(True)

    plt.subplot(1,3,2)
    plt.scatter(weekly_df['week'], weekly_df['recommendation'], color='blue', marker='o')  # 'X' on x-axis, 'Y' on y-axis
    plt.xlabel('weeks')
    plt.ylabel('recommendation score avg')
    plt.title('weekly avg recommendation score')
    plt.grid(True)

    plt.subplot(1,3,3)
    plt.scatter(weekly_df['week'], weekly_df['play_time'], color='blue', marker='o')  # 'X' on x-axis, 'Y' on y-axis
    plt.xlabel('weeks')
    plt.ylabel('play_time')
    plt.title('play time when reviews written')
    plt.grid(True)

    plt.tight_layout()
    plt.show()

#check to see what common words appear across multiple weeks
if make_key_count_plot and load_weekly_df:
    all_keys = [key for d in weekly_df['common_words'] for key in d.keys()]
    key_counts = Counter(all_keys)
    key_counts_df = pd.DataFrame(key_counts.items(), columns=['key', 'count'])

    # plt.figure(figsize=(30,20))
    plt.scatter(key_counts_df['key'], key_counts_df['count'], color='blue', marker='o')  # 'X' on x-axis, 'Y' on y-axis
    plt.xlabel('words')
    plt.xticks(rotation=45)

    plt.ylabel('word frequency')
    plt.title('frequency of most common words over time')
    plt.grid(True)
    
    plt.tight_layout()
    plt.show()

# makes plots to verify sentiment is correlated with review score
if make_sentiment_review_plots and load_weekly_df:
    plt.figure(figsize=(12,4))

    plt.subplot(1,3,1)
    plt.scatter(weekly_df['neg_sentiment'], weekly_df['recommendation'], color='blue', marker='o')  # 'X' on x-axis, 'Y' on y-axis
    plt.xlabel('sentiment')
    plt.ylabel('recommendation')
    plt.title('comparing neg sentiment to score')
    plt.grid(True)

    plt.subplot(1,3,2)
    plt.scatter(weekly_df['neu_sentiment'], weekly_df['recommendation'], color='blue', marker='o')  # 'X' on x-axis, 'Y' on y-axis
    plt.xlabel('sentiment')
    plt.ylabel('recommendation')
    plt.title('comparing neu sentiment to score')
    plt.grid(True)

    plt.subplot(1,3,3)
    plt.scatter(weekly_df['pos_sentiment'], weekly_df['recommendation'], color='blue', marker='o')  # 'X' on x-axis, 'Y' on y-axis
    plt.xlabel('sentiment')
    plt.ylabel('recommendation')
    plt.title('comparing pos sentiment to score')
    plt.grid(True)

    plt.tight_layout()
    plt.show()

# prepares the dataframe that still contains every unique review
if load_daily_df:
    if os.path.exists(daily_df_path):
        daily_df = pd.read_pickle(daily_df_path)
        daily_df["week"] = daily_df['review_date'].dt.isocalendar().week

# z-test for proportion, see if how recommended a game is changes between two specified weeks
if z_proportion_test and load_daily_df:
    patch_start = 23
    patch_end = 31

    patch_start_data = daily_df[daily_df['week'] == patch_start]
    patch_end_data = daily_df[daily_df['week'] == patch_end]

    successes = [patch_start_data['recommendation'].sum(), patch_end_data['recommendation'].sum()]
    totals = [len(patch_start_data), len(patch_end_data)]

    print(successes)
    print(totals)

    z_stat, p_value = proportions_ztest(successes, totals)

    print(f"Z-statistic: {z_stat:.4f}")
    print(f"P-value: {p_value:.4f}")

    alpha = 0.05
    if p_value < alpha:
        print("Significant difference between start and end of patch")
    else:
        print("Start and end of patch have no significant difference")

# t-test for mean, check if there is any significant difference in sentiment between start and end date
if t_mean_test and load_daily_df:
    patch_start = 23
    patch_end = 31

    patch_start_data = daily_df[daily_df['week'] == patch_start]['pos_sentiment']
    patch_end_data = daily_df[daily_df['week'] == patch_end]['pos_sentiment']

    t_stat, p_value = stats.ttest_ind(patch_start_data, patch_end_data, equal_var=False)

    print(f"Z-statistic: {t_stat:.4f}")
    print(f"P-value: {p_value:.4f}")

    alpha = 0.05
    if p_value < alpha:
        print("Significant difference between start and end of patch")
    else:
        print("Start and end of patch have no significant difference")

if check_frequent_words and load_weekly_df:
    # patch breakpoint week numbers
    group_1_end_week  = 22
    group_2_end_week = 31

    # initalize df used to track word differences between patches
    column_names = ['word', 'patch_1_ratio','patch_2_ratio','patch_3_ratio']
    word_freq_df = pd.DataFrame(columns=column_names)
    total_week_reviews = [0,0,0]
    seen_words = set()
    for index, row in weekly_df.iterrows():
        for key, value in row['common_words'].items():
            
            # key doesnt exist, make row first
            if key not in seen_words:
                new_row = {'word': key, 'patch_1_ratio': 0,'patch_2_ratio': 0,'patch_3_ratio': 0}
                word_freq_df = word_freq_df._append(new_row, ignore_index = True)
                seen_words.add(key)
                # new_row = [key, 0, 0, 0]
                # word_freq_df.loc[len(word_freq_df)] = new_row
            
            # update existing row
            if row['week'] <=group_1_end_week:
                word_freq_df.loc[word_freq_df['word']==key, 'patch_1_ratio'] += value
            elif row['week'] <=group_2_end_week:
                word_freq_df.loc[word_freq_df['word']==key, 'patch_2_ratio'] += value
            else:
                word_freq_df.loc[word_freq_df['word']==key, 'patch_3_ratio'] += value

    # get the total number of reviews for the patch in question
    for index, row in weekly_df.iterrows():
        row_total_reviews = row['review_count']
        if row['week'] <=group_1_end_week:
            total_week_reviews[0] += row_total_reviews
        elif row['week'] <=group_2_end_week:
            total_week_reviews[1] += row_total_reviews
        else:
            total_week_reviews[2] += row_total_reviews
    
    # turn frequencies into ratios
    for index, row in word_freq_df.iterrows():
        word_freq_df.at[index, 'patch_1_ratio'] /=total_week_reviews[0]
        word_freq_df.at[index, 'patch_2_ratio'] /=total_week_reviews[1]
        word_freq_df.at[index, 'patch_3_ratio'] /=total_week_reviews[2]
        # print(row['word'])




    # make graphs v1 TODO update to show multiple at a time
    for index, row in word_freq_df.iterrows():
        categories = ['patch_1_ratio', 'patch_2_ratio', 'patch_3_ratio']
        values = [row['patch_1_ratio'], row['patch_2_ratio'], row['patch_3_ratio']]
        plt.figure(figsize=(8, 4))
        plt.bar(categories, values, color=['blue', 'orange', 'green'])
        
        plt.title(f"Ratios for '{row['word']}'")
        plt.xlabel('Ratios')
        plt.ylabel('Values')

        plt.show()

