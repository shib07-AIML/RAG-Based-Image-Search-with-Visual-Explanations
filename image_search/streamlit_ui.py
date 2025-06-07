import streamlit as st
import requests

st.title("Image Search via Text")

query = st.text_input("Enter your search query")

if st.button("Search") and query:
    try:
        response = requests.post("http://localhost:8089/search", json={"query": query})
        #st.write("Status code:", response.status_code)
        #st.code(response.text)

        if response.status_code == 200:
            results = response.json().get("results", [])
            for res in results:
                st.image(res["image_url"], width=300)
                st.markdown(f"**Description:** {res['explanation']}")
        else:
            st.error("API call failed.")
    except Exception as e:
        st.error(f"Request error: {e}")
