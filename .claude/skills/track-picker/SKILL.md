---
name: track-picker
description: Compare current hackathon sponsor tracks with past winners and pick one feasible build that fits multiple tracks.
---
# Track picker

Copy the text below into Claude Code or Codex from this repository. Include your hackathon's official URL, candidate ideas, and what your team can build with the time and equipment you have.

## Prompt

Help my team pick one build for our hackathon. Use the event link and ideas I provide. Ask for the official link or the ideas if either is missing. Ask about a team constraint only if it can change the recommendation.

1. Read the current official event site, Devpost overview, rules, prize descriptions, and linked sponsor briefs. List every sponsor challenge and its advertised prize. For each, record the exact track name, mandatory integration, judging criteria, eligibility, submission proof, and source links. Capture deadlines, limits on entering multiple tracks, and any access or hardware requirements. Separate what the rules require from what the sponsor recommends. Mark unverified details and say which source you could not read.
2. Search `winners/winners.json` for those sponsors. Each sponsor also has a readable page linked from `SPONSORS.md`. Pull relevant examples with links and explain what role the sponsor technology played when the source shows it. Treat past winners as examples. Use the current rules to decide eligibility.
3. Make a matrix with one row per sponsor track and one column per idea. Score each cell 0 for a failed requirement or no fit, 1 for a possible fit with an unresolved dependency, or 2 for a verified fit with a concrete integration the team can demo. Give a short reason for each score. Check that the track combination is allowed and that the team can access the required services and devices.
4. Recommend one build with the most compatible score-2 tracks that fit one working demo. Aim for two to four. Break ties by favoring a smaller build, a clearer demo, and fewer access risks. If no idea has a score of 2, identify the quickest test that could confirm a fit. Set aside ideas with no plausible track.
5. End with the demo in one sentence, the minimum features to build, the first integration to test, and what to cut if time runs short. List what to confirm with organizers before committing. Cite sources for rules, prizes, and project claims. Only research and advise. Leave registration and submission to the team.
