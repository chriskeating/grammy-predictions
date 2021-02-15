import pandas as pd
import streamlit as st
import plotly.express as px
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import plotly.graph_objects as go

# @st.cache
def get_data():
    return pd.read_csv("https://ckeatingnh-images.s3.us-east-2.amazonaws.com/grammy_nominees_with_music_attributes.csv").drop('Unnamed: 0', axis=1)
def _max_width_():
    max_width_str = f"max-width: 63%;"
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
    
_max_width_()
df = get_data()
df.rename(columns={'valence': 'happiness'}, inplace=True)
year = 2021

# Header
st.title(f"Predicting and Betting the 2021 Grammy Awards!")
year = st.slider("Select the year you want to check out:", int(df['year'].min()), int(df['year'].max()), int(df['year'].max()))
x_options = ['danceability', 'energy', 'loudness',  'speechiness', 'acousticness',  'tempo', 'happiness']
trait = st.selectbox('Which value do you want to explore?', x_options)
st.header(f"You're looking at the Grammy Awards for {year}. See how the winner and losers compare to the previous ten years.")

# Modify the passed in data
df_history = df[(df['year'] < year) & (df['year'] > year - 10)]
df_this_year = df[df['year'] == year]
df_this_year['Category'] = 'Current Year (Loser)'
df_this_year['Cat'] = 'Historic'
df_this_year.loc[df_this_year['won_award'] == 1, 'Category'] = 'Current Year (Winner)'
past_winners = df_history.drop(columns=['year']).groupby('won_award').agg('mean').reset_index()
past_winners['Category'] = 'Historic'
past_winners['Cat'] = 'Historic'
past_winners['musician'] = ''
past_winners.loc[past_winners['won_award'] == 0, 'Category'] = 'Historic Losers (10 years)'
past_winners.loc[past_winners['won_award'] == 1, 'Category'] = 'Historic Winners (10 years)'
past_winners['song'] = past_winners['Category']
compare_nominees_to_history = pd.concat([past_winners,df_this_year[['song', 'musician', 'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'happiness', 'tempo','duration_ms', 'time_signature', 'Category', 'won_award']]]).set_index('song', drop=True)

# First bar chart (showing selected trait for year's nominees)
fig = px.bar(
    compare_nominees_to_history, 
    x=compare_nominees_to_history.index, 
    y=trait, 
    color='Category', 
    hover_data={'Category': False, 'Cat': False, 'musician': True},
    text='Cat',
    color_discrete_map={
        'Current Year (Winner)': '#5ced7e',
        'Current Year (Loser)': '#fa7070', 
        'Historic Losers (10 years)': '#7a0000', 
        'Historic Winners (10 years)': '#216603'
    }).update_xaxes(
    categoryorder="total descending")
fig.update_layout(title=f"Comparing {trait.title()} in Past Winners and Losers, and This Year's Nominees", autosize=False,width=1200, height=500,margin=dict(l=0, r=40, b=40, t=40))
st.plotly_chart(fig)

# Spider graph for comparing nominees to past winners on all traits
selected_attributes = st.multiselect('Which attributes do you want to view?',x_options, ['danceability', 'energy', 'loudness',  'speechiness', 'acousticness',  'tempo', 'happiness'])

songs_to_compare = compare_nominees_to_history.index.tolist()
song_comparisons = st.multiselect("Songs to compare", songs_to_compare, default=songs_to_compare[0:3])

if len(selected_attributes) > 0:
    compare_nominees_to_history[selected_attributes] = MinMaxScaler().fit_transform(compare_nominees_to_history[selected_attributes])
    spider_fig = go.Figure()

    for song in song_comparisons:    
        spider_fig.add_trace(go.Scatterpolar(
              r=compare_nominees_to_history.loc[song][selected_attributes],
              theta=selected_attributes,
              fill='toself',
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
        width=800, height=800,
        margin=dict(l=0, r=40, b=40, t=40))

    st.plotly_chart(spider_fig)

    
# Transform data for line graph
grouped = df[df['year'] < year].groupby('year').mean()
grouped = grouped[selected_attributes]
grouped[selected_attributes] = MinMaxScaler().fit_transform(grouped[selected_attributes])
grouped = grouped.rolling(10).mean().dropna()

# make y axis how important it was to winning
group_fig = px.line(data_frame=grouped)
group_fig.update_layout(title=f"Overall musical trends of Grammy Nominees", autosize=False,
    width=1200, height=500,
    margin=dict(l=0, r=40, b=40, t=40))
st.plotly_chart(group_fig)


st.header('What is your prediction for this year\'s song of the year?')

most_important_trait = st.selectbox("Which attribute do you think is the most important?", ['- Pick the most important trait here -'] + x_options)

winner_prediction = st.selectbox("Your prediction: which song wins the 2021 Grammy Award for Best Song?", ['- Pick a winner here -'] + songs_to_compare[2:])






















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



# current_attrs = ['danceability', 'acousticness', 'loudness']
# speechiness = st.sidebar.checkbox('speechiness')
# # acousticness = st.sidebar.checkbox('acousticness')
# duration_ms = st.sidebar.checkbox('duration_ms')
# energy = st.sidebar.checkbox('energy')
# key = st.sidebar.checkbox('key')
# # loudness = st.sidebar.checkbox('loudness')
# mode = st.sidebar.checkbox('mode')
# instrumentalness = st.sidebar.checkbox('instrumentalness')
# liveness = st.sidebar.checkbox('liveness')
# valence = st.sidebar.checkbox('valence')
# tempo = st.sidebar.checkbox('tempo')
# time_signature = st.sidebar.checkbox('time_signature')

# if speechiness:
#     current_attrs.append('speechiness')
# # if acousticness:
# #     current_attrs.append('acousticness')
# if duration_ms:
#     current_attrs.append('duration_ms')
# if energy:
#     current_attrs.append('energy')
# if key:
#     current_attrs.append('key')
# # if loudness:
# #     current_attrs.append('loudness')
# if mode:
#     current_attrs.append('mode')
# if instrumentalness:
#     current_attrs.append('instrumentalness')
# if liveness:
#     current_attrs.append('liveness')
# if valence:
#     current_attrs.append('valence')
# if tempo:
#     current_attrs.append('tempo')
# if time_signature:
#     current_attrs.append('time_signature')



# Only a subset of options make sense


# plot the value
# fig = px.scatter(df,
#                 x=x_axis,
#                 y='rating',
#                 hover_name='name',
#                 title=f'Cereal ratings vs. {x_axis}')

# st.plotly_chart(fig)

# f = px.histogram(df.query(f"price.between{values}"), x="price", nbins=15, title="Price distribution")
# f.update_xaxes(title="Price")
# f.update_yaxes(title="No. of listings")

# st.header("Customary quote")
# st.markdown("> I just love to go home, no matter where I am, the most luxurious hotel suite in the world, I love to go home.\n\n—Michael Caine")
# st.header("Airbnb NYC listings: data at a glance")
# st.markdown("The first five records of the Airbnb data we downloaded.")

# trait = st.selectbox('Which songs do you want to explore?', list(compare_nominees_to_history.index))