# Smart-Kitchen APP

## Project Overview

Smart-Kitchen APP is a web application designed to help you generate some idea about food recipes based on the ingredients you have in your kitchen. This application uses machine learning models to suggest recipes that you can prepare with the available ingredients.

## Getting Started

You can download the models from the following [Link Models](https://drive.google.com/file/d/1xvsD3ahpbGbT3L5xywdYzfckQzmDIugD/view?usp=sharing)

After downloading, extract the contents of the zip file into the models/ folder.

Don't forget to create some sub-folders for db/ in the root directory to store the database files, because we are using SQLite for this project (serverless database).

## Installing Required Packages

After all directories are set up, you can continue by downloading the required packages using the following command:

```bash
pip install -r requirements.txt
```

## Running the Application

After installing the required packages, you can run the application using the following command:

```bash
python app.py
```

or using (if you want to run the server with proxy like tailscale or ngrok):

```bash
python server.py
```

Now you can access the application in your web browser at `http://localhost:5000` or the provided proxy URL.

Enjoy using the Smart-Kitchen APP!