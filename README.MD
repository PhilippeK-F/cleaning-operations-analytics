# Cleaning Operations Analytics

Projet data simulant le pilotage d'opérations de nettoyage industriel.

L’objectif est de construire un pipeline simple :
- génération de données réalistes
- stockage PostgreSQL
- visualisation via un dashboard interactif

## Stack

- Python (Pandas, SQLAlchemy)
- PostgreSQL (Docker)
- Streamlit
- Plotly

## Fonctionnalités

- Génération de tâches de nettoyage (sites, zones, équipes)
- Calcul de scores de priorité et de qualité
- Dashboard interactif avec :
  - KPIs opérationnels
  - suivi des tâches dans le temps
  - répartition par zone / équipe
  - carte des sites (géolocalisation)
  - détection des tâches critiques
- Page dédiée performance des équipes

## Lancer le projet

```bash
docker compose up -d / http://localhost:8501

## Auteur :

Philippe Kirstetter-Fender