import pandas as pd
import streamlit as st
import plotly.express as px
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import plotly.graph_objects as go
st.set_page_config(page_title="Predicting and Betting the 2021 Grammy Awards!", page_icon='https://seeklogo.com/images/G/grammy-awards-logo-C83A55BBCB-seeklogo.com.png', layout='wide', initial_sidebar_state='collapsed')

c1, c2, st, c3 = st.beta_columns((1.4, .2, 5, .5))

# @st.cache
def get_data():
    return pd.read_csv("https://ckeatingnh-images.s3.us-east-2.amazonaws.com/grammy_nominees_with_music_attributes+(1).csv").drop('Unnamed: 0', axis=1)
def _max_width_():
    max_width_str = f"max-width: 58%;"
    st.markdown(
        f"""
    <style>
    .reportview-container .main .block-container{{
        {max_width_str}
    }}
    </style>    
    """,
        unsafe_allow_html=True,
    )
    
# _max_width_()
df = get_data()
df.rename(columns={'valence': 'happiness'}, inplace=True)
year = 2021
nominees_for_2021 = list(df[df['year'] == 2021]['song'])

st.title("Predicting and Betting the 2021 Grammy Awards!")
year = c1.slider("Select the year you want to check out:", int(df['year'].min()), int(df['year'].max()), int(df['year'].max()))
x_options = ['danceability', 'energy', 'loudness',  'speechiness', 'acousticness',  'tempo', 'happiness']
st.header(f"You're looking at the Grammy Awards for {year}. See how the winner and losers compare to the previous ten years.")

# Modify the passed in data
df[x_options] = MinMaxScaler().fit_transform(df[x_options])
df_history = df[(df['year'] < year) & (df['year'] > year - 10)]
df_this_year = df[df['year'] == year]
df_this_year['Category'] = 'Selected Year (Loser)'
df_this_year['Cat'] = 'Historic'
df_this_year.loc[df_this_year['won_award'] == 1, 'Category'] = 'Selected Year (Winner)'
past_winners = df_history.drop(columns=['year']).groupby('won_award').agg('mean').reset_index()
past_winners['Category'] = 'Historic'
past_winners['Cat'] = 'Historic'
past_winners['musician'] = ''
past_winners.loc[past_winners['won_award'] == 0, 'Category'] = 'Past Losers (Previous 10 years)'
past_winners.loc[past_winners['won_award'] == 1, 'Category'] = 'Past Winners (Previous 10 years)'
past_winners['song'] = past_winners['Category']
compare_nominees_to_history = pd.concat([past_winners,df_this_year[['song', 'musician', 'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'happiness', 'tempo','duration_ms', 'time_signature', 'Category', 'won_award']]]).set_index('song', drop=True)

# Spider graph for comparing nominees to past winners on all traits    

# selected_attributes = st.multiselect('Which attributes do you want to view?',x_options, ['danceability', 'energy', 'loudness',  'speechiness', 'acousticness',  'tempo', 'happiness'])
selected_attributes = ['danceability', 'energy', 'loudness',  'speechiness', 'acousticness',  'tempo', 'happiness']

songs_to_compare = compare_nominees_to_history.index.tolist()
song_comparisons = st.multiselect("Songs to compare", songs_to_compare[2:], default=songs_to_compare[3:6])
include_historic = st.checkbox('Include the winners and losers from the previous 10 years')
historic_songs = []
if include_historic:
    historic_songs = songs_to_compare[0:2]

if len(selected_attributes) > 0:
#     compare_nominees_to_history[selected_attributes] = MinMaxScaler().fit_transform(compare_nominees_to_history[selected_attributes])
    spider_fig = go.Figure()
    if len(historic_songs) > 0:
        for song in historic_songs:   
            cat = compare_nominees_to_history.loc[song]['Category']
            if cat == 'Past Losers (Previous 10 years)':
                fill_color = 'rgba(86, 0, 0, 0.7)'
                border_color='#7a0000'
            elif cat == 'Past Winners (Previous 10 years)':
                fill_color = 'rgba(0, 43, 0, 0.75)'
                border_color='#216603'
            song_name = song + ' - ' + compare_nominees_to_history.loc[song]['musician']
            spider_fig.add_trace(go.Scatterpolar(
                  r=compare_nominees_to_history.loc[song][selected_attributes],
                  theta=selected_attributes,
                  fill='toself',
                  fillcolor=fill_color,
                  line=dict(color=border_color,width=2),
#                   hovertext=song_name,
                  name=song
            ))

    for song in song_comparisons:   
        cat = compare_nominees_to_history.loc[song]['Category']
        song_name = song + ' - ' + compare_nominees_to_history.loc[song]['musician']
        spider_fig.add_trace(go.Scatterpolar(
              r=compare_nominees_to_history.loc[song][selected_attributes],
              theta=selected_attributes,
              fill='toself',
#               hovertext=song_name,
              name=song
        ))

    spider_fig.update_layout(
      polar=dict(
        radialaxis=dict(
          visible=True,
          range=[0, 1]
        )),
      showlegend=True
    )

    spider_fig.update_layout(title=f"Comparing This Year's Nominees with Past Winners and Losers", autosize=False,
        width=1100, height=800,
        margin=dict(l=100, r=40, b=40, t=40))

    st.plotly_chart(spider_fig)
show_attrs = c1.checkbox('Show attribute definitions?')
if show_attrs:
    c1.markdown(">Acousticness is a confidence measure from 0.0 to 1.0 of whether the track is acoustic. 1.0 represents high confidence the track is acoustic.")
    c1.markdown(">Danceability describes how suitable a track is for dancing based on a combination of musical elements including tempo, rhythm stability, beat strength, and overall regularity. A value of 0.0 is least danceable and 1.0 is most danceable")
    c1.markdown(">Energy is a measure from 0.0 to 1.0 and represents a perceptual measure of intensity and activity. Typically, energetic tracks feel fast, loud, and noisy. For example, death metal has high energy, while a Bach prelude scores low on the scale. Perceptual features contributing to this attribute include dynamic range, perceived loudness, timbre, onset rate, and general entropy.")
    c1.markdown(">Loudness is the overall loudness of a track in decibels (dB). Loudness values are averaged across the entire track and are useful for comparing relative loudness of tracks. Loudness is the quality of a sound that is the primary psychological correlate of physical strength (amplitude). Values typical range between -60 and 0 db.")
    c1.markdown(">Speechiness detects the presence of spoken words in a track. The more exclusively speech-like the recording (e.g. talk show, audio book, poetry), the closer to 1.0 the attribute value. Values above 0.66 describe tracks that are probably made entirely of spoken words. Values between 0.33 and 0.66 describe tracks that may contain both music and speech, either in sections or layered, including such cases as rap music. Values below 0.33 most likely represent music and other non-speech-like tracks.")
    c1.markdown(">Tempo is the overall estimated tempo of a track in beats per minute (BPM). In musical terminology, tempo is the speed or pace of a given piece and derives directly from the average beat duration.")
    c1.markdown(">Valence (renamed as happiness) is a measure from 0.0 to 1.0 describing the musical positiveness conveyed by a track. Tracks with high valence sound more positive (e.g. happy, cheerful, euphoric), while tracks with low valence sound more negative (e.g. sad, depressed, angry).")

st.header('Do Grammy nominees follow existing trends in popular music, or do they start new trends?')
st.write('And can we use this information to make a more educated guess about which traits are more/less important to predicting a winner for this year\'s Grammys?')

# Transform data for line graph
historical = pd.read_csv("https://ckeatingnh-images.s3.us-east-2.amazonaws.com/data_by_year.csv").set_index('year')
historical.rename(columns={'valence': 'happiness'}, inplace=True)
historical = historical[selected_attributes]
# historical[selected_attributes] = MinMaxScaler().fit_transform(historical[selected_attributes])
historical = historical.rolling(20, min_periods=3).mean().dropna()
historical = historical[historical.index > 1960]

historical_grammy_comparison = st.selectbox('Musical attributes to compare:', x_options.copy())

grouped = df[df['year'] < year].groupby('year').mean()
grouped_winners = df[df['won_award']==1].groupby('year').mean()
grouped_winners = grouped_winners[selected_attributes]
grouped_winners[selected_attributes] = MinMaxScaler().fit_transform(grouped_winners[selected_attributes])
grouped_winners = grouped_winners.rolling(30, min_periods=5).mean().dropna()

grouped_losers = df[df['won_award']==0].groupby('year').mean()
grouped_losers = grouped_losers[selected_attributes]
grouped_losers[selected_attributes] = MinMaxScaler().fit_transform(grouped_losers[selected_attributes])
grouped_losers = grouped_losers.rolling(30, min_periods=5).mean().dropna()
# st.table(historical)
grouped[selected_attributes] = MinMaxScaler().fit_transform(grouped[selected_attributes])
# df_this_year[selected_attributes] = MinMaxScaler().fit_transform(df_this_year[selected_attributes])

grouped = df.groupby(['won_award', 'year']).mean()
grouped = grouped[selected_attributes]

grouped.reset_index(inplace=True)
grouped_lose = grouped[(grouped['won_award'] == 0) & (grouped['year'] < 2021)]
grouped_win = grouped[grouped['won_award'] == 1]
grouped_lose.set_index('year', inplace=True)
grouped_win.set_index('year', inplace=True)
grouped_lose = grouped_lose.rolling(30, min_periods=5).mean().dropna()
grouped_win = grouped_win.rolling(30, min_periods=5).mean().dropna()

import plotly.graph_objects as go

compare_fig = go.Figure()

compare_fig.add_trace(go.Scatter(
    x=grouped_win.index,
    y=grouped_win[historical_grammy_comparison], 
    name='Grammy winners'
))

compare_fig.add_trace(go.Scatter(
    x=grouped_lose.index,
    y=grouped_lose[historical_grammy_comparison], 
    name='Grammy losers'
))

def add_scatter_per_song(row):
    compare_fig.add_trace(go.Scatter(x=[2021], y=[row[historical_grammy_comparison]], mode='markers', name=row['song']))
df_this_year.apply(add_scatter_per_song, axis=1)
    
compare_fig.update_layout(title=f"Compare Grammy nominees to overall music trends over time", autosize=False,
    width=1100, height=500,
    margin=dict(l=0, r=40, b=40, t=40))
st.plotly_chart(compare_fig)

st.header('What is your prediction for this year\'s song of the year?')

winner_prediction = st.selectbox("Your prediction: which song wins the 2021 Grammy Award for Best Song?", ['- Pick a winner here -'] + nominees_for_2021)

if winner_prediction != '- Pick a winner here -':
    st.header(f'Your selection is {winner_prediction} - let\'s see what the model and the public betting odds say about your selection:')

    model = pd.read_csv("https://ckeatingnh-images.s3.us-east-2.amazonaws.com/models_final.csv").set_index('song')

    display_model = model[['betting_odds_covers_com', 'preds_voting_classifier_exp']]

    current_odds = list(display_model.loc[winner_prediction])

    odds_fig = go.Figure()

    odds_fig.add_trace(go.Indicator(
        mode = "number",
    #     mode = "number+delta",
        value = current_odds[1],
        title = {"text": "Chris' Model<br><span style='font-size:0.8em;color:gray'>Voting Classifier Model with Logistic Regression, KNN, and Decision Tree</span><br>"},
    #     <span style='font-size:0.8em;color:gray'>Subsubtitle</span>
    #     delta = {'reference': 400, 'relative': True},
        domain = {'x': [0, .45], 'y': [0, 1]}
    ))
    
    odds_fig.update_traces(number_suffix='%', selector=dict(type='indicator'))

    odds_fig.add_trace(go.Indicator(
        mode = "number",
        value = current_odds[0],
        title = {"text": "Betting Odds Implied Chance of Winning<br><span style='font-size:0.8em;color:gray'>Odds courtesy of Covers.com</span><br>"},
    #     <span style='font-size:0.8em;color:gray'>Subsubtitle</span>
    #     delta = {'reference': 400, 'relative': True},
        domain = {'x': [.55, 1], 'y': [0, 1]}
    ))
    
    odds_fig.update_traces(number_suffix='%', selector=dict(type='indicator'))

    odds_fig.update_layout(autosize=False, width=1100, height=500, margin=dict(l=0, r=40, b=40, t=40))

    st.plotly_chart(odds_fig)



# most_important_trait = st.selectbox("Which attribute do you think is the most important?", ['- Pick the most important trait here -'] + x_options)
# ['danceability', 'energy', 'loudness',  'speechiness', 'acousticness',  'tempo', 'happiness']

# show songs from a year
# print out lyrics and positivity and negativity score
# clean one lyrics and display it
# print out lyrics and discuss whether it is postive or negative
# notebook 5 add nlp results
# “Previous 10 years”
# View historic winners as a checkbox
# Add this year’s nominees
# compare nominee avgs to music overall avgs
# flip throught traits
# which features did I find most important in 2021
# regressions with small datasets
# gradient booster, do other models

# st.header("Caching our data")
# st.markdown("Streamlit has a handy decorator [`st.cache`](https://streamlit.io/docs/api.html#optimize-performance) to enable data caching.")
# st.code("""
# @st.cache
# def get_data():
#     url = "http://data.insideairbnb.com/united-states/ny/new-york-city/2019-09-12/visualisations/listings.csv"
#     return pd.read_csv(url)
# """, language="python")
# st.markdown("_To display a code block, pass in the string to display as code to [`st.code`](https://streamlit.io/docs/api.html#streamlit.code)_.")
# with st.echo():
#     st.markdown("Alternatively, use [`st.echo`](https://streamlit.io/docs/api.html#streamlit.echo).")

# st.header("Where are the most expensive properties located?")
# st.subheader("On a map")
# st.markdown("The following map shows the top 1% most expensive Airbnbs priced at $800 and above.")
# st.map(df.query("price>=800")[["latitude", "longitude"]].dropna(how="any"))
# st.subheader("In a table")
# st.markdown("Following are the top five most expensive properties.")
# st.write(df.query("price>=800").sort_values("price", ascending=False).head())

# st.subheader("Selecting a subset of columns")
# st.write(f"Out of the {df.shape[1]} columns, you might want to view only a subset. Streamlit has a [multiselect](https://streamlit.io/docs/api.html#streamlit.multiselect) widget for this.")
# defaultcols = ["name", "host_name", "neighbourhood", "room_type", "price"]
# cols = st.multiselect("Columns", df.columns.tolist(), default=defaultcols)
# st.dataframe(df[cols].head(10))

# st.header("Average price by room type")
# st.write("You can also display static tables. As opposed to a data frame, with a static table you cannot sorting by clicking a column header.")
# st.table(df.groupby("room_type").price.mean().reset_index()\
#     .round(2).sort_values("price", ascending=False)\
#     .assign(avg_price=lambda x: x.pop("price").apply(lambda y: "%.2f" % y)))

# st.header("Which host has the most properties listed?")
# listingcounts = df.host_id.value_counts()
# top_host_1 = df.query('host_id==@listingcounts.index[0]')
# top_host_2 = df.query('host_id==@listingcounts.index[1]')
# st.write(f"""**{top_host_1.iloc[0].host_name}** is at the top with {listingcounts.iloc[0]} property listings.
# **{top_host_2.iloc[1].host_name}** is second with {listingcounts.iloc[1]} listings. Following are randomly chosen
# listings from the two displayed as JSON using [`st.json`](https://streamlit.io/docs/api.html#streamlit.json).""")

# st.json({top_host_1.iloc[0].host_name: top_host_1\
#     [["name", "neighbourhood", "room_type", "minimum_nights", "price"]]\
#         .sample(2, random_state=4).to_dict(orient="records"),
#         top_host_2.iloc[0].host_name: top_host_2\
#     [["name", "neighbourhood", "room_type", "minimum_nights", "price"]]\
#         .sample(2, random_state=4).to_dict(orient="records")})

# st.header("What is the distribution of property price?")
# st.write("""Select a custom price range from the side bar to update the histogram below displayed as a Plotly chart using
# [`st.plotly_chart`](https://streamlit.io/docs/api.html#streamlit.plotly_chart).""")
# values = st.sidebar.slider("Price range", float(df.price.min()), float(df.price.clip(upper=1000.).max()), (50., 300.))
# f = px.histogram(df.query(f"price.between{values}"), x="price", nbins=15, title="Price distribution")
# f.update_xaxes(title="Price")
# f.update_yaxes(title="No. of listings")
# st.plotly_chart(f)

# st.header("What is the distribution of availability in various neighborhoods?")
# st.write("Using a radio button restricts selection to only one option at a time.")
# st.write("💡 Notice how we use a static table below instead of a data frame. \
# Unlike a data frame, if content overflows out of the section margin, \
# a static table does not automatically hide it inside a scrollable area. \
# Instead, the overflowing content remains visible.")
# neighborhood = st.radio("Neighborhood", df.neighbourhood_group.unique())
# show_exp = st.checkbox("Include expensive listings")
# show_exp = " and price<200" if not show_exp else ""

# @st.cache
# def get_availability(show_exp, neighborhood):
#     return df.query(f"""neighbourhood_group==@neighborhood{show_exp}\
#         and availability_365>0""").availability_365.describe(\
#             percentiles=[.1, .25, .5, .75, .9, .99]).to_frame().T

# st.table(get_availability(show_exp, neighborhood))
# st.write("At 169 days, Brooklyn has the lowest average availability. At 226, Staten Island has the highest average availability.\
#     If we include expensive listings (price>=$200), the numbers are 171 and 230 respectively.")
# st.markdown("_**Note:** There are 18431 records with `availability_365` 0 (zero), which I've ignored._")

# df.query("availability_365>0").groupby("neighbourhood_group")\
#     .availability_365.mean().plot.bar(rot=0).set(title="Average availability by neighborhood group",
#         xlabel="Neighborhood group", ylabel="Avg. availability (in no. of days)")
# st.pyplot()

# st.header("Properties by number of reviews")
# st.write("Enter a range of numbers in the sidebar to view properties whose review count falls in that range.")
# minimum = st.sidebar.number_input("Minimum", min_value=0)
# maximum = st.sidebar.number_input("Maximum", min_value=0, value=5)
# if minimum > maximum:
#     st.error("Please enter a valid range")
# else:
#     df.query("@minimum<=number_of_reviews<=@maximum").sort_values("number_of_reviews", ascending=False)\
#         .head(50)[["name", "number_of_reviews", "neighbourhood", "host_name", "room_type", "price"]]

# st.write("486 is the highest number of reviews and two properties have it. Both are in the East Elmhurst \
#     neighborhood and are private rooms with prices $65 and $45. \
#     In general, listings with >400 reviews are priced below $100. \
#     A few are between $100 and $200, and only one is priced above $200.")
# st.header("Images")
# pics = {
#     "Cat": "https://cdn.pixabay.com/photo/2016/09/24/22/20/cat-1692702_960_720.jpg",
#     "Puppy": "https://cdn.pixabay.com/photo/2019/03/15/19/19/puppy-4057786_960_720.jpg",
#     "Sci-fi city": "https://storage.needpix.com/rsynced_images/science-fiction-2971848_1280.jpg"
# }
# pic = st.selectbox("Picture choices", list(pics.keys()), 0)
# st.image(pics[pic], use_column_width=True, caption=pics[pic])

# st.markdown("## Party time!")
# st.write("Yay! You're done with this tutorial of Streamlit. Click below to celebrate.")
# btn = st.button("Celebrate!")
# if btn:
#     st.balloons()

# f = px.histogram(df.query(f"price.between{values}"), x="price", nbins=15, title="Price distribution")
# f.update_xaxes(title="Price")
# f.update_yaxes(title="No. of listings")

# st.header("Customary quote")
# st.markdown("> I just love to go home, no matter where I am, the most luxurious hotel suite in the world, I love to go home.\n\n—Michael Caine")
# st.header("Airbnb NYC listings: data at a glance")
# st.markdown("The first five records of the Airbnb data we downloaded.")

# trait = st.selectbox('Which songs do you want to explore?', list(compare_nominees_to_history.index))

# group_fig = px.line(data_frame=grouped)
# group_fig.update_layout(title=f"Overall musical trends of Grammy Nominees", autosize=False,
#     width=1200, height=500,
#     margin=dict(l=0, r=40, b=40, t=40))
# st.plotly_chart(group_fig)

# trait = st.selectbox('Which value do you want to explore?', x_options)

# # First bar chart (showing selected trait for year's nominees)
# fig = px.bar(
#     compare_nominees_to_history, 
#     x=compare_nominees_to_history.index, 
#     y=trait, 
#     color='Category', 
#     hover_data={'Category': False, 'Cat': False, 'musician': True},
#     text='Cat',
#     color_discrete_map={
#         'Selected Year (Winner)': '#5ced7e',
#         'Selected Year (Loser)': '#fa7070', 
#         'Past Losers (Previous 10 years)': '#7a0000', 
#         'Past Winners (Previous 10 years)': '#216603'
#     }).update_xaxes(
#     categoryorder="total descending")
# fig.update_layout(title=f"Comparing {trait.title()} in Past Winners and Losers, and This Year's Nominees", autosize=False,width=1200, height=500,margin=dict(l=0, r=40, b=40, t=40))
# st.plotly_chart(fig)


# for song in song_comparisons:   
#         cat = compare_nominees_to_history.loc[song]['Category']
# #         if cat == 'Past Losers (Previous 10 years)':
# #             fill_color = 'rgba(86, 0, 0, 0.7)'
# #             border_color='#7a0000'
# #         elif cat == 'Past Winners (Previous 10 years)':
# #             fill_color = 'rgba(0, 43, 0, 0.75)'
# #             border_color='#216603'
# #         elif cat == 'Selected Year (Winner)':
# #             fill_color = 'rgba(92, 237, 126, 0.5)'
# #             border_color='#5ced7e'
# #         elif cat == 'Selected Year (Loser)':
# #             fill_color = 'rgba(250, 112, 112, 0.5)'
# #             border_color='#fa7070'
# #         st.header(song)
#         song_name = song + ' - ' + compare_nominees_to_history.loc[song]['musician']
#         spider_fig.add_trace(go.Scatterpolar(
#               r=compare_nominees_to_history.loc[song][selected_attributes],
#               theta=selected_attributes,
#               fill='toself',
# #               fillcolor=fill_color,
# #               line=dict(color=border_color,width=2),
#               hovertext=song_name,
#               name=song
#         ))


# import numpy as np
# compare_fig.add_trace(go.Scatter(
#     x=list(historical.index) + [2021],
#     y=list(historical[historical_grammy_comparison]) + [np.nan, np.nan],
#     name='Overall music trends (170k songs)'
# ))

# st.write(current_odds)

# # html_code = f"""
# # <table style="width:100%">
# #   <tr>
# #     <th>Betting Odds</th>
# #     <th>Chris' Model</th>
# #   </tr>
# #   <tr>
# #     <td>{current_odds[0]}</td>
# #     <td>{current_odds[1]}</td>
# #   </tr>
# # </table>
# # """

# html_code = """
# <table class="eli5-weights eli5-feature-importances" style="border-collapse: collapse; border: none; margin-top: 0em; table-layout: auto;">
# <thead>
# <tr style="border: none;">
#     <th style="padding: 0 1em 0 0.5em; text-align: right; border: none;">Weight</th>
#     <th style="padding: 0 0.5em 0 0.5em; text-align: left; border: none;">Feature</th>
# </tr>
# </thead>
# <tbody>
#     <tr style="background-color: hsl(120, 100.00%, 80.00%); border: none;">
#         <td style="padding: 0 1em 0 0.5em; text-align: right; border: none;">
#             0.4567 &plusmn; 0.5815
#         </td>
#         <td style="padding: 0 0.5em 0 0.5em; text-align: left; border: none;">
#             x3
#         </td>
#     </tr>
#     <tr style="background-color: hsl(120, 100.00%, 81.40%); border: none;">
#         <td style="padding: 0 1em 0 0.5em; text-align: right; border: none;">
#             0.4116 &plusmn; 0.5792
#         </td>
#         <td style="padding: 0 0.5em 0 0.5em; text-align: left; border: none;">
#             x2
#         </td>
#     </tr>
#     <tr style="background-color: hsl(120, 100.00%, 93.05%); border: none;">
#         <td style="padding: 0 1em 0 0.5em; text-align: right; border: none;">
#             0.1008 &plusmn; 0.2772
#         </td>
#         <td style="padding: 0 0.5em 0 0.5em; text-align: left; border: none;">
#             x0
#         </td>
#     </tr>
#     <tr style="background-color: hsl(120, 100.00%, 96.96%); border: none;">
#         <td style="padding: 0 1em 0 0.5em; text-align: right; border: none;">
#             0.0309 &plusmn; 0.0822
#         </td>
#         <td style="padding: 0 0.5em 0 0.5em; text-align: left; border: none;">
#             x1
#         </td>
#     </tr>
# </tbody>
# """

# st.markdown(html_code, unsafe_allow_html=True)
