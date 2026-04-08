# LINE Shopping List Bot

An open-source, self-hosted LINE shopping list bot built with Python (Flask) and Cloudflare Worker + D1.

This bot allows groups or families to collaboratively manage shopping lists with clear ownership, timestamps, and a simple checklist UX.

---

## Features

- Add shopping items via chat commands
- Mark items as purchased (text or checklist)
- View current shopping list
- View purchase history (last 7 days)
- Group-specific configurable keywords
- Each item is displayed as:
  
  Item Name (User, mm/dd)

Example:

Milk (L.Kung, 04/09)

---

## Architecture

LINE User
  ↓ Webhook
Python Flask App (line-bot-sdk v3)
  ↓ HTTP
Cloudflare Worker API
  ↓
Cloudflare D1 (SQLite)

Responsibilities:

- Handler: LINE events and UX responses
- Service: business logic
- Repository: data access abstraction
- Worker: API and database access only

---

## Project Structure

.
├── main.py
├── handlers
│   ├── text.py
│   ├── user_profile.py
│   └── buy_keyword_provider.py
├── shopping
│   ├── service.py
│   ├── repository.py
│   └── d1_repository.py
├── linebot_core
│   └── flask_app.py
└── README.md

---

## Design Principles

1. Configuration over hardcoding  
   All command keywords are stored in the database and resolved dynamically.

2. Clear separation of concerns  
   LINE interaction, business logic, and data access are separated.

3. Stable identifiers  
   Checklist actions always use item_id to avoid ambiguity.

---

## Supported Commands

Add item:

要買 牛奶  
要買 牛奶, 衛生紙  

Complete item:

已買 牛奶  

or click the checklist button.

View list:

清單

View history:

歷史

Help:

help  
?  
購買清單使用方法  

or click the help button in the list.

---

## Display Convention

All lists follow this format:

Item Name (User Display Name, mm/dd)

Examples:

- Milk (L.Kung, 04/09)
- Detergent (Mom, 04/08)

---

## Database Schema (D1)

Table: shopping_items

- id
- conversation_id
- item_name
- created_by
- created_at
- completed_by
- completed_at
- status (pending / completed)

Table: system_settings

- buy_keywords
- complete_keywords

---

## Environment Variables

Python app:

CHANNEL_ACCESS_TOKEN  
CHANNEL_SECRET  
D1_API_BASE_URL  
D1_API_KEY (optional)

Cloudflare Worker:

- Bound to a D1 database containing:
  - shopping_items
  - system_settings

---

## Getting Started

1. Create a LINE Messaging API channel  
2. Deploy the Cloudflare Worker and bind a D1 database  
3. Deploy the Python app (Render or any hosting platform)  
4. Set required environment variables  
5. Set the LINE webhook URL to the Python app

---

## Contributing

Contributions are welcome.

- Fork the repository
- Create a feature branch
- Keep changes small and readable
- Submit a pull request

Please keep UI logic in handlers and business logic in services.

---

## License

This project is open source.

You may choose a license such as MIT or Apache-2.0 and add a LICENSE file.

---

## Status

Production-ready and designed for long-term maintainability.
