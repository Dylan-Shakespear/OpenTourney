# OpenTourney
Open Tourney is an in-development web-based tournament manager built with Python (Django)

# Setting up your local environment

To clone this repository, run the following command on your git enabled terminal
```bash
git clone https://github.com/Dylan-Shakespear/OpenTourney.git
```

Navigate into `OpenTourney/OpenTourney` Download python, pip, django, and dotenv
```bash
sudo apt install python3-pip -y
```
```bash
pip install django
```
```bash
pip install python-dotenv
```



## Secret Key (Optional)
Create a .env file in the project's root directory. Open the file and add the following line:
`SECRET_KEY=mysecretkey`
Replace `mysecretkey` with a secure and unique string of your choosing. You can use a tool like Django Secret Key 
Generator to generate a random secret key.

Save and close the .env file.

If you do not do this, the project will still run, just with a filler (not secure) secret key.

## DB and Running Server

This repository comes with a DEMO database. It is recommended you delete the migrations and database and create a new
one. Otherwise you can now start the server.
```bash
python3 manage.py runserver
```