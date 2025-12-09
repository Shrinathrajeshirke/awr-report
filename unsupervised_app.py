import streamlit as st
import os
import sys
import tempfile
from src.exception import CustomException
from src.unsupervised_pipeline.unsupervised_prediction_pipeline import UnsupervisedPredictPipeline
from src.logger import logging

ANOMALY_SCORE_THRESHOLD = -0.025

st.set_page_config(page_title="AWR Anomaly detection", layout="wide")
st.title("AWR Report Anomaly Detector")

try:
    predictor = UnsupervisedPredictPipeline()
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

        with st.spinner('Analyzing AWR report and detecting Anomalies...'):
            status, anomaly_score = predictor.predict(html_filepath=tmp_filepath,
                                                      anomaly_threshold=ANOMALY_SCORE_THRESHOLD)

        st.divider()
        col1, col2 = st.columns([1,2])

        with col1:
            st.subheader("Prediction status")
    
            if status == "NORMAL":
                st.success(f"**NORMAL**")
                st.markdown(f"The AWR report metrics are consistent with typical system behavior")
            else:
                st.error(f"**{status}**")
                st.markdown("Metrices indicate a significant deviation from the normal")
        
        with col2:
            st.subheader("Anomaly score (lower is more anomalous)")

            st.metric(
                label="Isolation Forest Score",
                value= f"{anomaly_score:.4f}",
                delta=f"Threshold: {ANOMALY_SCORE_THRESHOLD:.4f}",
                delta_color="off"
            )

            st.caption(f"A score below **{ANOMALY_SCORE_THRESHOLD:.4f}** is flagged as an anomaly.")

    except CustomException as e:
        st.error(f"Prediction Error: Data processing failed. Details: {e.error_message}")
        logging.error(f"Prediction Error in App: {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        logging.error(f"Generic App Error: {e}")
    finally:
        # Clean up the temporary file
        if tmp_filepath and os.path.exists(tmp_filepath):
            os.remove(tmp_filepath)