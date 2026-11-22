[Hackathon Tracks](../../README.md) / [Sponsors](../../SPONSORS.md) / NVIDIA

# NVIDIA

**16 winning projects** · 6 hackathons · 16 prizes · [Filter on the site](https://tracks.azizu.dev/#sponsor=NVIDIA)

**Jump to:** [What winners have in common](#what-winners-have-in-common) · [2026 winners](#2026-winners) · [2025 winners](#2025-winners) · [Track names and requirements](#track-names-and-requirements)

## What winners have in common

- **Most used tech:** python (12), arduino (5), typescript (5), fastapi (4), jetson-nano (4)
- **Project areas:** Safety and emergency response (2), Accessibility and assistive tools (1), Climate and environment (1)
- **Demo formats:** Hardware or robotics (8), Web app or dashboard (5), Mobile app (2)
- **Demo videos:** 16 of 16 winners link one

<sub>Counts use one entry per winning project. Areas and formats are matched from keywords in project descriptions and tech tags.</sub>

## 2026 winners

### [CalTrack](https://devpost.com/software/caltrack-i0pq3n)

[TreeHacks 2026](../by-hackathon/treehacks-2026.md#project-caltrack-i0pq3n) · **Edge AI Track**

Using mass surveillance to keep people safe - predicting impact, affected areas, and coordinating faster emergency response in disasters.

**How it used NVIDIA:** NVIDIA Earth-2 provides predictive weather patterns for the fire-risk overlay.

[Code](https://github.com/alangrewco/treehacks) · [Demo video](https://www.youtube.com/watch?v=51RLdw6FQOg) · Built with nvidia, docker, earth2studio, fastapi

### [Detour](https://devpost.com/software/detour-64kpds)

[TreeHacks 2026](../by-hackathon/treehacks-2026.md#project-detour-64kpds) · **Edge AI Track**

An onboard satellite agent evaluates possible debris collisions and proposes an avoidance maneuver.

**How it used NVIDIA:** The multi-agent workflow is powered by a local NVIDIA model via vLLM.

[Code](https://github.com/keanucz/detour) · [Demo video](https://www.youtube.com/watch?v=XTLts_t78IQ) · Built with dgx-spark, nvidia, agents, cdm

### [Farsight](https://devpost.com/software/farsight-t4qyli)

[Knight Hacks IX 2026](../by-hackathon/knight-hacks-ix-2026.md#project-farsight-t4qyli) · **Best Use of Jetson Nano**

Farsight is a rescue rover that streams its surroundings to an operator and turns measured room captures into a walkthrough for a VR headset.

**How it used NVIDIA:** The Jetson runs the rover server and YOLO11n-pose through TensorRT.

[Code](https://github.com/azizu06/farsight) · [Demo video](https://www.youtube.com/watch?v=AmrOGcTBTKU) · Built with nvidia-jetson, tensorrt, arduino, arkit

### [Fireline](https://devpost.com/software/fireline-764nir)

[Knight Hacks IX 2026](../by-hackathon/knight-hacks-ix-2026.md#project-fireline-764nir) · **Best Use of Jetson Nano**

An edge device identifies early signs of wildfire smoke and reports them to a dashboard.

**How it used NVIDIA:** The NVIDIA Jetson Orin Nano runs the smoke model on its GPU using TensorRT.

[Code](https://github.com/kateye31/fireline) · [Demo video](https://www.youtube.com/watch?v=vhKG4MiWa9A) · Built with jetson-nano, tensorrt, arduino, azure

### [KennyCraft](https://devpost.com/software/kennycraft)

[HackUTD 2026](../by-hackathon/hackutd-2026.md#project-kennycraft) · **Nvidia Track**

Custom voxel engine on a ARTY A7-100T FPGA with a realistic trading sim.

**How it used NVIDIA:** Nearby villagers use NVIDIA Nemotron Nano running locally and fall back to rules if it times out.

[Code](https://github.com/Sweet-Rice/kennycraft-alpha) · [Demo video](https://www.youtube.com/watch?v=Qakh5g6futU) · Built with arty-a7-100t-fpga, assembly, c, graphics

### [Permanence](https://devpost.com/software/permanence)

[Knight Hacks IX 2026](../by-hackathon/knight-hacks-ix-2026.md#project-permanence) · **Best Use of Jetson Nano**

A spatial awareness tool tracks objects and remembers their locations when they move out of view.

**How it used NVIDIA:** The Jetson drives the Arduino Uno and L298N motor driver and steers from the phone’s position.

[Code](https://github.com/billpquach/permanence) · [Demo video](https://www.youtube.com/watch?v=GexOIHp7s1w) · Built with cuda, jetson-nano, arduino, c++

### [Sprout](https://devpost.com/software/greenguardian-microfarm)

[TreeHacks 2026](../by-hackathon/treehacks-2026.md#project-greenguardian-microfarm) · **Edge AI Track**

A miniature robotic growing system monitors and tends a small farm.

**How it used NVIDIA:** The project processes visual data locally on the Jetson.

[Code](https://github.com/lethan3/cactushacks) · [Demo video](https://www.youtube.com/watch?v=PbnM8TVgxBQ) · Built with cuda, jetson-nano, arduino, claude

### [TORQ](https://devpost.com/software/torq)

[TreeHacks 2026](../by-hackathon/treehacks-2026.md#project-torq) · **Edge AI Track**

A Jetson-based retrofit tests autonomous driving functions in vehicles that were built without them.

**How it used NVIDIA:** The project’s high-level reasoning layer runs NVIDIA’s Alpamayo R1 vision-language-action model.

[Code](https://github.com/JoelGrayson/Treehacks2026) · [Demo video](https://www.youtube.com/watch?v=zEDVGfCVhaw) · Built with cuda, nvidia, c++, holoscan

### [TripWir3](https://devpost.com/software/test-l3i74h)

[HackUTD 2026](../by-hackathon/hackutd-2026.md#project-test-l3i74h) · **Nvidia Track**

Introducing TripWir3! Powered by NVIDIA Nemotron™ agents, this weight-provenance framework audits a given open-weight model's LoRA weights and trigger behaviors and returns an evidence-backed verdict.

**How it used NVIDIA:** The Nemotron 3.5 Super orchestrator on the NVIDIA API plans and calls tools.

[Code](https://github.com/mukherjeeabhirup/tripwir3) · [Demo video](https://www.youtube.com/watch?v=vPMd6Ijjr3M) · Built with nvidia-api, nvidia-brev, nvidia-nemotron, css

## 2025 winners

### [Alchemetrics](https://devpost.com/software/abc-xapnio)

[HackUTD 2025](../by-hackathon/hackutd-2025.md#project-abc-xapnio) · **Nvidia**

Alchemetrics is a real-time AI dashboard that tracks cauldrons, matches tickets, and forecasts overflows, bringing automation and clarity to Poyo’s Potion Factory’s magical chaos.

**How it used NVIDIA:** NVIDIA Nemotron orchestrates the multi-agent system.

[Code](https://github.com/Lanisha20/Alchemetrics) · [Demo video](https://www.youtube.com/watch?v=_XkRiy9jCP8) · Built with nemotron, css, fastapi, nextjs

### [DataDriver](https://devpost.com/software/datadriver)

[HackUTD 2025](../by-hackathon/hackutd-2025.md#project-datadriver) · **Nvidia**

DataPilot is an Agentic AI powered assistant that utilizes NVIDIA Nemotron to generate detailed step by step work plans, inspect real time inventory availability, and replan tasks when issues arise.

**How it used NVIDIA:** The project combines NVIDIA’s Nemotron Nano 9B v2 model with LangChain for its ReAct agent.

[Code](https://github.com/Jeanpascal-Gauthier/Data-Driver) · [Demo video](https://www.youtube.com/watch?v=w0YteTzoGc4) · Built with nemotron, agents, ai, flask

### [Portable Braille](https://devpost.com/software/portable-braille-cdq8v5)

[TreeHacks 2025](../by-hackathon/treehacks-2025.md#project-portable-braille-cdq8v5) · **Robo Prize**

A portable teaching device helps children with visual impairments practice Braille.

**How it used NVIDIA:** The project uses the Jetson Orin Nano for face expression recognition with RayBan Meta glasses.

[Code](https://github.com/Adil-Jussupov/PortableBraille) · [Demo video](https://www.youtube.com/watch?v=0vI_fjJIOsE) · Built with arduino, bluetooth, braille, c

### [Ranger](https://devpost.com/software/ranger-6jkv5s)

[TreeHacks 2025](../by-hackathon/treehacks-2025.md#project-ranger-6jkv5s) · **Best Accelerated Compute**

An AR wearable displays cues about nearby sounds to deaf and hard-of-hearing users.

**How it used NVIDIA:** The project uses Whisper Mini on the Jetson Nano for real-time voice transcription.

[Code](https://github.com/YuanSamuel/Treehacks2025) · [Demo video](https://www.youtube.com/watch?v=dUlzwdfdT2U) · Built with jetson-nano, adb, edge, linux

### [Toyotron](https://devpost.com/software/toyotron)

[HackUTD 2025](../by-hackathon/hackutd-2025.md#project-toyotron) · **Nvidia**

Toyotron is a solution that allows users to easily find their dream Toyota through agentic AI powered by NVIDIA's intelligent open source foundational model, Nemotron.

**How it used NVIDIA:** The project uses Nemotron as the reasoning core of its agents.

[Code](https://github.com/anbguye/hackutd-Toyota-Toyotron) · [Demo video](https://www.youtube.com/watch?v=CSc6zKQRxIY) · Built with nemotron, ai, css, next.js

### [VL-ADK](https://devpost.com/software/vl-adk)

[ShellHacks 2025](../by-hackathon/shellhacks-2025.md#project-vl-adk) · **NVIDIA**

A "psuedo" VLA model leveraging a fleet of autonomous ADK agents.

**How it used NVIDIA:** The team used SSH tunnels to connect its hosts to the Jetson Orin mounted on the Jetbot.

No public code linked · [Demo video](https://www.youtube.com/watch?v=0t4X0DoKbsc) · Built with jetson-orin, gemini, google-adk, python

### [WiiWork](https://devpost.com/software/wiiwork-8u1x62)

[TreeHacks 2025](../by-hackathon/treehacks-2025.md#project-wiiwork-8u1x62) · **Best Accelerated Compute**

WiiWork is a voice-controlled website designed for people and AI agents to use.

**How it used NVIDIA:** The project uses DeepSeek with NVIDIA for specialized reasoning.

[Code](https://github.com/Alezander9/WiiWork) · [Demo video](https://www.youtube.com/watch?v=rkLqYKocnNc) · Built with nvidia, anthropic, convex, deepseek

## Track names and requirements

<details>
<summary>Show track names, required tech and rule sources</summary>

| Hackathon | Track name | Required tech or brief | Source |
| --- | --- | --- | --- |
| [HackUTD 2026](../by-hackathon/hackutd-2026.md) | Nvidia Track | No specific requirement captured | [Event prize rules](https://hackutd-zeroday.devpost.com/) |
| [Knight Hacks IX 2026](../by-hackathon/knight-hacks-ix-2026.md) | NVIDIA: Best Use of Jetson Nano | NVIDIA Jetson Nano | [Track label](https://knight-hacks-ix.devpost.com/) |
| [TreeHacks 2026](../by-hackathon/treehacks-2026.md) | &#91;NVIDIA&#93; Edge AI Track | No specific requirement captured | [Event prize rules](https://treehacks-2026.devpost.com/) |
| [HackUTD 2025](../by-hackathon/hackutd-2025.md) | Nvidia | No specific requirement captured | [Event prize rules](https://hackutd-2025.devpost.com/) |
| [ShellHacks 2025](../by-hackathon/shellhacks-2025.md) | NVIDIA | Build a project that uses the power of AI, graphics, or accelerated computing to make life better, smarter, or more fun. | [Devpost prize description](https://shellhacks2025.devpost.com/) |
| [TreeHacks 2025](../by-hackathon/treehacks-2025.md) | NVIDIA: Best Accelerated Compute (5090s per team member - 1 GPU JHH signed &#91;1st&#93; &amp; 5080s per team member &#91;2nd&#93;) | Best use of NVIDIA AI or accelerated computing. | [Devpost prize description](https://treehacks-2025.devpost.com/) |
| [TreeHacks 2025](../by-hackathon/treehacks-2025.md) | NVIDIA: Robo Prize (Jetson Dev kit per team member) | Best use of NVIDIA tech in robotics, computer vision or edge AI. | [Devpost prize description](https://treehacks-2025.devpost.com/) |

</details>

[Back to top](#nvidia)
