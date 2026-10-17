import os
import pickle
import streamlit as st
from PIL import Image
from urllib.parse import quote

# Load models
movies = pickle.load(open('artifacts/movie_list.pkl', 'rb'))
similarity = pickle.load(open('artifacts/similarity.pkl', 'rb'))

# Function to fetch poster path safely



import os
import requests
from urllib.parse import quote


def fetch_poster(movie_title):
    import os
    import requests
    from urllib.parse import quote

    safe_title = movie_title.translate(
        str.maketrans('', '', r'\/:*?"<>|')
    ).strip()

    local_path = os.path.join("posters", f"{safe_title}.jpg")

    if os.path.exists(local_path):
        return local_path

    url = (
        "https://en.wikipedia.org/api/rest_v1/page/summary/"
        + quote(movie_title.replace(" ", "_"))
    )

    try:
        response = requests.get(
            url,
            headers={"User-Agent": "MovieRecommender/1.0"},
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            image_url = data.get("thumbnail", {}).get("source")

            if image_url:
                return image_url

    except requests.RequestException:
        pass

    return None




# Recommendation logic
def recommend(movie):
    idx = movies[movies['title'] == movie].index[0]
    distances = similarity[idx]
    movie_indices = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    names = []
    posters = []
    for i in movie_indices:
        title = movies.iloc[i[0]].title
        names.append(title)
        posters.append(fetch_poster(title))
    return names, posters

# UI setup
st.set_page_config(page_title="MovieMatch", page_icon="🎬", layout="wide")
st.title('🎬 Movie Recommender (Offline Version)')

selected_movie = st.selectbox(
    'Select a movie to get recommendations:',
    movies['title'].values
)

if st.button('Show Recommendations'):
    names, posters = recommend(selected_movie)
    cols = st.columns(5)
    for col, name, poster in zip(cols, names, posters):
        with col:
            st.markdown(f"**{name}**")
            if poster is not None:
                if poster.startswith("http"):
                    st.image(poster, use_container_width=True)
                else:
                    img = Image.open(poster)
                    st.image(img, use_container_width=True)
            else:
                st.image("posters/default.jpg", use_container_width=True)
                st.caption("Poster unavailable")

            