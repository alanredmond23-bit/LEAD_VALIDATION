# Lead Validation Audit Tools

This folder contains the assets and instructions for the "Anthony Lead Forensics" workflow to validate a vendor lead file (pet/dental “free scan/review”) and generate evidence suitable for publisher disputes or refunds.

## Contents
- `agent prompt.md` — the system/agent prompt that defines the mission, inputs, and anomaly logic.
- `LEADVALIDATIONREADME.md` — this guide (how to run and what to expect).

Additional outputs you will generate during analysis:
- `addresses_with_multiple_lastnames.csv`
- `top_surname_clusters.csv`
- `high_risk_ips.csv`
- `lead_anomalies_ranked.csv`

## Input data locations (local machine)
- `/Users/alanredmond/Desktop/anthony`
- `/Users/alanredmond/Desktop/anthony audit`

Expected input files:
- `pet data 1.xlsx` (original)
- `unique_ips_top500.csv` (IP + count)
- Later: `ip_enriched_full.csv` (after running the IP enrichment script)

## Column mapping (important)
In `pet data 1.xlsx`:
- `time stamp` = IP address
- `ip address` = HH:MM:SS
- `generation date` = date

Always build a real datetime by combining: `generation date` + `ip address` (HH:MM:SS).

## Core steps
1. Load the Excel and normalize column names.
2. Produce slices:
   - Top surnames (look for spikes like 181 WILSON)
   - Addresses with multiple distinct last names
   - Top IPs with counts
3. Run IP enrichment in batches (free API):
   - Base: `http://ip-api.com/json/{query}`
   - Fields: `status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,proxy,hosting,query`
   - Respect rate limit 45 req/min → batch 40, sleep 60s.
   - Save as `/Users/alanredmond/Desktop/ip_enriched_full.csv`.
4. Join `ip_enriched_full.csv` back to the Excel by IP.
5. Flag/score anomalies:
   - IP has `proxy=true` or `hosting=true` → high
   - IP ASN/org is cloud/DC → high
   - Address has >1 distinct last name → high
   - Surname frequency is abnormally high → medium/high
   - Bursty timestamps (hundreds in the same minute) → medium
   - Phone last4 sequences → medium
   - Missing ad/UTM/referrer fields → supporting evidence
6. Export the four CSVs listed above.

## Evidence summary to produce
Provide a short summary that includes:
- % of leads from suspect IPs
- List of suspect addresses
- List of overrepresented surnames
- Recommendation: “dispute/refund N leads.”

## Drive / Notion handoff (optional)
If asked to “put slices in Drive/Notion,” create or use a folder named `anthony-lead-forensics` and upload:
- The four anomaly CSVs
- This README
- The XLSX structure report

For the full mission narrative and decision logic, see `agent prompt.md`.
