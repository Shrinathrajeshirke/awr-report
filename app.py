import streamlit as st
import os
import sys
import tempfile
from src.exception import CustomException
from src.pipeline.predict_pipeline import PredictionPipeline
from src.logger import logging

st.set_page_config(page_title="AWR Anomaly detection", layout="wide")
st.title("AWR Report Anomaly Detector")

try:
    predictor = PredictionPipeline()
    logging.info("Prediction pipeline initialized successfully")
except Exception as e:
    st.error(f"Error initializing prediction pipeline: {e}")
    logging.error(f"Initialization error: {e}")
    sys.exit(1)

uploaded_file = st.file_uploader("Upload AWR HTML Report (.html)", type=["html"])

if uploaded_file is not None:
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_filepath = tmp_file.name

        with st.spinner('Analyzing AWR report and predicting Anomaly type...'):
            predict_anomaly = predictor.predict(html_filepath=tmp_filepath)

        st.divider()
        st.subheader("Prediction Results")

        if predict_anomaly == "NONE":
            st.markdown(f"**Status:** the report indicates **No significant Anomaly**.")
        else:
            st.markdown(f"**Predicted Anomaly Type:** {predict_anomaly}")
    except CustomException as e:
        st.error(f"Prediction Error: A crucial file is missing or data structure is incorrect. Details: {e}")
        logging.error(f"Prediction Error in App: {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        logging.error(f"Generic App Error: {e}")
    finally:
        # Clean up the temporary file
        if 'tmp_filepath' in locals() and os.path.exists(tmp_filepath):
            os.remove(tmp_filepath)
