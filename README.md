# Crypto Price Tracker Automation

An automated workflow built with n8n that tracks Bitcoin and Ethereum prices every hour and saves them to Google Sheets automatically.

## What it does
- Fetches live Bitcoin and Ethereum prices from CoinGecko API
- Runs automatically every hour
- Saves all data to Google Sheets
- Zero manual work required

## Tools Used
- n8n (automation)
- CoinGecko API (crypto prices)
- Google Sheets (data storage)

## How it works
1. Schedule Trigger fires every hour
2. HTTP Request fetches live prices from CoinGecko
3. Google Sheets node saves the data automatically

## How to use
1. Import My workflow 2.json into your n8n instance
2. Connect your Google Sheets account
3. Activate the workflow

## Author
Built by Sar — engineering student building AI automations in public
