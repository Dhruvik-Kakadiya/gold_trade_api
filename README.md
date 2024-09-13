
# 🏅 PlusGold - Gold Trade API with Superpowers!

Welcome to PlusGold - the gold trading platform that makes trading shiny assets as easy as eating pie! 🍰 We’ve put together a backend API that’s not just another trading platform, but a supercharged, turbo-powered, and (hopefully) fun experience! Dive in, and let’s get shiny! ✨

## 🌟 Features

- **User Registration & Authentication:** We’ve got your back with JWT-based authentication. Trade with peace of mind—no leaks, no hacks, nada!


- **Real-time Gold Prices:** Fetches gold prices from a super-reliable public API (via Redis cache, for ultra-fast responses 🚀).

- **Buy/Sell Gold API:** Convert your hard-earned cash into gold (and vice versa) with a flick of your fingertips. Grams, ounces? We've got you covered. 💰


- **Transaction History:** Because you deserve to keep tabs on your bling transactions. Paginated to perfection. 📜


- **Concurrency Control:** No double-spending here! We use Redis locks and multithreading for the smoothest trading experience.


- **Secure and Rate-Limited:** Our API is locked and loaded with JWT tokens and rate-limiting to keep things safe and fair. 🚔


- **Dockerized:** Runs in a Docker container for easy peasy deployment. Containers are cool, right? 🐳




## Prerequisites

- [Python](https://www.python.org/downloads/) v3.8.0+
- [pip](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#installing-pip) v21.0.0+


## Setup Django Project

Clone the project

_using ssh_

```bash
git clone git@github.com:Dhruvik-Kakadiya/gold_trade_api.git
```

_or using https_

```bash
git clone https://github.com/Dhruvik-Kakadiya/gold_trade_api.git
```

Go to the project directory

```bash
cd gold_trade_api
```

Create a virtual environment

```bash
python3 -m venv ./venv
```

Activate a virtual environment

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Provide Environment variables in project root directory

```bash
cp .env.sample .env
gedit .env
```


## Run using runserver


Run the migrations first

```bash
python manage.py migrate
```

Install redis-server for caching (For Ubuntu)

```bash
sudo apt install redis-server
```

Start redis-server service for caching (For Ubuntu)

```bash
sudo systemctl start redis
```

To run the python server

```bash
python manage.py runserver
```

To create your admin user

```bash
python manage.py createsuperuser
```

## Run using Docker
> **Note**
> uncomment the redis host environment configurations for docker from the .env

Build a docker image

```bash
docker-compose build
```

Now, to run docker containers in daemon mode using docker compose file, run this command

```bash
docker-compose up -d
```
