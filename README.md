# PDF Tools Web Application

## ● Introduction

This project provides a suite of PDF tools accessible via a web application. It started as a CLI-based project, later upgraded to a [Tkinter GUI version](https://github.com/vedantterse/AIO-PDF_tools),

and finally transformed into a [live website](https://aiopdftools.vercel.app/). This progression was driven by the desire to enhance my skills in Docker, Vercel hosting, Flask development, and general web application development. Contributions are welcome, whether for improving the backend (Flask) or the front end. 

## ● Features

- Merge multiple PDF files
- Convert images to PDF
- Encrypt PDF files with a password
- Convert PDF pages to images
- Split PDF files into specific pages or a range of pages

## ● Setup Instructions

### ●  Prerequisites

Ensure you have the following installed on your machine:

- [Git](https://git-scm.com/)
- [Docker](https://www.docker.com/get-started)
- [python](https://www.python.org/downloads/)

## ● Learn Git/GitHub

### *Don't know Git/GitHub? No problem! Learn the basics and get started with open source contributions by checking out [this repository](https://github.com/vedantterse/python).* 
### **Once you're familiar with Git/GitHub, come back and contribute to this project!**


## ● Clone the Repository

To clone the repository, run the following command in your terminal:

```bash
git clone  https://github.com/your-username/AIO-PDF-tools-web
```
```
cd AIO-PDF-tools-web
```
## ● Setting Up with Docker

### Build the Docker Image:

```bash
docker build -t flaskapp .
```
### It will take some time to build the image, as it needs to install the dependencies.

Run the Docker Container:

```
docker run -p 5000:5000 -v %cd%:/app flaskapp
```
For Unix-based systems (Linux/macOS), use:

```
docker run -d -p 5000:5000 -v $(pwd):/app flaskapp
```
## ● Access the Application

**Open your web browser and navigate to [http://localhost:5000](http://localhost:5000) to access the application.**


![image](https://github.com/vedantterse/AIO-PDF-tools-web/assets/69134828/17c23308-db50-4762-8e6b-eb2c5b922841)


##### If you encounter any issues while running the app, please open an issue on the repository with a detailed explanation of your problem.
We appreciate your feedback and contributions!

### ● **Live Reload**

**For live reloading when making changes to the backend or frontend files, ensure your Docker run command includes volume mounting as shown above.**

**This setup will reflect changes without needing to restart the container.**

## ● Contributions
Contributions are welcomed and appreciated! Feel free to fork the repository and create a pull request with your improvements or bug fixes. 

Whether you want to update the backend (Flask) or enhance the front end, your efforts are valuable.

Acknowledgments
This project was developed with the assistance of AI tools like ChatGPT.


