"""Upload a food image and ask the inference service for a prediction."""
import os

import requests
import streamlit as st

INFERENCE_URL = os.getenv("INFERENCE_URL", "http://127.0.0.1:8000").rstrip("/")

st.set_page_config(page_title="Food-11 classifier", page_icon="🍽️")
st.title("Food-11 classifier")
st.write("Upload a food photo to see the predicted category.")
uploaded = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])

if uploaded is not None:
    st.image(uploaded, width=300)
    if st.button("Predict", type="primary"):
        try:
            with st.spinner("Checking your image…"):
                response = requests.post(
                    f"{INFERENCE_URL}/predict",
                    files={"file": (uploaded.name, uploaded.getvalue(), uploaded.type)},
                    timeout=(5, 60),
                )
                response.raise_for_status()
                result = response.json()
            st.success(f"Prediction: {result['category']} ({result['confidence']:.1%})")
        except requests.HTTPError as exc:
            if exc.response.status_code == 400:
                st.error("This file could not be read as an image. Please try another one.")
            else:
                st.error("The prediction failed. Please try again in a moment.")
        except requests.RequestException:
            st.error("The prediction service is unavailable. Please try again shortly.")
        except (ValueError, KeyError, TypeError):
            st.error("The prediction service returned an unexpected response.")
