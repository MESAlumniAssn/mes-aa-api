# MES Alumni Association 

[![Build Status](https://app.travis-ci.com/MESAlumniAssn/mes-aa-api.svg?branch=main)](https://app.travis-ci.com/MESAlumniAssn/mes-aa-api)

## Setting up the api
1. Clone the repository - `git clone https://github.com/MESAlumniAssn/mes-aa-api`
2. Create a virtual environment - `python -m venv venv`
3. Activate the virtual environment - `venv\Scripts\activate` (windows) or `source venv/bin/activate` (Linux/MacOS)
4. Install the project dependencies - `pip install -r requirements.txt`
5. Create the environment variables in a `.env` file. Refer to the `.env.example` file for the list of variables
6. Run the project - `uvicorn app.main:app --reload`

Refer to the [Documentation site](https://mesalumniassn.github.io/docs) for the full documentation.
