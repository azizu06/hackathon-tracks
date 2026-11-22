"use strict";

const byId = (id) => document.getElementById(id);
const collator = new Intl.Collator("en", { sensitivity: "base", numeric: true });
const normalize = (text) => String(text ?? "").trim().toLowerCase();
const format = (number) => number.toLocaleString("en");
const plural = (count, word, many = word + "s") => `${format(count)} ${count === 1 ? word : many}`;
const slugify = (text) => normalize(text).replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
const repo = "https://github.com/azizu06/hackathon-tracks/blob/main/";
const batchSize = 24;

function element(tag, text, className) {
  const node = document.createElement(tag);
  if (text) node.textContent = text;
  if (className) node.className = className;
  return node;
}

function icon(name) {
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("class", "icon");
  svg.setAttribute("aria-hidden", "true");
  const use = document.createElementNS("http://www.w3.org/2000/svg", "use");
  use.setAttribute("href", "#i-" + name);
  svg.append(use);
  return svg;
}

function link(text, href, className) {
  const anchor = element("a", text, className);
  anchor.href = href;
  return anchor;
}

function tally(list, labels) {
  const counts = new Map();
  for (const item of list) {
    const unique = new Map(labels(item).filter(Boolean).map((label) => [normalize(label), label]));
    for (const [key, label] of unique) {
      if (!counts.has(key)) counts.set(key, { label, count: 0 });
      counts.get(key).count++;
    }
  }
  return [...counts.values()].sort((a, b) => b.count - a.count || collator.compare(a.label, b.label));
}

const projects = (window.TRACKS_CATALOG ?? []).map((project) => ({
  ...project,
  edition: [project.event, project.year].filter(Boolean).join(" "),
  sponsorAwards: project.awards.filter((award) => award.sponsor),
  isChampion: project.sponsors.length >= 2 || project.awards.filter((award) => award.sponsor).length >= 2,
  keywords: normalize([
    project.name, project.summary, project.event, project.year, ...project.sponsors,
    ...project.tech, ...project.awards.map((award) => award.title),
  ].join(" ")),
}));
const sponsors = tally(projects, (project) => project.sponsors);
const editions = new Set(projects.map((project) => project.editionId || project.edition).filter(Boolean));
const options = {
  sponsor: { label: "All sponsors", values: sponsors },
  event: { label: "All hackathons", values: tally(projects, (project) => [project.event]) },
  year: { label: "All years", values: tally(projects, (project) => [project.year]) },
  tech: { label: "All tech", values: tally(projects, (project) => project.tech) },
};
const filters = Object.fromEntries(Object.keys(options).map((key) => [key, byId("filter-" + key)]));
const listViews = new Set(["browse", "champions"]);
const mainViews = new Set(["browse", "sponsors", "hackathons", "champions", "picker"]);
const search = byId("search");
const sort = byId("sort");
const context = byId("context");
const results = byId("results");
const heading = byId("view-title");
const more = byId("more");
const selectedSponsors = new Set();
const theme = byId("theme");
let currentView = { name: "browse", params: new URLSearchParams() };
let limit = batchSize;
let displayed = [];
let pickerSummary;

function sponsorHref(sponsor) {
  return "#sponsor=" + encodeURIComponent(sponsor);
}

function browseHref(params) {
  const query = new URLSearchParams(Object.entries(params).filter(([, value]) => value)).toString();
  return "#browse" + (query ? "?" + query : "");
}

function getView(hash = location.hash) {
  const route = hash.slice(1);
  if (route.startsWith("sponsor=")) {
    try {
      const key = normalize(decodeURIComponent(route.slice("sponsor=".length)));
      const sponsor = sponsors.find((entry) => normalize(entry.label) === key);
      if (sponsor) return { name: "sponsor", sponsor: sponsor.label, params: new URLSearchParams() };
    } catch {
      // A malformed sponsor link returns to the directory.
    }
    return { name: "sponsors", params: new URLSearchParams() };
  }
  const [name, query = ""] = route.split("?");
  return { name: mainViews.has(name) ? name : "browse", params: new URLSearchParams(query) };
}

function stat(label, count) {
  const item = element("li");
  item.append(element("strong", format(count)), element("span", label));
  return item;
}

function matchingSponsor(project, sponsor) {
  return project.sponsors.some((name) => normalize(name) === normalize(sponsor));
}

function rankedList(title, entries, hrefForLabel, level = "h3") {
  if (!entries.length) return null;
  const panel = element("section", "", "ranked-panel");
  panel.append(element(level, title));
  const list = element("ol", "", "ranked");
  for (const { label, count } of entries.slice(0, 5)) {
    const row = element("li");
    row.append(hrefForLabel ? link(label, hrefForLabel(label)) : element("span", label));
    row.append(element("span", format(count), "rank-count"));
    list.append(row);
  }
  panel.append(list);
  return panel;
}

function setLinks(entries) {
  const node = byId("view-links");
  node.replaceChildren();
  for (const [label, href] of entries) {
    const anchor = link(label, href);
    anchor.append(icon("out"));
    node.append(anchor);
  }
  node.hidden = !entries.length;
}

function showSponsor(sponsor) {
  const entries = projects.filter((project) => matchingSponsor(project, sponsor));
  const hackathons = new Set(entries.map((project) => project.edition)).size;
  byId("view-intro").textContent = `${plural(entries.length, "winning project")} at ${plural(hackathons, "hackathon")}.`;
  byId("view-intro").hidden = false;
  setLinks([["Track rules on GitHub", `${repo}winners/by-sponsor/${slugify(sponsor)}.md`]]);
  const panel = element("section", "", "insights");
  panel.append(element("h2", "What winners have in common"));
  const group = element("div", "", "insight-grid");
  const lists = [
    rankedList("Most used tech", tally(entries, (project) => project.tech),
      (label) => browseHref({ sponsor: normalize(sponsor), tech: normalize(label) })),
    rankedList("Hackathons", tally(entries, (project) => [project.edition]), (label) => {
      const match = entries.find((project) => project.edition === label);
      return browseHref({ sponsor: normalize(sponsor), event: normalize(match.event), year: match.year });
    }),
    rankedList("Also won prizes from", tally(entries, (project) =>
      project.sponsors.filter((name) => normalize(name) !== normalize(sponsor))), sponsorHref),
  ].filter(Boolean);
  group.append(...lists);
  panel.append(group);
  context.append(panel);
}

function directoryFilter(placeholder, labelText, onInput) {
  const wrap = element("label", "", "search search-small");
  wrap.append(icon("search"), element("span", labelText, "sr-only"));
  const input = element("input");
  input.type = "search";
  input.placeholder = placeholder;
  input.autocomplete = "off";
  input.addEventListener("input", () => onInput(normalize(input.value)));
  wrap.append(input);
  return wrap;
}

function showSponsorDirectory() {
  const toolbar = element("div", "", "directory-toolbar");
  const order = element("label", "", "sort");
  order.append(element("span", "Sort"));
  const select = element("select");
  select.append(new Option("Name A to Z", "name"), new Option("Most winners", "count"));
  order.append(select);
  const letters = element("nav", "", "letters");
  letters.setAttribute("aria-label", "Jump to a letter");
  const track = element("div", "", "letters-track");
  letters.append(track);
  const listing = element("div", "", "directory");
  const empty = element("p", "No sponsors match that search.", "empty");
  empty.hidden = true;
  let query = "";

  function letterOf(label) {
    const first = label.trim()[0]?.toUpperCase() ?? "#";
    return first >= "A" && first <= "Z" ? first : "#";
  }

  function draw() {
    listing.replaceChildren();
    track.replaceChildren();
    const matches = sponsors.filter(({ label }) => normalize(label).includes(query));
    empty.hidden = matches.length > 0;
    const byCount = select.value === "count";
    const groups = new Map();
    const ordered = byCount ? matches : [...matches].sort((a, b) => collator.compare(a.label, b.label));
    for (const entry of ordered) {
      const key = byCount ? "all" : letterOf(entry.label);
      if (!groups.has(key)) groups.set(key, []);
      groups.get(key).push(entry);
    }
    letters.hidden = byCount || !matches.length;
    for (const [key, entries] of groups) {
      const section = element("section", "", "directory-group");
      if (!byCount) {
        section.id = "letter-" + (key === "#" ? "num" : key);
        const title = element("h2", key === "#" ? "0–9" : key);
        title.append(element("small", plural(entries.length, "sponsor")));
        section.append(title);
        const jump = link(key === "#" ? "0–9" : key, "#" + section.id);
        jump.addEventListener("click", (event) => {
          event.preventDefault();
          section.scrollIntoView({ block: "start" });
          section.querySelector("a")?.focus({ preventScroll: true });
        });
        track.append(jump);
      }
      const list = element("ul", "", "directory-list");
      for (const { label, count } of entries) {
        const item = element("li");
        const anchor = link("", sponsorHref(label));
        anchor.append(element("span", label, "directory-name"), element("span", plural(count, "winner"), "pill"));
        item.append(anchor);
        list.append(item);
      }
      section.append(list);
      listing.append(section);
    }
  }

  select.addEventListener("change", draw);
  toolbar.append(directoryFilter("Find a sponsor", "Find a sponsor", (value) => { query = value; draw(); }), order);
  context.append(toolbar, letters, listing, empty);
  draw();
}

function showHackathonDirectory() {
  const rows = new Map();
  for (const project of projects) {
    if (!project.event) continue;
    const key = project.editionId || project.edition;
    if (!rows.has(key)) rows.set(key, { event: project.event, year: project.year, winners: 0, sponsors: new Set() });
    const row = rows.get(key);
    row.winners++;
    for (const sponsor of project.sponsors) row.sponsors.add(normalize(sponsor));
  }
  const years = new Map();
  for (const row of [...rows.values()].sort((a, b) => Number(b.year) - Number(a.year) || collator.compare(a.event, b.event))) {
    if (!years.has(row.year)) years.set(row.year, []);
    years.get(row.year).push(row);
  }
  const groups = [];
  const listing = element("div", "", "directory");
  for (const [year, entries] of years) {
    const section = element("section", "", "directory-group");
    const title = element("h2", year);
    title.append(element("small", plural(entries.length, "hackathon")));
    section.append(title);
    const list = element("ul", "", "directory-list");
    const items = [];
    for (const row of entries) {
      const item = element("li");
      item.dataset.search = normalize(row.event + " " + row.year);
      const anchor = link("", browseHref({ event: normalize(row.event), year: row.year }));
      const label = element("span", "", "directory-label");
      label.append(element("span", row.event, "directory-name"), element("span", plural(row.sponsors.size, "sponsor") + " awarded prizes", "directory-meta"));
      anchor.append(label, element("span", plural(row.winners, "winner"), "pill"));
      item.append(anchor);
      list.append(item);
      items.push(item);
    }
    section.append(list);
    listing.append(section);
    groups.push({ section, items });
  }
  const empty = element("p", "No hackathons match that search.", "empty");
  empty.hidden = true;
  const filter = directoryFilter("Find a hackathon", "Find a hackathon", (query) => {
    let visible = 0;
    for (const { section, items } of groups) {
      let shown = 0;
      for (const item of items) {
        item.hidden = !item.dataset.search.includes(query);
        if (!item.hidden) shown++;
      }
      section.hidden = shown === 0;
      visible += shown;
    }
    empty.hidden = visible > 0;
  });
  const toolbar = element("div", "", "directory-toolbar");
  toolbar.append(filter);
  context.append(toolbar, listing, empty);
}

function showPicker() {
  const panel = element("fieldset", "", "picker");
  panel.append(element("legend", "Sponsors at your event"));
  const find = directoryFilter("Find a sponsor", "Find a sponsor to pick", (query) => {
    let visible = 0;
    for (const chip of choices.children) {
      chip.hidden = !normalize(chip.textContent).includes(query);
      if (!chip.hidden) visible++;
    }
    empty.hidden = visible > 0;
  });
  const choices = element("div", "", "picker-choices");
  const empty = element("p", "No sponsors match that search.", "empty");
  empty.hidden = true;
  for (const { label } of [...sponsors].sort((a, b) => collator.compare(a.label, b.label))) {
    const chip = element("label");
    const checkbox = element("input");
    checkbox.type = "checkbox";
    checkbox.checked = selectedSponsors.has(normalize(label));
    checkbox.addEventListener("change", () => {
      if (checkbox.checked) selectedSponsors.add(normalize(label));
      else selectedSponsors.delete(normalize(label));
      limit = batchSize;
      refreshResults();
    });
    chip.append(checkbox, element("span", label));
    choices.append(chip);
  }
  pickerSummary = element("div", "", "picker-summary");
  panel.append(find, choices, empty);
  context.append(panel, pickerSummary);
}

function resetFilters() {
  search.value = "";
  for (const filter of Object.values(filters)) filter.value = "";
  limit = batchSize;
}

function applyParams(params) {
  search.value = params.get("q") ?? "";
  for (const [key, filter] of Object.entries(filters)) {
    const value = normalize(params.get(key));
    filter.value = [...filter.options].some((option) => option.value === value) ? value : "";
  }
  if ([...sort.options].some((option) => option.value === params.get("sort"))) sort.value = params.get("sort");
}

function syncHash() {
  if (!listViews.has(currentView.name)) return;
  const params = { q: search.value.trim() };
  for (const [key, filter] of Object.entries(filters)) params[key] = filter.value;
  if (sort.value !== defaultSort(currentView.name)) params.sort = sort.value;
  const query = new URLSearchParams(Object.entries(params).filter(([, value]) => value)).toString();
  const hash = "#" + currentView.name + (query ? "?" + query : "");
  if (hash !== location.hash && !(hash === "#browse" && !location.hash)) history.replaceState(null, "", hash);
}

function defaultSort(name) {
  return { champions: "awards", picker: "match" }[name] ?? "recent";
}

function applyView(view, focus = false) {
  currentView = view;
  resetFilters();
  sort.options[0].hidden = view.name !== "picker";
  sort.value = defaultSort(view.name);
  const titles = {
    browse: "Winning projects",
    sponsors: "Sponsors",
    hackathons: "Hackathons",
    sponsor: view.sponsor,
    champions: "Multi-track winners",
    picker: "Track picker",
  };
  const intros = {
    sponsors: "Pick a sponsor to see its winners and how they used its tech where Devpost describes it.",
    hackathons: "Pick a hackathon to see every project that won a sponsor prize there.",
    champions: "Projects that won prizes from two or more sponsors at the same hackathon.",
    picker: "Tick the sponsors at your event. Past winners of those prizes appear below, best match first.",
  };

  document.querySelector(".hero").hidden = view.name !== "browse";
  heading.textContent = titles[view.name];
  document.title = view.name === "browse" ? "Hackathon Tracks" : `${titles[view.name]} · Hackathon Tracks`;
  const intro = byId("view-intro");
  intro.textContent = intros[view.name] ?? "";
  intro.hidden = !intro.textContent;
  byId("view-crumb").hidden = view.name !== "sponsor";
  setLinks([]);
  for (const navLink of document.querySelectorAll("[data-view]")) {
    const navView = view.name === "sponsor" ? "sponsors" : view.name;
    if (navLink.dataset.view === navView) {
      navLink.setAttribute("aria-current", "page");
      navLink.scrollIntoView({ block: "nearest", inline: "nearest" });
    } else navLink.removeAttribute("aria-current");
  }
  context.replaceChildren();
  context.hidden = listViews.has(view.name);
  byId("catalog-controls").hidden = !listViews.has(view.name) && view.name !== "sponsor";
  byId("field-sponsor").hidden = view.name === "sponsor";

  if (view.name === "sponsors") showSponsorDirectory();
  if (view.name === "hackathons") showHackathonDirectory();
  if (view.name === "sponsor") showSponsor(view.sponsor);
  if (view.name === "picker") showPicker();
  if (listViews.has(view.name)) applyParams(view.params);
  refreshResults();
  if (focus) heading.focus({ preventScroll: true });
}

function pickerMatches(project) {
  return project.sponsors.filter((name) => selectedSponsors.has(normalize(name))).length;
}

function prizeItem(award) {
  const item = element("li");
  const text = element("span");
  let title = award.title;
  if (award.sponsor) {
    const lead = normalize(title).startsWith(normalize(award.sponsor) + " ");
    if (lead) title = title.slice(award.sponsor.length).replace(/^[\s:–-]+/, "");
    text.append(link(award.sponsor, sponsorHref(award.sponsor), "prize-sponsor"), " ");
  }
  text.append(element("span", title, "prize-title"));
  item.append(icon("award"), text);
  return item;
}

function projectCard(project) {
  const card = element("article", "", "card");
  const title = element("h2", "", "card-title");
  title.append(link(project.name, project.devpost || "#"));
  card.append(title);

  const meta = element("p", "", "card-event");
  meta.append(element("span", project.edition || "Hackathon not listed"));
  if (Number.isInteger(project.team) && project.team > 0) {
    meta.append(element("span", project.team === 1 ? "Solo project" : `Team of ${project.team}`));
  }
  card.append(meta);

  if (currentView.name === "picker") {
    card.append(element("p", `Matches ${pickerMatches(project)} of ${selectedSponsors.size} picked sponsors`, "card-match"));
  }

  const focus = currentView.name === "sponsor" ? normalize(currentView.sponsor) : "";
  const awards = [...project.sponsorAwards].sort((a, b) =>
    Number(normalize(b.sponsor) === focus) - Number(normalize(a.sponsor) === focus));
  const others = project.awards.filter((award) => !award.sponsor);
  if (awards.length) {
    const list = element("ul", "", "card-prizes");
    list.setAttribute("aria-label", "Sponsor prizes");
    for (const award of awards.slice(0, 2)) list.append(prizeItem(award));
    card.append(list);
  }
  const extra = [...awards.slice(2), ...others];
  if (extra.length) {
    const details = element("details", "", "card-more");
    details.append(element("summary", `+${plural(extra.length, "more prize")}`));
    const list = element("ul", "", "card-prizes");
    for (const award of extra) list.append(prizeItem(award));
    details.append(list);
    card.append(details);
  }

  if (project.summary) {
    const summary = element("p", project.summary, "card-summary");
    summary.title = project.summary;
    card.append(summary);
  }
  const integrations = [...(project.integrations ?? [])].sort((a, b) =>
    Number(normalize(b.sponsor) === focus) - Number(normalize(a.sponsor) === focus));
  const notes = element("dl", "", "card-integrations");
  for (const { heading, sponsor, note } of integrations) {
    notes.append(
      element("dt", heading || (sponsor ? `How it used ${sponsor}` : "Sponsor use")),
      element("dd", note),
    );
  }
  if (integrations.length) card.append(notes);
  if (project.tech.length) {
    const tech = element("p", "", "card-tech");
    tech.append(element("span", "Built with ", "sr-only"), project.tech.slice(0, 8).join(" · "));
    tech.title = project.tech.join(", ");
    card.append(tech);
  }

  const links = element("div", "", "card-links");
  const code = project.code || project.github;
  for (const [label, url, name] of [["Devpost", project.devpost, "out"], ["Code", code, "code"], ["Demo", project.demo, "play"]]) {
    if (!url && name === "code") links.append(element("span", "No public code linked", "card-code-missing"));
    if (!url) continue;
    const anchor = link("", url);
    anchor.append(icon(name), element("span", label));
    anchor.setAttribute("aria-label", `${label} for ${project.name}`);
    links.append(anchor);
  }
  card.append(links);
  return card;
}

function renderBatch(start = 0) {
  const cards = displayed.slice(start, limit).map(projectCard);
  results.append(...cards);
  const remaining = displayed.length - limit;
  more.hidden = remaining <= 0;
  more.textContent = `Show ${Math.min(remaining, batchSize)} more of ${format(remaining)}`;
  return cards;
}

function emptyState(isPicker) {
  const box = element("div", "", "empty-state");
  box.append(element("p", isPicker ? "No past winners match these sponsors." : "No projects match these filters."));
  if (!isPicker) {
    const reset = element("button", "Clear filters", "button");
    reset.type = "button";
    reset.addEventListener("click", () => {
      resetFilters();
      refreshResults();
      search.focus();
    });
    box.append(reset);
  }
  return box;
}

function refreshResults() {
  results.replaceChildren();
  const { name, sponsor } = currentView;
  const isPicker = name === "picker";
  const showResults = !["sponsors", "hackathons"].includes(name) && (!isPicker || selectedSponsors.size > 0);
  byId("result-toolbar").hidden = !showResults;
  more.hidden = true;
  const filtered = Boolean(search.value) || Object.values(filters).some((filter) => filter.value);
  byId("clear").hidden = !filtered;
  if (isPicker) pickerSummary.replaceChildren();
  syncHash();
  if (!showResults) return;

  const query = normalize(search.value).split(/\s+/).filter(Boolean);
  displayed = projects.filter((project) => {
    if (name === "champions" && !project.isChampion) return false;
    if (name === "sponsor" && !matchingSponsor(project, sponsor)) return false;
    if (isPicker) return pickerMatches(project) > 0;
    return query.every((term) => project.keywords.includes(term))
      && (!filters.sponsor.value || matchingSponsor(project, filters.sponsor.value))
      && (!filters.event.value || normalize(project.event) === filters.event.value)
      && (!filters.year.value || project.year === filters.year.value)
      && (!filters.tech.value || project.tech.some((tag) => normalize(tag) === filters.tech.value));
  });
  if (isPicker) {
    const picked = element("p", "", "picked");
    const names = sponsors.filter(({ label }) => selectedSponsors.has(normalize(label))).map(({ label }) => label);
    picked.append(element("strong", "Picked: "), names.join(", ") + " ");
    const reset = element("button", "Clear picks", "text-button");
    reset.type = "button";
    reset.addEventListener("click", () => {
      selectedSponsors.clear();
      for (const box of context.querySelectorAll(".picker-choices input")) box.checked = false;
      refreshResults();
    });
    picked.append(reset);
    pickerSummary.append(picked);
    const insights = rankedList("Tech these winners used most", tally(displayed, (project) => project.tech), null, "h2");
    if (insights) pickerSummary.append(insights);
  }

  const alphabetical = (a, b) => collator.compare(a.name, b.name);
  displayed.sort((a, b) => {
    if (sort.value === "name") return alphabetical(a, b);
    if (sort.value === "awards" && b.sponsorAwards.length !== a.sponsorAwards.length) {
      return b.sponsorAwards.length - a.sponsorAwards.length;
    }
    if (sort.value === "match") {
      const difference = pickerMatches(b) - pickerMatches(a);
      if (difference) return difference;
    }
    return Number(b.year) - Number(a.year) || b.sponsorAwards.length - a.sponsorAwards.length || alphabetical(a, b);
  });

  byId("result-status").textContent = plural(displayed.length, "project");
  byId("clear").hidden = !filtered || !displayed.length;
  sort.parentElement.hidden = !displayed.length;
  if (displayed.length) renderBatch();
  else results.append(emptyState(isPicker));
}

theme.value = document.documentElement.dataset.theme ?? "system";
theme.addEventListener("change", () => {
  const root = document.documentElement;
  if (theme.value === "system") delete root.dataset.theme;
  else root.dataset.theme = theme.value;
  try {
    if (theme.value === "system") localStorage.removeItem("tracks-theme");
    else localStorage.setItem("tracks-theme", theme.value);
  } catch {
    // The selected theme still applies for this visit.
  }
});

window.addEventListener("storage", (event) => {
  if (event.key !== "tracks-theme" && event.key !== null) return;
  if (event.newValue === "light" || event.newValue === "dark") {
    document.documentElement.dataset.theme = event.newValue;
  } else {
    delete document.documentElement.dataset.theme;
  }
  theme.value = document.documentElement.dataset.theme ?? "system";
});

if (!projects.length) {
  byId("load-error").hidden = false;
} else {
  byId("catalog-stats").append(
    stat("winning projects", projects.length), stat("sponsors", sponsors.length), stat("hackathon editions", editions.size),
  );
  for (const [key, { label, values }] of Object.entries(options)) {
    const ordered = [...values].sort((a, b) => key === "year"
      ? Number(b.label) - Number(a.label) : collator.compare(a.label, b.label));
    filters[key].append(new Option(label, ""));
    for (const { label: value } of ordered) filters[key].append(new Option(value, normalize(value)));
  }

  function onFilterChange() {
    limit = batchSize;
    refreshResults();
  }

  let typing;
  search.addEventListener("input", () => {
    clearTimeout(typing);
    typing = setTimeout(onFilterChange, 120);
  });
  for (const filter of Object.values(filters)) filter.addEventListener("change", onFilterChange);
  sort.addEventListener("change", onFilterChange);
  byId("clear").addEventListener("click", () => {
    resetFilters();
    refreshResults();
    search.focus();
  });
  more.addEventListener("click", () => {
    const start = limit;
    limit += batchSize;
    const [first] = renderBatch(start);
    const anchor = first?.querySelector(".card-title a");
    if (anchor) anchor.focus();
  });
  window.addEventListener("hashchange", () => {
    if (location.hash === "#main" || location.hash.startsWith("#letter-")) return;
    applyView(getView(), true);
  });
  for (const navLink of document.querySelectorAll(".section-nav a, .brand")) {
    navLink.addEventListener("click", () => {
      if (navLink.hash === location.hash) heading.focus();
    });
  }
  applyView(getView());
}
