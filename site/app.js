"use strict";

const byId = (id) => document.getElementById(id);
const collator = new Intl.Collator("en", { sensitivity: "base", numeric: true });
const normalize = (text) => String(text ?? "").trim().toLowerCase();
const format = (number) => number.toLocaleString("en");
const batchSize = 18;

function element(tag, text, className) {
  const node = document.createElement(tag);
  if (text) node.textContent = text;
  if (className) node.className = className;
  return node;
}

function tally(projects, labels) {
  const counts = new Map();
  for (const project of projects) {
    const unique = new Map(labels(project).filter(Boolean).map((label) => [normalize(label), label]));
    for (const [key, label] of unique) {
      if (!counts.has(key)) counts.set(key, { label, count: 0 });
      counts.get(key).count++;
    }
  }
  return [...counts.values()].sort((a, b) => b.count - a.count || collator.compare(a.label, b.label));
}

const projects = (window.TRACKS_CATALOG ?? []).map((project) => ({
  ...project,
  edition: [project.event, project.year].filter(Boolean).join(" · "),
  isChampion: project.sponsors.length >= 2 || project.awards.filter((award) => award.sponsor).length >= 2,
  keywords: normalize([
    project.name, project.summary, project.event, project.year, ...project.sponsors,
    ...project.tech, ...project.awards.map((award) => award.title),
  ].join(" ")),
}));
const sponsors = tally(projects, (project) => project.sponsors);
const editions = tally(projects, (project) => project.event ? [project.edition] : []);
const options = {
  sponsor: { label: "Sponsor", values: sponsors },
  event: { label: "Hackathon", values: tally(projects, (project) => [project.event]) },
  year: { label: "Year", values: tally(projects, (project) => [project.year]) },
  tech: { label: "Tech", values: tally(projects, (project) => project.tech) },
};
const filters = Object.fromEntries(Object.keys(options).map((key) => [key, byId("filter-" + key)]));
const mainViews = new Set(["browse", "sponsors", "champions", "picker"]);
const search = byId("search");
const sort = byId("sort");
const context = byId("context");
const results = byId("results");
const heading = byId("view-title");
const more = byId("more");
const selectedSponsors = new Set();
const theme = byId("theme");
let currentView = { name: "browse" };
let limit = batchSize;
let displayed = [];
let pickerSummary;

function sponsorHref(sponsor) {
  return "#sponsor=" + encodeURIComponent(sponsor);
}

function getView(hash = location.hash) {
  const route = hash.slice(1);
  if (route.startsWith("sponsor=")) {
    try {
      const key = normalize(decodeURIComponent(route.slice("sponsor=".length)));
      const sponsor = sponsors.find((entry) => normalize(entry.label) === key);
      if (sponsor) return { name: "sponsor", sponsor: sponsor.label };
    } catch {
      // A malformed sponsor link returns to the directory.
    }
    return { name: "sponsors" };
  }
  return { name: mainViews.has(route) ? route : "browse" };
}

function stat(label, count) {
  const item = element("li");
  item.append(element("strong", format(count)), element("span", label));
  return item;
}

function matchingSponsor(project, sponsor) {
  return project.sponsors.some((name) => normalize(name) === normalize(sponsor));
}

function rankedList(title, entries, hrefForLabel) {
  if (!entries.length) return null;
  const panel = element("section");
  panel.append(element("h3", title));
  const list = element("ul", "", "ranked");
  for (const { label, count } of entries.slice(0, 5)) {
    const row = element("li");
    const name = element(hrefForLabel ? "a" : "span", label);
    if (hrefForLabel) name.href = hrefForLabel(label);
    row.append(name, element("strong", format(count), "rank-count"));
    list.append(row);
  }
  panel.append(list);
  return panel;
}

function showSponsor(sponsor) {
  const entries = projects.filter((project) => matchingSponsor(project, sponsor));
  const panel = element("section", "", "insights");
  panel.append(element("h3", "What winners have in common"));
  panel.append(element("p", "Counts show how many listed projects share each trait. Tech is taken from the tags available in the catalog."));
  const group = element("div", "", "insight-grid");
  const lists = [
    rankedList("Most listed tech", tally(entries, (project) => project.tech)),
    rankedList("Hackathon editions", tally(entries, (project) => [project.edition])),
    rankedList("Other sponsor prizes", tally(entries, (project) =>
      project.sponsors.filter((name) => normalize(name) !== normalize(sponsor))), sponsorHref),
  ].filter(Boolean);
  if (lists.length) {
    group.append(...lists);
    panel.append(group);
  }
  context.append(panel);
}

function showSponsorDirectory() {
  const list = element("ul", "", "sponsor-directory");
  for (const { label, count } of [...sponsors].sort((a, b) => collator.compare(a.label, b.label))) {
    const item = element("li");
    const link = element("a");
    link.href = sponsorHref(label);
    link.append(element("strong", label), element("span", `${format(count)} ${count === 1 ? "project" : "projects"}`));
    item.append(link);
    list.append(item);
  }
  context.append(list);
}

function showPicker() {
  const panel = element("fieldset", "", "picker");
  panel.append(element("legend", "Sponsors at your event"));
  const find = element("input", "", "picker-search");
  find.type = "search";
  find.placeholder = "Find a sponsor…";
  find.setAttribute("aria-label", "Find a sponsor to pick");
  const choices = element("div", "", "picker-choices");
  const empty = element("p", "No sponsors match that search.");
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
  find.addEventListener("input", () => {
    const query = normalize(find.value);
    let visible = 0;
    for (const chip of choices.children) {
      chip.hidden = !normalize(chip.textContent).includes(query);
      if (!chip.hidden) visible++;
    }
    empty.hidden = visible > 0;
  });
  panel.append(find, choices, empty);
  context.append(panel, pickerSummary);
}

function resetFilters() {
  search.value = "";
  for (const filter of Object.values(filters)) filter.value = "";
  limit = batchSize;
}

function applyView(view, focus = false) {
  currentView = view;
  resetFilters();
  sort.options[0].hidden = view.name !== "picker";
  sort.value = { champions: "awards", picker: "match" }[view.name] ?? "recent";
  const titles = {
    browse: "Winning projects",
    sponsors: "Browse by sponsor",
    sponsor: view.sponsor,
    champions: "Multi-track champions",
    picker: "Track picker",
  };
  const intros = {
    sponsors: "Choose a sponsor to see winning projects and what they have in common.",
    champions: "Projects that won at least two sponsor tracks.",
    picker: "Choose sponsors at your event to see past winners and the tech they used.",
  };

  heading.textContent = titles[view.name];
  const intro = byId("view-intro");
  intro.textContent = intros[view.name] ?? "";
  intro.hidden = !intro.textContent;
  for (const link of document.querySelectorAll("[data-view]")) {
    const navView = view.name === "sponsor" ? "sponsors" : view.name;
    if (link.dataset.view === navView) link.setAttribute("aria-current", "page");
    else link.removeAttribute("aria-current");
  }
  context.replaceChildren();
  context.hidden = view.name === "browse" || view.name === "champions";
  byId("catalog-controls").hidden = view.name === "sponsors" || view.name === "picker";
  filters.sponsor.hidden = view.name === "sponsor";

  if (view.name === "sponsors") showSponsorDirectory();
  if (view.name === "sponsor") showSponsor(view.sponsor);
  if (view.name === "picker") showPicker();
  refreshResults();
  if (focus) heading.focus();
}

function pickerMatches(project) {
  return project.sponsors.filter((name) => selectedSponsors.has(normalize(name))).length;
}

function projectCard(project) {
  const card = element("article", "", "project");
  if (project.image) {
    const image = element("img", "", "project-image");
    image.alt = "";
    image.loading = "lazy";
    image.decoding = "async";
    image.referrerPolicy = "no-referrer";
    image.addEventListener("error", () => image.remove(), { once: true });
    image.src = project.image;
    card.append(image);
  }
  const body = element("div", "", "project-body");
  const meta = [project.edition, Number.isInteger(project.team) && project.team > 0 ? `${project.team} on team` : ""].filter(Boolean);
  if (currentView.name === "picker") meta.push(`${pickerMatches(project)} of ${selectedSponsors.size} sponsors`);
  if (meta.length) body.append(element("p", meta.join("  /  "), "project-meta"));
  body.append(element("h3", project.name));
  if (project.sponsors.length) {
    const badges = element("ul", "", "sponsor-badges");
    for (const sponsor of project.sponsors) {
      const link = element("a", sponsor);
      link.href = sponsorHref(sponsor);
      const item = element("li");
      item.append(link);
      badges.append(item);
    }
    body.append(badges);
  }
  const awards = currentView.name === "sponsor"
    ? [...project.awards].sort((a, b) => Number(normalize(b.sponsor) === normalize(currentView.sponsor))
      - Number(normalize(a.sponsor) === normalize(currentView.sponsor)))
    : project.awards;
  if (awards.length) {
    body.append(element("p", awards[0].title, "prize"));
    if (awards.length > 1) {
      const details = element("details", "", "expand");
      details.append(element("summary", `+${awards.length - 1} ${awards.length === 2 ? "prize" : "prizes"}`));
      const list = element("ul");
      for (const award of awards.slice(1)) list.append(element("li", award.title));
      details.append(list);
      body.append(details);
    }
  }
  if (project.summary) body.append(element("p", project.summary, "project-summary"));
  if (project.tech.length) {
    const tags = element("ul", "", "tech-list");
    for (const tag of project.tech.slice(0, 6)) tags.append(element("li", tag));
    body.append(tags);
    if (project.tech.length > 6) {
      const details = element("details", "", "expand");
      details.append(element("summary", `+${project.tech.length - 6} tech tags`));
      const extras = element("ul", "", "tech-list");
      for (const tag of project.tech.slice(6)) extras.append(element("li", tag));
      details.append(extras);
      body.append(details);
    }
  }
  const links = element("div", "", "project-links");
  for (const [label, url] of Object.entries({ Devpost: project.devpost, GitHub: project.github, Demo: project.demo })) {
    if (!url) continue;
    const link = element("a", label);
    link.href = url;
    link.setAttribute("aria-label", `${label} for ${project.name}`);
    link.append(element("span", " ↗", "link-arrow"));
    link.lastChild.setAttribute("aria-hidden", "true");
    links.append(link);
  }
  if (links.childElementCount) body.append(links);
  card.append(body);
  return card;
}

function renderBatch(start = 0) {
  const cards = displayed.slice(start, limit).map(projectCard);
  results.append(...cards);
  const remaining = displayed.length - limit;
  more.hidden = remaining <= 0;
  more.textContent = `Show ${Math.min(remaining, batchSize)} more`;
  return cards;
}

function refreshResults() {
  results.replaceChildren();
  const { name, sponsor } = currentView;
  const isPicker = name === "picker";
  const showResults = name !== "sponsors" && (!isPicker || selectedSponsors.size > 0);
  byId("result-toolbar").hidden = !showResults;
  more.hidden = true;
  byId("clear").hidden = !search.value && Object.values(filters).every((filter) => !filter.value);
  if (isPicker) pickerSummary.replaceChildren();
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
    const insights = rankedList("Most listed tech among matches", tally(displayed, (project) => project.tech));
    if (insights) pickerSummary.append(insights);
  }

  const alphabetical = (a, b) => collator.compare(a.name, b.name);
  displayed.sort((a, b) => {
    if (sort.value === "name") return alphabetical(a, b);
    if (sort.value === "awards" && b.awards.length !== a.awards.length) return b.awards.length - a.awards.length;
    if (sort.value === "match") {
      const difference = pickerMatches(b) - pickerMatches(a);
      if (difference) return difference;
    }
    return Number(b.year) - Number(a.year) || alphabetical(a, b);
  });

  byId("result-status").textContent = `${format(displayed.length)} ${displayed.length === 1 ? "project" : "projects"}`;
  if (displayed.length) renderBatch();
  else results.append(element("p", isPicker ? "No past winners match these sponsors." : "No projects match. Try another search or clear a filter.", "empty"));
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
    stat("projects", projects.length), stat("sponsors", sponsors.length), stat("hackathon editions", editions.length),
  );
  for (const [key, { label, values }] of Object.entries(options)) {
    const ordered = [...values].sort((a, b) => key === "year"
      ? Number(b.label) - Number(a.label) : collator.compare(a.label, b.label));
    filters[key].append(new Option(label + ": All", ""));
    for (const { label: value } of ordered) filters[key].append(new Option(value, normalize(value)));
  }

  function onFilterChange() {
    limit = batchSize;
    refreshResults();
  }

  search.addEventListener("input", onFilterChange);
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
    const title = first?.querySelector("h3");
    if (title) {
      title.tabIndex = -1;
      title.focus();
    }
  });
  window.addEventListener("hashchange", () => {
    if (location.hash !== "#main") applyView(getView(), true);
  });
  for (const link of document.querySelectorAll(".section-nav a, .brand")) {
    link.addEventListener("click", () => {
      if (link.hash === location.hash) heading.focus();
    });
  }
  applyView(getView());
}
