import streamlit as st
from jobsdatascrapper import process_data
from jobsdatascrapper import geminiclient
from jobsvectorembedding import findJobsData

st.title("Wells Job Search: Jobs Q&A 👕")

numpages = st.text_input("Number Of Pages to load wells fargo data: ")

question = st.text_input("Question: ")
if numpages and not question:
     process_data(numpages)

if question:
     response = findJobsData(question)
     st.header("Answer")
     st.write(response)