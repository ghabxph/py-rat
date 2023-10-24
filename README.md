# Python RAT for Personal Use

## Setting Up

Create virtual environment

```
python3 -m venv venv
```

Then activate

```
source venv/bin/activate.fish
```

To update requirements.txt, just run:

```
pip freeze > requirements.txt
```

I prefer selecting the packages that I installed only rather than just keeping the frozen dependencies.

From:

```
blinker==1.6.3
click==8.1.7
Flask==3.0.0
importlib-metadata==6.8.0
itsdangerous==2.1.2
Jinja2==3.1.2
MarkupSafe==2.1.3
Werkzeug==3.0.0
zipp==3.17.0
```

To:

```
Flask==3.0.0
```

Since at the time of writing, I'm only importing flask. The other dependencies are part of flask that are explicitly installed when installing flask. But to keep things clean on high level, I'll just keep the dependencies that I know I installed myself.

## Running the app

Run the app through:

```
python src/main.py
```

Then expose the service through ngrok

```
ngrok http 9000
```

This should allow you to access this RAT on any machine to control the server for things you like to do

## Features

Currently, you can run bash commands through this program remotely via http. That's it for now.
