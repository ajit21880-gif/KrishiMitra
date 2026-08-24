# KrishiMitra AI --- Hyperlocal Agri-Mandi & Input Assistant

Version: 1.0 Purpose: Production implementation specification
(IMPLEMENT.md)

## Overview

KrishiMitra AI is a multilingual, voice-first agritech platform for
farmers, traders, FPOs, fertilizer dealers, and government extension
officers across India.

Primary objective:

-   Fetch **live mandi grain prices** from **official Government
    sources** (AGMARKNET, data.gov.in, eNAM where applicable).
-   Support **voice and text** in multiple Indian languages.
-   Automatically detect the spoken language and respond in the same
    language.
-   Connect farmers with verified buyers and agricultural input dealers.

------------------------------------------------------------------------

# Core Modules

## Farmer Module

Features: - Voice query - Text query - Live mandi rates - MSP
comparison - Nearby mandi comparison - Weather advisory - Crop advisory

Example:

> "What is today's maize rate in Shimoga?"

Response:

-   Modal Price
-   Minimum Price
-   Maximum Price
-   MSP
-   Source
-   Last Updated

------------------------------------------------------------------------

## Trader Module

Features: - Compare prices across multiple mandis - Daily price trends -
Bulk purchase opportunities - Verified sellers - Commodity analytics

------------------------------------------------------------------------

## Buyer Marketplace

Buyer profile includes: - Company Name - GST Verification - Mobile
Number - WhatsApp - Commodity - District - Rating - Payment Terms

Filters: - Commodity - Distance - Exporter - Processor - Immediate
Pickup

------------------------------------------------------------------------

## Fertilizer & Input Dealers

Search: - Urea - DAP - NPK - Seeds - Pesticides

Dealer card: - Shop Name - Stock Availability - Distance - Phone -
Navigation

------------------------------------------------------------------------

# Multilingual Support

Supported Languages

  Language    Code
  ----------- ------
  English     en
  Hindi       hi
  Kannada     kn
  Marathi     mr
  Tamil       ta
  Telugu      te
  Malayalam   ml
  Gujarati    gu
  Punjabi     pa
  Bengali     bn

## Language Logic

1.  User speaks.
2.  Convert speech to text.
3.  Detect language.
4.  If confidence \>80%, use same language.
5.  Otherwise ask user to select default language.
6.  Save preference.

------------------------------------------------------------------------

# Voice AI

Speech to Text: - Whisper

Language Detection: - Whisper + FastText

Translation: - IndicTrans2 / NLLB

Text to Speech: - Azure or Google TTS

------------------------------------------------------------------------

# Location Selection

Mandatory hierarchy:

State → District → Taluka (optional) → APMC / Mandi → Commodity

The dropdown values must come from official mandi master datasets.

------------------------------------------------------------------------

# Government Data Integration

Priority:

1.  AGMARKNET
2.  data.gov.in
3.  eNAM
4.  State APMC APIs

Rules:

-   Never hardcode prices.
-   Never hallucinate values.
-   Always display source.
-   Cache responses for 30 minutes.

Example API flow:

User → State → District → Mandi → Commodity → Government API → AI
Formatting → Voice + Text

------------------------------------------------------------------------

# Database Schema

## users

``` sql
id UUID PRIMARY KEY,
name TEXT,
mobile TEXT,
preferred_language TEXT,
state TEXT,
district TEXT,
village TEXT,
created_at TIMESTAMP
```

## mandis

``` sql
id UUID PRIMARY KEY,
state TEXT,
district TEXT,
mandi_name TEXT,
apmc_code TEXT,
latitude DECIMAL,
longitude DECIMAL
```

## commodities

``` sql
id UUID PRIMARY KEY,
commodity_name TEXT,
local_name TEXT,
category TEXT
```

## daily_prices

``` sql
id UUID PRIMARY KEY,
mandi_id UUID,
commodity_id UUID,
date DATE,
min_price NUMERIC,
modal_price NUMERIC,
max_price NUMERIC,
source TEXT
```

## buyers

``` sql
id UUID PRIMARY KEY,
company TEXT,
gst_number TEXT,
district TEXT,
commodity TEXT,
phone TEXT,
verified BOOLEAN,
rating NUMERIC
```

## dealers

``` sql
id UUID PRIMARY KEY,
shop_name TEXT,
fertilizer BOOLEAN,
seed BOOLEAN,
pesticide BOOLEAN,
location TEXT,
verified BOOLEAN
```

------------------------------------------------------------------------

# AI Intent Recognition

Supported intents:

  Intent    Example
  --------- ---------------
  Price     Maize rate
  MSP       Wheat MSP
  Buyer     Sell soybean
  Dealer    Need DAP
  Weather   Rain tomorrow
  Scheme    PM Kisan

Example JSON

``` json
{
  "intent":"price",
  "commodity":"Maize",
  "state":"Karnataka",
  "district":"Shivamogga",
  "language":"kn"
}
```

------------------------------------------------------------------------

# UI Screens

## Welcome

-   Logo
-   Voice Button
-   Language
-   Continue
-   Offline Mode

## Language Screen

-   Native script names
-   Search
-   Save default

## Location Screen

-   State
-   District
-   Taluka
-   Mandi
-   Commodity

## Mandi Result

Display:

-   Commodity
-   Mandi
-   Date
-   Min Price
-   Modal Price
-   Max Price
-   MSP
-   Source
-   Last Updated

------------------------------------------------------------------------

# Admin Dashboard

Modules

-   Users
-   Dealers
-   Buyers
-   Price Logs
-   Commodity Master
-   API Health
-   Voice Transcripts
-   Language Analytics

Charts

-   Top searched crops
-   Active districts
-   Buyer leads
-   API requests

------------------------------------------------------------------------

# Security

-   Firebase OTP
-   JWT
-   Role Based Access
-   API Rate Limiting
-   Voice Encryption
-   User Consent

------------------------------------------------------------------------

# Offline Mode

If internet unavailable:

-   Store voice locally.
-   Queue API request.
-   Show cached prices.
-   Display last updated timestamp.

------------------------------------------------------------------------

# Tech Stack

  Layer      Technology
  ---------- ---------------
  Frontend   Next.js 15
  Mobile     React Native
  Backend    FastAPI
  AI         GPT-5
  Voice      Whisper
  Database   PostgreSQL
  Cache      Redis
  Search     Elasticsearch
  Storage    S3
  Maps       Google Maps

------------------------------------------------------------------------

# Implementation Roadmap

## Phase 1 (Weeks 1--2)

-   Project setup
-   Authentication
-   Language detection
-   Voice input
-   State/District/Mandi
-   Government API integration

## Phase 2 (Weeks 3--4)

-   Buyer marketplace
-   Dealer module
-   WhatsApp integration
-   Notifications
-   Admin dashboard

## Phase 3 (Weeks 5--6)

-   Price prediction
-   Crop disease detection
-   Weather alerts
-   Analytics
-   AI recommendations

------------------------------------------------------------------------

# Deployment

-   Docker
-   Nginx
-   GitHub Actions CI/CD
-   PostgreSQL
-   Redis
-   SSL
-   Swagger Documentation

------------------------------------------------------------------------

# Acceptance Criteria

-   Voice works in 10+ Indian languages.
-   Official mandi prices only.
-   Language auto-detection.
-   Buyer & dealer marketplace.
-   MSP calculator.
-   Offline caching.
-   Admin dashboard.
-   Production-ready architecture.
