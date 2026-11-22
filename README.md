# Hackathon Tracks

![Hackathon Tracks. Pick the track before the idea.](docs/tracks-banner.png)

Past hackathon winners, organized by the sponsor prize they won, so you can see what judges rewarded before you pick your next project.

Project entries link to Devpost and explain how the team used the sponsor's tech where the Devpost write-up says. Code is linked where public.

<!-- BEGIN coverage -->

![1,553 winning projects](https://img.shields.io/badge/Winning%20projects-1,553-0F2A4A) ![60 hackathon editions](https://img.shields.io/badge/Hackathon%20editions-60-3B82F6) ![379 sponsors](https://img.shields.io/badge/Sponsors-379-0F2A4A) ![1,697 sponsor prizes](https://img.shields.io/badge/Sponsor%20prizes-1,697-3B82F6)

<!-- END coverage -->

A winning project is one Devpost URL at one hackathon edition, identified by its event slug. The sponsor count includes distinct named sponsors. The `Other` group covers individual or unattributed prizes.

**[Search every winner at tracks.azizu.dev](https://tracks.azizu.dev/)**

<!-- BEGIN directory -->

## Browse

| Start with | What you get |
| --- | --- |
| **[By sponsor](SPONSORS.md)** | 379 sponsors, A to Z. See what won and what the Devpost write-ups say about sponsor tech. |
| **[By hackathon](HACKATHONS.md)** | 60 editions of 23 hackathons, with every sponsor track and its winners. |
| **[By tech or project type](TOPICS.md)** | Health, finance, hardware, voice and more, plus the most used tech. |
| **[Search the site](https://tracks.azizu.dev/)** | Filter all 1,553 winners by sponsor, hackathon, year and tech. |

## Top sponsors

| Sponsor | Winning projects | Hackathons |
| --- | --- | --- |
| [Google](winners/by-sponsor/google.md) | 71 | 41 |
| [Fetch.ai](winners/by-sponsor/fetch-ai.md) | 65 | 11 |
| [Wolfram](winners/by-sponsor/wolfram.md) | 38 | 6 |
| [Solana](winners/by-sponsor/solana.md) | 29 | 22 |
| [Capital One](winners/by-sponsor/capital-one.md) | 28 | 21 |
| [GoDaddy Registry](winners/by-sponsor/godaddy-registry.md) | 28 | 27 |
| [Snap](winners/by-sponsor/snap.md) | 25 | 8 |
| [Figma](winners/by-sponsor/figma.md) | 24 | 6 |
| [Regeneron](winners/by-sponsor/regeneron.md) | 24 | 2 |
| [MongoDB](winners/by-sponsor/mongodb.md) | 22 | 22 |
| [ElevenLabs](winners/by-sponsor/elevenlabs.md) | 21 | 20 |
| [Spacetime](winners/by-sponsor/spacetime.md) | 17 | 3 |

[See all 379 sponsors](SPONSORS.md)

<!-- END directory -->

## Pick your tracks

1. **List your event's sponsor tracks.** Check its Devpost page and rules for each track's required tech and judging criteria.
2. **Read what won before.** Open each sponsor in [the sponsor list](SPONSORS.md) to see what past winners built and look for sponsor-use notes.
3. **Score your ideas.** Copy the [track matrix](templates/track-matrix.md) and mark each idea against each track. Pick the smallest build you can demo that fits two to four tracks.

## Use it with your AI agent

The whole index is one file per format, ready for Claude Code, Codex or any agent that can read a URL:

- [winners/winners.json](winners/winners.json) · [raw](https://raw.githubusercontent.com/azizu06/hackathon-tracks/main/winners/winners.json)
- [winners/winners.csv](winners/winners.csv) · [raw](https://raw.githubusercontent.com/azizu06/hackathon-tracks/main/winners/winners.csv)

Each row is one project and one sponsor prize it won. The fields you will use most:

| Field | What it holds |
| --- | --- |
| `project`, `url` | Project name and Devpost page |
| `hackathon`, `year` | Where and when it won |
| `sponsor`, `prize` | Who awarded the prize and its exact Devpost label |
| `description` | What the project does |
| `sponsor_integration` | Documented sponsor use or a sponsor product listed in Built With |
| `use_source`, `use_quote` | Source field and exact supporting excerpt |
| `built_with`, `sponsor_tech` | All tech tags, and the ones that belong to the sponsor |
| `source_urls`, `demo_video_urls` | Verified code and demo video links |
| `required_tech` | What the track asked for, when captured |

The [data guide](winners/README.md#fields) lists every field.

Example prompt:

```text
Read https://raw.githubusercontent.com/azizu06/hackathon-tracks/main/winners/winners.json.
My hackathon has tracks from Google, ElevenLabs and Snowflake. For each sponsor, show
three past winners with their prize, what they built and how they used the sponsor's
product. Then suggest two project ideas that could fit at least two of these tracks.
```

For a full workflow, give your agent the [track picker prompt](prompts/track-picker.md).

## Contributing

[Open an issue](https://github.com/azizu06/hackathon-tracks/issues/new) to add a missing winner or fix a record. Include the Devpost project URL, the hackathon and the exact prize label. [scripts/README.md](scripts/README.md) explains how to rebuild the index, and the [coverage report](docs/coverage.md) lists known gaps.

## License

[MIT](LICENSE). Maintained by [@azizu06](https://github.com/azizu06). Project details come from public Devpost pages.
