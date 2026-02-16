# Nexus Factory POC

This repository now includes a runnable proof of concept for a manufacturing assistant focused on:
- parsing unstructured plant updates
- surfacing bottlenecks and logistics delays
- flagging likely at-risk customer orders

## Quick Start

Run a one-shot query:

```powershell
python run_poc.py --question "where are the bottlenecks?"
```

Start interactive mode:

```powershell
python run_poc.py
```

Use deterministic date logic (useful for demos):

```powershell
python run_poc.py --as-of 2026-02-16 --question "order risks"
```

Launch the dashboard view:

```powershell
python run_dashboard.py --as-of 2026-02-16
```

Then open `http://127.0.0.1:8787/` in your browser.

The dashboard is AI-powered end-to-end: each bottleneck, shipment delay, and order risk includes a **We have an answer** button that generates a context-specific recovery plan.

## Data Inputs

The POC reads plain text files from `data/unstructured/`:
- `shift_report_morning.txt`
- `logistics_update.txt`
- `orders_digest.txt`
- `maintenance_note.txt`

Add more `.txt` files with similar phrasing to simulate additional plants, shifts, and exceptions.

## Landing Website

A public-facing website for outreach interviews is available at `docs/site/`.

Run locally:

```powershell
python -m http.server 8090 --directory docs/site
```

Then open `http://127.0.0.1:8090/`.

The interview form opens a prefilled email draft. Set your team inbox in `docs/site/index.html` by updating `TEAM_CONTACT_EMAIL`.

## Virtual Twin Research Notes

Vetted starter options for manufacturing line virtual twins are listed in:

- `docs/virtual-twin-options.md`

## Tests

Run unit tests:

```powershell
python -m unittest discover -s tests
```
