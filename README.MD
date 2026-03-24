# Industrial Cleaning Operations Analytics

A small data project to monitor and prioritize industrial cleaning operations.

## Stack

- Python
- PostgreSQL
- Streamlit
- Docker
- Pandas
- SQLAlchemy
- Plotly

## Project Goal

This project simulates an operational analytics tool for industrial cleaning.

It helps answer questions such as:
- Which zones should be cleaned first?
- Which teams are the most loaded?
- Which sites have lower quality scores?
- How many tasks are delayed?

## Architecture

CSV → Python ingestion → PostgreSQL → Streamlit

## Features

- realistic cleaning task generation
- PostgreSQL storage
- interactive Streamlit dashboard
- priority scoring logic
- critical zone tracking

## Run the project

Start PostgreSQL:

```bash
docker compose up -d