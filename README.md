This is a [FastAPI](https://fastapi.tiangolo.com/) project for Sales AI API integration.

## Getting Started

First, install the virtual environment:

```bash
python -m venv 'your_virtualenv'

# Windows
.\path\[your_virtualenv]\Scripts\activate

#Linux
source [your_virtualenv]/bin/activate

```

Next, install the external libraries

```bash
pip install -r requirements.txt
```

Run the server
```bash
uvicorn api.main:app --reload
```
