# TRACKS inference pass

Coverage compared with `3420589` on `coverage-r3`. Each count is a prize row.

| Sponsor note tier | Before | After |
| --- | ---: | ---: |
| Shown | 1,034 | 1,034 |
| Inferred | 0 | 25 |
| Award-only | 539 | 514 |
| Not stated | 124 | 124 |
| **Total** | **1,697** | **1,697** |

Shown includes 994 full notes and 40 Built With notes before and after.

## Award-only review

| Outcome | Rows |
| --- | ---: |
| Examined | 539 |
| Qualified | 25 |
| Skipped as non-tech | 482 |
| Skipped as unclear | 32 |

I screened every award-only row against its exact prize label and available challenge criteria, then checked the eligible or ambiguous rows against the cached Devpost narrative, gallery captions and Built With tags. I followed up on promising rows with their own linked READMEs and captions where available. Challenge rules established which product or input a prize was about. The evidence quotes below come from the projects.

Non-tech includes category and theme awards, recruiting and subscription awards, and challenges open to any implementation or a third-party platform. Unclear includes tech-linked prizes where the available feature evidence could not identify the sponsor product, and cases where the public rules left the supplied resource unspecified.

For example, ADLOVIN documented ad feature extraction without identifying AppLovin’s supplied files. The two Kensho election winners described candidate speeches or supplementary Wikipedia analysis without identifying a Kensho-supplied dataset. Hashling wrote its own benchmark messages. TrustEstate AI used a mock property file in its demo. These rows retain their award notes.

Selected public prize criteria for challenge datasets are linked here. [AppLovin Query Planner](https://docs.google.com/document/d/1k1J3HrCThfZyI2PdwgSOwGpT0Vt8Wv_QPhexhhZSatE/edit), [Bloomberg Industry Group at Bitcamp](https://bitcamp2024.devpost.com/), [CSE Network Traffic Exploration](https://hackthenorth2025.devpost.com/), [CSE Log & Order and RBC Signal in the Noise](https://hackthenorth2026.devpost.com/), [EOG Beat the Shutdown](https://github.com/nihaal419/HackUTD-ZeroDay), [EOG CauldronWatch](https://hackutd2025.eog.systems/), [Toyota and EOG at HackUTD Ripple Effect](https://ripple.hackutd.co/), [Tesla at TreeHacks](https://treehacks-2025.devpost.com/).

The 25 notes cover 24 projects and cite 22 Devpost rows, two GitHub README rows and one demo-caption row. VisionGuard has two qualifying Tesla prize rows. Its linked repository also includes the Tesla Video Q&A question CSV and sample submission. The TSV files preserve the exact project, edition, prize and source text used for each note. [Reviewed notes](scripts/inferred-uses.tsv), [Source excerpts](scripts/inferred-evidence.tsv).

## 15 randomly sampled inferred rows

Sampled without replacement from the 24 qualifying projects in export order, using each project’s first inferred prize row and seed `3420589`. Quotes preserve the source wording with whitespace normalized.

### 1. FUELICIENT

**Toyota Financial Services** · Toyota

Likely used the Toyota challenge’s fuel-economy data for exploring vehicle fuel efficiency and saving each user’s previous analyses (inferred from the write-up).

> FUELICIENT gives a clean UI for Toyota fuel-efficiency data exploration, coupled with a system for retaining previous analyses on a per-account basis.

[Evidence](https://devpost.com/software/fuelicient)

### 2. Minny

**Communications Security Establishment** · CSE: Log & Order

Likely used CSE’s Log & Order dataset for testing whether the log analyzer could find the challenge’s planted security incident (inferred from the write-up).

> Finding the incident planted in the CSE dataset was table stakes

[Evidence](https://devpost.com/software/minny)

### 3. Duck Duck Goose

**AppLovin** · AppLovin: Query Planner Challenge

Likely used AppLovin’s simulated ad-event dataset and benchmark queries for testing a faster DuckDB query planner (inferred from the write-up).

> we achieve a ~1300x speedup compared to the baseline implementation (~45s to ~30ms) on an M3 Pro with 18 GB RAM.

[Evidence](https://devpost.com/software/duck-duck-goose-jelxr9)

### 4. ContractScope

**Bloomberg Industry Group** · Best AI Powered Solution for Defense Contracts - Bloomberg Industry Group

Likely used the Bloomberg Industry Group challenge’s Defense Department contract notices for parsing government contract details with an NLP model (inferred from the write-up).

> a scheduled function to scrape the latest contracts from the DOD website. These contracts were then fed into our custom NLP model

[Evidence](https://devpost.com/software/contractscope)

### 5. Trace

**Communications Security Establishment** · CSE: Log & Order

Likely used CSE’s Log & Order dataset for testing whether the detector could uncover incidents in unlabeled Apache logs (inferred from the README).

> It uncovered a hidden 22-event, multi-stage attack across 180,800 unlabeled Apache log entries

[Evidence](https://github.com/JeremyFriesenGitHub/htn26)

### 6. PipeBrAIns

**EOG Resources** · EOG Resources

Likely used EOG Resources’ Hydrate Detection Challenge datasets for training a model to flag possible hydrate blockages in pipes (inferred from the write-up).

> With this, our trained model was able to predict possible hydrates in the pipes

[Evidence](https://devpost.com/software/pipebrains)

### 7. HorizonX

**Tesla** · Tesla: Excellence Prize

Likely used Tesla’s Real-World Video Q&A dataset for answering challenge questions by sampling frames from short driving clips (inferred from the write-up).

> We sample frames at fixed intervals from short driving videos—here, five frames from a nominal 5-second clip.

[Evidence](https://devpost.com/software/horizonx)

### 8. Athena

**NSA** · NSA: Hearsay: The Audio Authentication Challenge - 2nd Place

Likely used the NSA HEARSAY evaluation dataset for benchmarking whether its detector could distinguish real speech from synthetic speech (inferred from the write-up).

> Our NSA HEARSAY challenge model scores every 4 s of the caller's voice real-vs-synthetic

[Evidence](https://devpost.com/software/callguard)

### 9. FinRet

**RBC** · RBC: Signal in the Noise

Likely used RBC’s challenge MCP research corpus for indexing financial documents and answering questions with verified citations (inferred from the write-up).

> The harness ingests financial research from MCP data source, structures the corpus into searchable evidence, and answers research questions with verified citations.

[Evidence](https://devpost.com/software/finret)

### 10. Rewind

**SpaceXSI** · [MLH] Build Your Hackathon A-Team with SpaceXSI

Likely used Grok Bot for matching uploaded concert clips to other fans’ videos on X (inferred from the write-up).

> Grok searches X for other fans' videos of the same moment and compares the stage, lighting and crowd in our frames against what people posted.

[Evidence](https://devpost.com/software/rewind-7ir2hn)

### 11. hearsay_hgt13

**NSA** · NSA: Hearsay: The Audio Authentication Challenge - 3rd Place

Likely used the NSA HEARSAY evaluation dataset for benchmarking a detector that scores recordings for synthetic speech (inferred from the README).

> Our submitted detector received a **0.0248 minDCF** on the organizer’s evaluator

[Evidence](https://github.com/malachiwang/hearsay_hgt13)

### 12. Hivemind

**EOG Resources** · EOG Resources Track

Likely used EOG Resources’ Beat the Shutdown dataset for forecasting when a tank will hit its limit after a pump failure (inferred from the write-up).

> Counts down to shutdown: for every failed pump, it projects when the tank will reach its limit, with a confidence range.

[Evidence](https://devpost.com/software/hivemind-lnhy8g)

### 13. YeetThePacket

**Communications Security Establishment** · CSE: Network Traffic Exploration

Likely used the CSE challenge’s MACCDC 2012 network traffic dataset for turning packet captures into evidence-backed summaries (inferred from the write-up).

> End‑to‑end pipeline from PCAP ingestion to evidence‑backed AI narratives, running reliably on real data (MACCDC 2012).

[Evidence](https://devpost.com/software/nocapnethack)

### 14. Pew Pew

**Communications Security Establishment** · CSE: Network Traffic Exploration

Likely used the CSE challenge’s MACCDC 2012 network traffic dataset for mapping network hosts and producing a forensic timeline (inferred from the write-up).

> Pew Pew is a FastAPI analyzer that turns the legacy CCDC intrusion dataset into a forensic-ready narrative by auto-mapping hosts, aggressive attackers, targeted victims, and an attack timeline.

[Evidence](https://devpost.com/software/pew-pew-9mi8pb)

### 15. The Anachronist

**Luma AI** · LumaLabs: Reimagining Visual Creation with AI

Likely used the LumaLabs AI API for generating opening and closing videos for the game (inferred from the write-up).

> we integrated the LumaLabs AI API to generate realistic videos, which both open and close our game

[Evidence](https://devpost.com/software/the-anachronist)

## Corrected sourced notes

- **DronAR · Google Cardboard Development Prize.** The Unity script toggles Google Cardboard VR mode when the user presses the spacebar. The project scene also contains the Cardboard component. The note now cites the actual SDK call. [DronAR source at the checked commit](https://github.com/sebLopezCot/DronAR/blob/b55bcbfcd9056297e925e6a45dd4a92c8aee10ed/Assets/PennApps/scripts/DisableVR.cs#L14).
- **LeLamp Play Pack · Human Computer Lab Build with LeLamp SDK.** The tracker game calls the LeLamp runtime to change color and aim the lamp at virtual fruit. The pinned bridge configures the runtime and calls its light and motor APIs. [LeLamp runtime setup](https://github.com/tessaSlice/lelamp-play-pack/blob/3d1b11f31eb386acd6923b36b8585655305aac8b/tracker-game/game_bridge.py#L18), [light and motor calls](https://github.com/tessaSlice/lelamp-play-pack/blob/3d1b11f31eb386acd6923b36b8585655305aac8b/tracker-game/game_bridge.py#L40-L92).

## Verification

- Rebuilt the winners exports, Markdown directories and coverage report from the existing Devpost cache, then rebuilt the site catalog.
- `python3 scripts/verify.py --readme README.md` passed with byte-identical offline replay. A second run checked the inferences against the raw cached Devpost pages, linked READMEs and demo captions. It also checked the pinned code excerpts.
- `python3 site/build.py` passed. All 1,553 project cards matched their exported notes and headings. The card renderer emitted 24 distinct inferred headings, including one shared by the two VisionGuard prize rows.
- The verifier rejected fixtures with a missing or false flag, invalid wording, an empty or fabricated quote, an unrelated URL and a mismatched source suffix.
- Compared all 1,697 prize identities and the HTTP receipts with the baseline. The notes changed on 27 rows.

## Resource review fixes

Coverage before this follow-up is measured from `f767319`. Prize rows and project cards use different denominators because one project at one edition can win more than one prize.

| Prize-row coverage | Before | After |
| --- | ---: | ---: |
| Shown, including full notes and tech listings | 1,034 | 1,023 |
| Inferred | 25 | 25 |
| Award-only | 514 | 516 |
| Not stated | 124 | 123 |
| Linked resource only, counted separately | Included in shown | 10 |
| **Total prize rows** | **1,697** | **1,697** |

The 1,023 shown rows include 964 full notes and 59 tech listings. The 59 comprise 44 Built With tags, three write-up listings and 12 code imports. The first-screen disclosure counts 908 cards with sourced use, 24 with inferred notes, 64 with listed tech or links only and 557 that are award-only or unstated. Four cards have both sourced and inferred notes.

### Public code

The Nov. 22 research snapshot at 01:49 ET contained 47 high-confidence matches. Each matched the exact Devpost URL, project title, edition and year, and its public GitHub URL returned HTTP 200. All 47 were added with their match evidence and check time. Code coverage increased from **1,216 to 1,263 of 1,553 cards**, leaving 290 cards labeled “No public code found.” Poysson’s evidence now records that the repository owner handle is absent from the Devpost team roster.

### Sponsor notes

- Microsoft’s PrepBear and Repro list TypeScript. VL-ADK also lists TypeScript. CADVision lists C#. AccountableAI and Spitball list VS Code. Standard Response already used a TypeScript tag and now has the same “Listed on Devpost” heading. These notes record the language or editor named by the project.
- Sora2Detector lists ROCm. Aether and EcoBuddy use the verified TerpAI prize label and award-only framing. GitFlow now cites the write-up’s explicit use of the GitHub REST API. Ad BlockAR cites its Accomplishments section.
- The code audit found 12 pins that establish imports. They now use an “Imported in code” heading. The projects are RecovARy, Permanence, Crisis Maps, FreshDetect, Emergency Eye, Wordhawk, Forseen, ADapt, Motherly.ai, DIVE-DE.TECH, fly VS worm and Omni-Assist.
- Underflow says it calls `defang generate`. Smart Window says it creates a Twilio TwiML response. Ripple says it sets a list of Grok models. Lotus Journal refers to new user text. HandyDaddy now pins the ElevenLabs text-to-speech call, and Snitch pins the extraction of the GPTZero probability. Fish Persuasion follows the caption’s attribution to Gemini and Fish Audio.
- The award notes use sanitized prize labels. Tend keeps the Nessie flow without the payment amount. Seven project descriptions were edited to retain the supported feature while dropping the cost. Among the checked award labels were CodeInsight, Spielberg and Lemon.

### Presentation and verification

- The README and site hero lead with coverage. The README moves Browse above the banner. The site and Markdown label linked resources separately. The site’s light and dark themes, icon and README badges use the navy and blue palette.
- Rebuilt the exports, Markdown and static site. The required verifier and a second run with source caches passed. All 71 pinned code excerpts matched their recorded commits. Negative checks rejected unsupported code behavior, a mismatched code pin and money in display fields and site output, including currency escaped in catalog JSON.
- Checked the site in Chrome at 1,280 and 390 pixels, and checked cards for the code link, missing-code label, award-only note, inferred note, linked resource and listed tech. All 1,553 catalog code fields agree with the exported source URLs.
- The public site and GitHub raw export still need the release check after an authorized deployment.
