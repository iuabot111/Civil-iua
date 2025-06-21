#!/bin/bash

TOKEN="123456:7336468743:AAEscQiBQMaY9pvgKt9SVKP1B-EoDrfZD6k"
URL="https://civil-iua-production.up.railway.app"

curl -X POST "https://api.telegram.org/bot$TOKEN/setWebhook?url=$URL/$TOKEN"
