# mclauncher - Launcher for Minecraft Server on Google Cloud

## Objective

### Goals

To launch Minecraft server on Google Compute Engine anytime when players want to play.
And to cut cost down, shutting down the server as all the players disconnected.

### Requirements

* Allowlisted players can launch the server anytime via a web interface.
* Shut the server down automatically when all the players left.
* Notify players of the events and the IP address of the server.
* Low infrastructure cost. Zero cost is the best if possible.

### Non-goals

* Managing Minecraft server such as upgrading, back-ups and availability.

## Background

Running Minecraft servers costs us.
If we could run the server during we want to play, we would minimize the cost.

## Overview

Simple web app with a single page app and a RESTful API.

## Infrastructure and storage

To reduce infrastructure cost and to reduce operational cost, I prefer serverless platforms and use free tier of them.

* Cloud Run - to host the SPA and the API as a service.
* Cloud Scheduler - to check how many players are connecting regularly.
* Cloud Firestore - to store the server list and the allowlist of players.
* Firebase Authentication - to authenticate players.

## Detailed designs

### API

I chose Python and FastAPI because:

* Python - I want to learn Python
* [Fast API](https://fastapi.tiangolo.com/ja/) - is high performance, modern and well integrated for RESTful JSON APIs. Auto-generated OpenAPI and type hints are also great features.

It should be implemented with the path prefix `/api` of the app.

* `GET /api/v1/server` - returns the status of the server that includes the list of players connecting.
* `POST /api/v1/servers/start` - start the server.

It has versioning APIs with the path prefixes like `/v1` to be easily managed on codes and analysis.

It should be configured with environment variables.

* `INSTANCE_NAME` - the instance name of the Minecraft server.
* `INSTANCE_ZONE` - the zone where the instance is placed.

### Web frontend

Just plain React app with TypeScript.
It should be distributed as static files of the App.

## Security and privacy

It must allow only restricted players to use. If anyone could use it, anyone would be able to control the GCE instance.

To avoid that situation, authenticate users of this app with Firebase Authentication and authorize them with the token from it.

## Caveat

Firebase Authentication's project must be separated from other Google Cloud services because [Blaze plan](https://firebase.google.com/pricing) cost it, but Spark doesn't.
