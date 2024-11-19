# AIO PDF Tools Web Application
## Introduction
#### AIO PDF Tools is a versatile web application designed to simplify PDF management through a user-friendly interface. 
#### Initially developed as a command-line interface (CLI) tool, it has evolved into a robust web application utilizing Flask, Docker, and Vercel hosting[live website](https://aiopdftools.vercel.app/). 
#### This project aims to enhance skills in web application development while providing essential features for handling PDF files. Contributions are encouraged to improve both the backend and frontend functionalities.
## Features
#### • Merge PDFs: Combine multiple PDF files into a single document.
#### • Image to PDF Conversion: Convert images into PDF format seamlessly.
#### • PDF Encryption: Secure your PDF files with password protection.
#### • PDF to Image Conversion: Transform PDF pages into image files.
#### • PDF Splitting: Divide PDFs into specific pages or designated ranges.
## Setup Instructions
## Prerequisites:-
### Before setting up the application, ensure the following software is installed on your machine:
- [Git](https://git-scm.com/)
- [Docker](https://www.docker.com/get-started)
- [python](https://www.python.org/downloads/)
### Clone the Repository
#### To clone the repository, run the following commands in your terminal:
```
git clone https://github.com/your-username/AIO-PDF-tools-web
```
```bash
cd AIO-PDF-tools-web
```
### Setting Up Without Docker
#### For those who prefer not to use Docker, you can set up the application using a virtual environment:
#### Create a virtual environment:
```bash
python -m venv venv
```
#### Activate the virtual environment:
On Windows:
```bash
venv\Scripts\activate
```
#### On Unix-based systems (Linux/macOS):
```bash
source venv/bin/activate
```
##### Install the required dependencies:
```bash
pip install -r requirements.txt
```
#### Run the application:
```bash
python app.py
```
#### The application will be accessible at http://localhost:5000.

### Setting Up with Docker
If you choose to set up using Docker, follow these steps:
#### Build the Docker Image:
```bash
docker build -t flaskapp .
```
##### Run the Docker Container:
For Windows:
```bash
docker run -d -p 5000:5000 -v %cd%:/app flaskapp
```
For Unix-based systems (Linux/macOS):
```bash
docker run -d -p 5000:5000 -v $(pwd):/app flaskapp
```
#### Accessing the Application
###### Open your web browser and navigate to http://localhost:5000 to access the application.
![image](https://github.com/user-attachments/assets/8624843a-bf03-4ee6-9985-c985c7241337)

### Contributions
#### Contributions are highly valued! Feel free to fork the repository and submit a pull request with your improvements or bug fixes. Whether enhancing the backend (Flask) or improving the front end, your efforts will significantly benefit the project.
