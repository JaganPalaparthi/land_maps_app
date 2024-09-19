# Land Maps PDF to KML Converter

This application processes PDF files to extract land coordinates, LP Numbers, total extents, and other information to generate KML files that represent these locations. The app is built using Streamlit for the front end and handles PDF extraction using `PyPDF2`.

## Features

- Extracts LP Numbers and total extents from uploaded PDFs.
- Creates KML files with the extracted data, including polygons and placemarks.
- Allows users to download individual KML files or a ZIP archive of all KMLs.
- Custom file names including Pattadar Name and Katha Number inputs from the user.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine or a Docker container.

### Prerequisites

- Python 3.10+
- Docker (optional if you prefer Docker over a local Python environment)

### Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/land-maps-kml.git
cd land-maps-kml
