[Hackathon Tracks](../README.md) / Data

# Winners data

Every sponsor prize in this index as one row: 1,697 prizes won by 1,553 projects at 60 hackathon editions from 379 sponsors.

## Files

| File | What it holds |
| --- | --- |
| [winners.json](winners.json) | One object per project and sponsor prize. Best for scripts and AI agents. |
| [winners.csv](winners.csv) | The same rows. List fields hold JSON arrays. |
| [fetch-receipts.jsonl](fetch-receipts.jsonl) | HTTP status and fetch time for every linked URL. |
| [Coverage report](../docs/coverage.md) | Which galleries were read, known gaps and link checks. |

Readable pages: [sponsors](../SPONSORS.md), [hackathons](../HACKATHONS.md) and [tech and project types](../TOPICS.md).

## Fields

| Field | Meaning |
| --- | --- |
| `project` | Project name on Devpost |
| `hackathon`, `year`, `event_slug` | Hackathon edition name, year and Devpost subdomain |
| `sponsor` | Organization that awarded the prize. `Other` when the prize names no organization |
| `prize` | Exact prize label from the Devpost gallery |
| `prize_value` | Placement or value stated in the label, or null |
| `description` | What the project does, from its Devpost page |
| `sponsor_integration` | Documented sponsor use or a sponsor product listed in Built With |
| `use_source`, `use_quote` | Source field and exact supporting excerpt for a sponsor use note |
| `summary`, `summary_evidence` | Description plus integration note, and how well the source supports it |
| `sponsor_tech` | Built With tags that belong to the sponsor |
| `built_with` | All Built With tags on Devpost |
| `team_size` | Number of team members, or null |
| `event_prizes`, `event_prize_count` | Every prize the project won at that hackathon |
| `required_tech`, `requirement_source` | Tech or brief the track required, and where that came from |
| `source_urls`, `demo_video_urls` | Code and demo video links that returned HTTP 200 |
| `source_link_count_listed`, `demo_video_count_listed` | How many code and video links Devpost listed |
| `url`, `gallery_url`, `rules_url` | Devpost project page, winners gallery and prize rules |
| `award_evidence` | `Devpost Winner label`, or `Sponsor-reported prize` for a prize confirmed by the sponsor |
| `fetched_on`, `http_status` | Date the project page was read and its HTTP status |

## Notes

- A project that won several sponsor prizes at one hackathon has one row per prize.
- `sponsor` is `Other` for 3 prizes credited to an individual or to no organization. Sponsor counts leave it out.
- 1 prize came from a sponsor report instead of a Devpost Winner label; `award_evidence` marks it.
- Rebuild instructions are in [scripts/README.md](../scripts/README.md).
