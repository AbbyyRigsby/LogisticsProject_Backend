# Logistics Path Tracking API

## Purpose

The purpose of this program is to allow a requestable API for users to determine the shortest travel time between ports, taking into account both seaports and airports.

## On Startup

On API startup, the API will take existing datasets to make a Pandas Dataframe. Then, using that data, will make a **K-Nearest Neighbors Graph** using NetworkX with a default value of 10.


## Composing Docker File 

The dockerfile container is made for the following use-cases:

- deployment: allows for easier deployment to local servers
- ease of local-testing
