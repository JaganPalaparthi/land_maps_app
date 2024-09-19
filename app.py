import os
import re
import zipfile
import streamlit as st
from PyPDF2 import PdfReader
import simplekml
import pandas as pd

# Function to extract text from a PDF
def extract_text_from_pdf(pdf_file):
    text = ""
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        text += page.extract_text()
    return text

# Function to find LP_NUMBER after a specific keyword
def find_lp_number(text, keyword):
    pattern = re.compile(re.escape(keyword) + r'\s*(\S+)')
    match = pattern.search(text)
    if match:
        return match.group(1)
    else:
        return "LP_NUMBER not found"

# Function to find the value after a dynamic prefix and before a static suffix
def find_value_after_dynamic_prefix(text):
    pattern = re.compile(r'79.{12}(\d+\.\d+)Ğʂమĉ')
    match = pattern.search(text)
    if match:
        return match.group(1)
    else:
        return "Value not found"

# Function to extract latitude and longitude coordinates
def extract_lat_long_from_pdf(text):
    coordinates = []
    lat_long_pattern = re.compile(r"(\d{2}\.\d+)\s+\d+\.\d+\s+\d+\.\d+\s+(\d{2}\.\d+)")
    lines = text.splitlines()
    for line in lines:
        match = lat_long_pattern.search(line)
        if match:
            long = float(match.group(1))  # Longitude
            lat = float(match.group(2))  # Latitude
            coordinates.append({"Latitude": lat, "Longitude": long})
    return coordinates

# Function to create a KML file from coordinates
def create_kml_file(coordinates, lp_number, total_extent, kml_file_path, pattadar_name, katha_number):
    kml = simplekml.Kml()
    coords = [(point['Longitude'], point['Latitude']) for point in coordinates]
    coords.append(coords[0])  # Close the polygon
    
    # Create the polygon with LP_NUMBER and total_extent in the name
    polygon_name = f"Polygon - LP: {lp_number}, Extent: {total_extent}, Pattadar: {pattadar_name}, Katha: {katha_number}"
    pol = kml.newpolygon(name=polygon_name)
    pol.outerboundaryis = coords
    pol.style.polystyle.color = "red"  # Set color to red
    pol.style.polystyle.fill = 1
    pol.style.polystyle.outline = 1
    
    # Calculate the center point for the placemark
    avg_lat = sum(point['Latitude'] for point in coordinates) / len(coordinates)
    avg_lon = sum(point['Longitude'] for point in coordinates) / len(coordinates)
    
    # Create a placemark with LP_NUMBER, total_extent, pattadar_name, and katha_number in the label
    placemark_name = f"LP: {lp_number}, Extent: {total_extent}, Pattadar: {pattadar_name}, Katha: {katha_number}"
    placemark = kml.newpoint(name=placemark_name, coords=[(avg_lon, avg_lat)])
    placemark.style.labelstyle.scale = 1.5
    
    # Save the KML file with the desired filename format
    kml.save(kml_file_path)

# Streamlit App UI
st.title("LAND MAPS")

# User inputs for Pattadar Name and Katha Number
pattadar_name = st.text_input("Enter Pattadar Name")
katha_number = st.number_input("Enter Katha Number", min_value=1)

# File uploader for multiple PDFs
uploaded_files = st.file_uploader("Upload PDF files", type="pdf", accept_multiple_files=True)

# Predefined keyword for LP_NUMBER extraction
keyword = "భూకమత పటĉ :"

# Directory for storing generated KML files
output_dir = "output_kml"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Table data initialization
table_data = []

if st.button("Process PDFs"):
    if uploaded_files and pattadar_name and katha_number:
        kml_file_paths = []
        
        # Process each uploaded PDF
        for pdf_file in uploaded_files:
            pdf_name = pdf_file.name
            kml_file_name = None
            kml_file_path = None
            status = "Processing"
            kml_status = "No"
            download_link = ""
            
            try:
                # Extract text from PDF
                text = extract_text_from_pdf(pdf_file)
                
                # Find LP_NUMBER and total_extent
                lp_number = find_lp_number(text, keyword)
                total_extent = find_value_after_dynamic_prefix(text)
                
                # Extract coordinates
                coordinates = extract_lat_long_from_pdf(text)
                
                # Define KML file path with pattadar_name and katha_number
                kml_file_name = f"{lp_number}_{total_extent}_{pattadar_name}_{katha_number}.kml"
                kml_file_path = os.path.join(output_dir, kml_file_name)
                
                # Create KML file
                create_kml_file(coordinates, lp_number, total_extent, kml_file_path, pattadar_name, katha_number)
                
                kml_file_paths.append(kml_file_path)
                status = "Processed"
                kml_status = "Yes"
                download_link = kml_file_name
            except Exception as e:
                status = f"Error: {str(e)}"
            
            # Append to table data
            table_data.append({
                "File Name": pdf_name,
                "PDF Process Status": status,
                "KML Generation": kml_status,
                "Download Link": f"[Download KML](output_kml/{kml_file_name})" if kml_status == "Yes" else ""
            })
        
        # Display the table with statuses and links
        df = pd.DataFrame(table_data)
        st.write(df)
        
        # Zip all KML files and provide download link
        if kml_file_paths:
            zip_filename = f"kml_files_{pattadar_name}_{katha_number}.zip"
            with zipfile.ZipFile(zip_filename, 'w') as zipf:
                for file_path in kml_file_paths:
                    zipf.write(file_path, os.path.basename(file_path))
            
            # Offer the ZIP file for download
            with open(zip_filename, "rb") as f:
                st.download_button(
                    label="Download All KML Files",
                    data=f,
                    file_name=zip_filename,
                    mime="application/zip"
                )
    else:
        st.error("Please upload at least one PDF file and provide Pattadar Name and Katha Number.")
