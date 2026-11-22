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

## FRAMING

Counts cover 1,697 individual prize rows across 990 edition-specific tracks. The baseline is the completed resource-fix pass at `b7f33d3`.

| Prize coverage | Rows |
| --- | ---: |
| Tech prizes with sponsor use | **968** (943 shown, 25 inferred) |
| Theme prizes with no sponsor tech named | **541** |
| Tech prizes where use was not found | **188** |
| **Total** | **1,697** |

448 award-only rows and 10 not-stated rows moved to theme. The resource fixes had reduced the original 124 not-stated rows to 123 before this pass. The same track rule moved 66 full notes, 14 tech listings and 3 linked resources to theme. The 188 tech gaps include 68 award-only rows, 113 not-stated rows and 7 linked resources. The source-use ledger preserves those earlier quotes. The prize-kind ledger records each exact gallery label, the decision, its rationale and the public rules URL. 1,263 of 1,553 project cards have public code links. [Prize-kind ledger](scripts/prize-kinds.tsv), [Source-use ledger](scripts/sponsor-uses.tsv).

A subscription, device or API credit offered as a reward did not make the track a tech-use prize. A named sponsor technology offered for the build, a specific challenge input, or an unresolved technical brief kept the track in tech. Awards such as Peraton’s web hack and Ergo’s productivity challenge name third-party frameworks and have no identified technology from the awarding sponsor. The 25 previous labeled inferences passed the source check.

### Previously unclear rows

All 32 were rechecked. 14 now qualify as theme prizes, including the Cal Hacks clinical-trial awards and the generic MoPub mobile data award. The other 18 remain tech gaps. No additional row tied a concrete feature to a supported sponsor product or dataset. The PrizePicks entries describe Sportradar or their own video analysis. The Kensho entries describe candidate speeches and tweets. The two Toyota entries analyze vehicle data about Toyota and its competitors. Their write-ups leave the dataset source unresolved.

### Ten randomly sampled theme prizes

Sampled 10 prize rows without replacement in export order with seed `1697`. Prize text below uses the published display quote.

| Project and edition | Prize text | Classification basis |
| --- | --- | --- |
| Empirica · Cal Hacks 12.0 2025 | Regeneron: Honorable Mention | The rubric judges clinical-trial usefulness, design, relevance, availability and readiness. The starter kit lists multiple external data sources. [Public rules](https://regn.link/Calhacks). |
| Charitable · HackDuke Code for Good 2020 | Wolfram Award | Software access or subscription prize. [Public rules](https://code-for-good.devpost.com/). |
| ClariTA · ShellHacks 2025 | Assurant | Insurance and responsible AI challenge. [Public rules](https://shellhacks2025.devpost.com/). |
| Voiceboard · ShellHacks 2024 | Google | Social good category open to any medium. [Public rules](https://shellhacks2024.devpost.com/). |
| GaitGuard · Bitcamp 2026 | Most Philanthropic Hack - Bloomberg | Public health, social impact or sustainability category. [Public rules](https://bitcamp-2026.devpost.com/). |
| Blockify · Cal Hacks 11.0 2024 | Cal Hacks / Berkeley RDI: Berkeley RDI Web3 Prize | Web3 category. [Public rules](https://cal-hacks-11-0.devpost.com/). |
| GEarth · Knight Hacks IX 2026 | BNY: Financial Services Challenge | Financial services category. [Public rules](https://knight-hacks-ix.devpost.com/). |
| TraceFund · Cal Hacks 12.0 2025 | Ethereum Foundation: Honorable Mention | Honorable mention with a gift card in the prize listing. [Public rules](https://cal-hacks-12-0.devpost.com/). |
| Troomba · HackMIT 2018 | element14 Presents a Robotics Kit | The TI robotics kit is awarded to the winner. [Public rules](https://hackmit-2018.devpost.com/). |
| Vigilante · TreeHacks 2025 | Otsuka Valuenex: VALUENEX Big Data Visualization Award | The rules ask for visualization of complex data such as images, audio or text. [Public rules](https://treehacks-2025.devpost.com/). |

### Theme-like tracks retained as tech gaps

The gaps below have a category-style title or a brief that leaves the technology relationship ambiguous. The row count covers projects in each track with no shown or inferred use. Tracks that explicitly name a sponsor tool in their title remain tech as recorded in the ledger.

| Edition | Prize | Gap rows | Basis |
| --- | --- | ---: | --- |
| HackUTD 2026 | 8090 Track | 3 | The available public listing only gives rewards. The modernization challenge may have included an 8090 product or starter resource. [Public rules](https://zeroday.hackutd.co/). |
| Cal Hacks 12.0 2025 | AppLovin: Ad Intelligence Challenge | 1 | AppLovin’s challenge criteria specify supplied ad creatives for feature extraction. [Public rules](https://docs.google.com/document/d/1i2wu_Z6Hb-WDyzM1woYFpqtfyp1Y-0Gc135XvK5fC8g/edit). |
| nwHacks 2025 | Aquareum.tv Sponsor Prize | 5 | Eligibility calls for an integration with Streamplace, Livepeer or video on the AT protocol. [Public rules](https://nwhacks-2025.devpost.com/). |
| HackHarvard 2026 | ASUS Sustainability: Save the Earth | 2 | The rules offer ASUS hardware to support development and encourage teams to use it. [Public rules](https://hackharvard2026.devpost.com/). |
| LA Hacks 2026 | ASUS Company Challenge | 1 | The rules offer participants access to ASUS Ascent GX10 hardware for their build. [Public rules](https://la-hacks-2026.devpost.com/). |
| HackMIT 2018 | Cadillac: Time = Luxury | 1 | Eligibility calls for an app for the Cadillac in-vehicle infotainment platform. [Public rules](https://hackmit-2018.devpost.com/). |
| Bitcamp 2026 | Best Financial Hack - Capital One | 1 | The financial hack rules offer the optional Capital One Nessie API. [Public rules](https://bitcamp-2026.devpost.com/). |
| Bitcamp 2025 | Best Financial Hack - Capital One | 1 | The financial hack rules offer the optional Capital One Nessie API. [Public rules](https://bitcamp2025.devpost.com/). |
| HackGT 12 2025 | Capital One - Best Financial Hack | 1 | The financial hack rules suggest the Capital One Nessie API. [Public rules](https://hackgt-12.devpost.com/). |
| HackNYU 2025 | Track: Fintech - Best Financial Hack | 2 | The financial hack rules offer the optional Capital One Nessie API. [Public rules](https://hacknyu-2025.devpost.com/). |
| MHacks 2024 | CAT Digital - Best Use of API | 1 | The exact prize label calls out technology or a technical input. [Public rules](https://mhacks-2024.devpost.com/). |
| HackUTD 2026 | CBRE Track | 3 | The challenge refers to a real estate data scenario. The public detail available here does not establish which resources were required. [Public rules](https://zeroday.hackutd.co/). |
| Bitcamp 2024 | Best use of AI/ML Innovation for the Francis Scott Key Bridge Recovery Efforts - Cloudforce | 3 | The rules link to Microsoft Education Hub for implementation and compute resources. [Public rules](https://bitcamp2024.devpost.com/). |
| Bitcamp 2026 | TerpAI Ultimate Agent Showdown - Cloudforce/Microsoft | 2 | The rules call for building a TerpAI agent in the event platform. [Public rules](https://bitcamp-2026.devpost.com/). |
| Bitcamp 2025 | Best Use of GenAI in Business - Cloudforce/Microsoft | 1 | The rules call for using TerpAI to generate a business pitch. [Public rules](https://bitcamp2025.devpost.com/). |
| TreeHacks 2025 | Codegen: Best Code Analysis Application | 1 | The rules encourage the Codegen SDK. [Public rules](https://treehacks-2025.devpost.com/). |
| TreeHacks 2025 | Codegen: Best Developer Tool | 1 | The rules encourage the Codegen SDK. [Public rules](https://treehacks-2025.devpost.com/). |
| Hack the North 2024 | CSE: Working in an Air-Gapped Environment | 1 | The cached rules describe this as a CSE API challenge while leaving the API unspecified. [Public rules](https://hackthenorth2024.devpost.com/). |
| TreeHacks 2025 | Context: Best AI Employee Workflow | 1 | The rules suggest the Context API or context engine. [Public rules](https://treehacks-2025.devpost.com/). |
| HackMIT 2018 | Most Novel Data Mobility Hack by Dell | 1 | The rules give a judging advantage to entries built for Dell products. [Public rules](https://hackmit-2018.devpost.com/). |
| Hack the North 2026 | Dominion Dynamics: WHITEOUT | 2 | The rules call for building for Dominion’s WHITEOUT simulation. [Public rules](https://hackthenorth2026.devpost.com/). |
| Hack the North 2026 | Dryft: Dryft Company Challenge | 1 | The rules supply an autoregressive transformer for an inference optimization competition. [Public rules](https://hackthenorth2026.devpost.com/). |
| ShellHacks 2024 | ETH Miami | 2 | The rules specify SpeedRunEthereum and Scaffold-ETH. [Public rules](https://shellhacks2024.devpost.com/). |
| Hack the North 2024 | ETHGlobal: Ethereum's Infinite Garden | 1 | The rules require deployment to an Ethereum or Ethereum L2 testnet. [Public rules](https://hackthenorth2024.devpost.com/). |
| Hack the North 2025 | ETHGlobal: Ethereum's Infinite Garden | 2 | The rules require deployment to an Ethereum or Ethereum L2 testnet. [Public rules](https://hackthenorth2025.devpost.com/). |
| HackMIT 2016 | Best Creative Car Hack (Ford) | 1 | The rules name Ford OpenXC as the vehicle API and hardware. [Public rules](https://hackmit-2016.devpost.com/). |
| MHacks 2025 | Vision Alignment Tool presented by Ford | 1 | The exact industrial vision tooling requirements are unclear from the archived prize listing. [Public rules](https://mhacks-2025.devpost.com/). |
| TreeHacks 2026 | &#91;Google&#93; Cloud AI Track | 1 | Conservative tech classification. The cached prize listing leaves the scope of sponsor technology unclear. [Public rules](https://treehacks-2026.devpost.com/). |
| HackMIT 2018 | Best Disaster Preparedness &amp; Relief Solutions for IBM Call for Code Challenge | 1 | Eligibility requires an IBM Cloud or Bluemix API service. [Public rules](https://hackmit-2018.devpost.com/). |
| Hack the North 2024 | Intuit: Win a VR Headset! | 1 | The rules require the Intuit QuickBooks API. [Public rules](https://hackthenorth2024.devpost.com/). |
| HackMIT 2016 | Most interesting use of Wikipedia data around the US presidential candidates, campaigns and/or upcoming election (Kensho) | 2 | The prize names Wikipedia election data. No Kensho-specific data source is identified in the project evidence. [Public rules](https://hackmit-2016.devpost.com/). |
| TreeHacks 2025 | Edge AI Prize: Operator Optimization Champion | 1 | The rules specify a Galaxy S24 profiling setup and the challenge’s operator-optimization benchmark. [Public rules](https://treehacks-2025.devpost.com/). |
| Cal Hacks 12.0 2025 | LiveKit: Most Creative Project | 1 | The rules name LiveKit as one of the accepted paths for a voice or video project. [Public rules](https://cal-hacks-12-0.devpost.com/). |
| MHacks 2024 | Magic Loops - Best use of Generative UI | 1 | The title refers to generative UI and the cached rules give rewards only. Whether the Magic Loops platform is in scope is unclear. [Public rules](https://mhacks-2024.devpost.com/). |
| HackMIT 2013 | Facebook | 1 | The title names Facebook, which is also a platform. The cached prize listing only gives rewards. [Public rules](https://hackmit.devpost.com/). |
| HackMIT 2016 | Oculus Prize (Facebook) | 1 | Conservative tech classification. The cached prize listing leaves the scope of sponsor technology unclear. [Public rules](https://hackmit-2016.devpost.com/). |
| LA Hacks 2025 | MSI Lucky's Hackening | 1 | The rules require MSI hardware and name the MSI Raider laptop and a Pro MP monitor. [Public rules](https://la-hacks-2025.devpost.com/). |
| HackGT 13 2026 | NSA: Hearsay: The Audio Authentication Challenge - 1st Place | 1 | The NSA Hearsay competition uses a sponsor-provided audio evaluation challenge. [Public rules](https://hackgt13.devpost.com/). |
| TreeHacks 2025 | Otsuka Valuenex: ekkomi® Advanced Technologies for User Feedback Award | 1 | The track names Otsuka’s ekkomi app and its experience is the target of the feedback challenge. [Public rules](https://treehacks-2025.devpost.com/). |
| Knight Hacks VIII 2025 | Pheratech Systems: ROS2 Autonomy Challenge | 1 | The prize specifies the ROS 2 autonomy platform. The available rules do not resolve whether a sponsor kit was part of the task. [Public rules](https://knighthacksviii.devpost.com/). |
| HackMIT 2016 | Focus based document summarization (Philips) | 1 | The published challenge supplies a specific Timeline17 archive for document summarization. [Public rules](https://hackmit-2016.devpost.com/). |
| HackMIT 2016 | Best On-Demand Hack (Postmates) | 1 | The rules identify the Postmates Delivery API for implementing the on-demand feature. [Public rules](https://hackmit-2016.devpost.com/). |
| HackGT 12 2025 | PrizePicks - Signal from the Noise | 1 | The rules offer anonymized PrizePicks-style projection and event stream data. [Public rules](https://hackgt-12.devpost.com/). |
| HackGT 12 2025 | PrizePicks - The Second Screen Experience | 1 | The rules offer a PrizePicks React Native starter kit and a simulated update stream. [Public rules](https://hackgt-12.devpost.com/). |
| HackHarvard 2026 | Regeneron Healthcare: Reinvent Clinical Trials &amp; Drug Development | 10 | The rules link sponsor starter sheets and data sources. The available summaries do not settle whether the project used a supplied resource. [Public rules](https://regn.link/hackharvard). |
| Knight Hacks VIII 2025 | ServiceNow: Knowledge Gap Request Agent Challenge | 3 | The listed ServiceNow challenge concerns knowledge-gap automation. The archived prize listing does not establish whether the platform was optional. [Public rules](https://knighthacksviii.devpost.com/). |
| HackUTD 2026 | &#91;MLH&#93; Build Your Hackathon A-Team with SpaceXSI | 1 | Raffle eligibility requires Cursor and a Grok Bot automation. [Public rules](https://hackutd-zeroday.devpost.com/). |
| HackMIT 2018 | Best Use of Deep Neural Networks | 1 | The rules require a pre-trained model and Spell’s cloud GPU. [Public rules](https://hackmit-2018.devpost.com/). |
| HackMIT 2013 | Square Inc. - Making Commerce Easy and Rounding the Corners | 1 | The Square prize title names the sponsor but the archived listing only gives the reward. [Public rules](https://hackmit.devpost.com/). |
| HackUTD 2025 | T-Mobile | 2 | The challenge specifies a T-Mobile Customer Happiness Index using customer feedback and network data. The source of that data is unclear. [Public rules](https://legend.hackutd.co/). |
| HackUTD 2026 | T-Mobile Track | 3 | The challenge describes a synthetic customer-protection dataset. [Public rules](https://zeroday.hackutd.co/). |
| UC Berkeley AI Hackathon 2026 | Best Compression Model for The Token Company | 1 | The title asks for a compression model for The Token Company. The cached rubric does not identify which implementation input was expected. [Public rules](https://ai-hackathon-2026.devpost.com/). |
| HackUTD 2024 | Toyota | 2 | The organizer’s Toyota challenge specifies vehicle fuel-economy data for 2021–2025. [Public rules](https://ripple.hackutd.co/). |
| Cal Hacks 13.0 2026 | &#91;Visa&#93; Best use of Reimagining Shopping sponsored by Visa | 1 | The listed Visa track asks for a use case in reimagining shopping. The cached rules do not resolve which payment tools were in scope. [Public rules](https://cal-hacks-13-0.devpost.com/). |
| TreeHacks 2026 | &#91;Visa&#93; The Generative Edge: Future of Commerce | 1 | The Visa commerce track is described by its title and a reward. The archived listing does not establish what technology was in scope. [Public rules](https://treehacks-2026.devpost.com/). |
| Cal Hacks 11.0 2024 | Warp: Best Developer Tool by Warp | 1 | The rules encourage trying Warp while hacking, while allowing other tools. [Public rules](https://cal-hacks-11-0.devpost.com/). |
| Hack@Brown 2024 | Best Developer Tool sponsored by Warp | 1 | The rules invite participants to try Warp, while allowing other tools. [Public rules](https://hack-brown-2024.devpost.com/). |
| Hack the North 2024 | Warp: Best Developer Tool by Warp | 1 | The archived rules mention Warp as an optional terminal and explicitly allow other tools. [Public rules](https://hackthenorth2024.devpost.com/). |
| Hack the North 2025 | Warp: Best Developer Tool by Warp | 1 | The rules invite teams to try Warp during the build, while allowing other tools. [Public rules](https://hackthenorth2025.devpost.com/). |
| Hack the North 2026 | Warp: Best Developer Tool by Warp | 1 | The rules invite teams to try Warp and the Oz API, while allowing other tools. [Public rules](https://hackthenorth2026.devpost.com/). |
| MHacks 2024 | Warp - Best Developer Tool | 1 | The rules encourage trying Warp while hacking, while allowing other tools. [Public rules](https://mhacks-2024.devpost.com/). |
| TreeHacks 2025 | Warp: Best Developer Tool (Keychron Mechanical Keyboard per team member) | 1 | The rules invite teams to try Warp during the build, while allowing other tools. [Public rules](https://treehacks-2025.devpost.com/). |
| Hack the North 2024 | Web Summit: Web Summit challenge | 2 | The rules specify the Web Summit companion app as a baseline. [Public rules](https://hackthenorth2024.devpost.com/). |
| nwHacks 2025 | Wondershare Sponsor Prize | 1 | The rules require using Wondershare Filmora to make the submission video. [Public rules](https://nwhacks-2025.devpost.com/). |
| Bitcamp 2024 | University Course Catalog Data Extraction and Query Challenge - Xficient | 3 | The challenge specifies course-catalogue data for the extraction task, although teams may choose their stack. [Public rules](https://bitcamp2024.devpost.com/). |

### Verification

- Rebuilt the exports, Markdown directory, coverage report and static site. The required offline verifier and the source-cache run passed.
- Checked that every prize appears in exactly one of the three buckets, every theme row has a matching ledger record and award quote, and the README, site and coverage report publish identical totals. Also checked the exact theme heading in the catalog, with failing fixtures for a stale count, missing basis, incorrect heading and old gap wording.
- Compared prize identities, public code links and all previously inferred notes with the resource-fix baseline. Confirmed the disclosure and sampled theme, tech-gap and inference headings in Chrome at 1,280 and 390 pixels.
