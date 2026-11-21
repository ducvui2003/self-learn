# AGENT.md — Context & Conventions for Modern Angular Learning Project

> Read this file first. It lets any agent or chat continue the work consistently.

## 1. Goal
- Topic: **Modern Angular (2+)**, not AngularJS 1.x. Use the latest stable version (standalone components, signals, new control flow).
- The user is learning it to work on a **Japan client project**.
- The user already knows **JavaScript, React, Vue and AngularJS 1.x** (see `../angular1/`). Map each concept to a React/Vue/AngularJS equivalent (use comparison tables).
- Keep explanations concise and practical for enterprise codebases. Use modern style: standalone components, `inject()`, signals, `@if`/`@for`, typed forms, `OnPush`.
- Also show legacy style (NgModule, `*ngIf`, constructor injection) in one short note, because Japan enterprise projects often use older Angular versions.

## 2. Folder structure (`angular2/`)
| Path | Purpose |
| :--- | :--- |
| `ROADMAP.md` | Master roadmap: mental-model mapping table + 6 phases. Mark finished phases with ✅ Ready. |
| `phase-N/` | **One folder per phase**. Contains the guide and a runnable example. |
| `phase-N/PHASE-N.md` | Study guide for that phase (concepts + React/Vue/AngularJS mapping tables). |
| `phase-N/` | Runnable Angular CLI example (`npm install` then `ng serve`). |

`angular1/` is a separate AngularJS project and is not part of this work.

## 3. Rules for creating a new phase
1. The user says which phase to do next (for example "start phase 2"). Do only that phase.
2. Create `phase-N/` with `PHASE-N.md` and a runnable example.
3. `PHASE-N.md` must include:
   - a React/Vue/AngularJS/Angular mapping table for each topic;
   - the common pitfalls;
   - Japan-project tips;
   - a section pointing to the example files.
4. The example must be a small, realistic Japan-enterprise scenario (for example an employee directory with JP/EN labels). Comment each concept where it is used.
5. Use TypeScript strict mode, standalone components and `inject()`. **One `ng new` project per phase** (decided by the user): `ng new app --directory phase-N --style=css --ssr=false --zoneless --skip-git --defaults --ai-config=none`. Run it from `angular2/`.
   - **Monorepo (npm workspaces):** `angular2/package.json` holds the shared libs (Angular, rxjs, CLI...) and `"workspaces": ["phase-*"]`. There is ONE `node_modules` at `angular2/`.
   - After `ng new`, make `phase-N/package.json` small: only `name` (`phase-N`), `scripts`, and `dependencies` with **extra libs that only this phase needs**. Delete the shared deps from it. Do not keep a `node_modules` or lock file inside `phase-N`.
   - Add a shared lib: `npm i <lib> --legacy-peer-deps` in `angular2/`. Add a phase-only lib: `npm i <lib> -w phase-N --legacy-peer-deps`.
   - Run `npm install --legacy-peer-deps` in `angular2/` (plain `npm install` fails with `edgesOut`). Run a phase from its own folder: `cd phase-N` then `npm start` (the `ng` command is found in the root `node_modules`). Do not add run scripts to the root `package.json`.
6. After finishing, update `ROADMAP.md` (link the phase, mark it ✅ Ready) and summarize with file links.

## 4. Roadmap status
| Phase | Topic | Status |
| :--- | :--- | :--- |
| 1 | Setup, CLI, project structure, components, templates, control flow | ✅ Done (`phase-1/`) |
| 2 | Signals, inputs/outputs, component communication, lifecycle | ✅ Done (`phase-2/`) |
| 3 | Dependency injection, services, RxJS basics, `HttpClient` + interceptors | ✅ Done (`phase-3/`) |
| 4 | Forms (template-driven, reactive, typed), validation, search/table screens | ✅ Done (`phase-4/`) |
| 5 | Routing, guards, resolvers, lazy loading, directives & pipes | ✅ Done (`phase-5/`) |
| 6 | State management, testing, performance, project conventions | ✅ Done (`phase-6/`) |

## 5. Language rules
- **Main language: English.** Write all guides, code comments and replies in English.
- **Use basic words.** Use short sentences and simple words. Avoid hard or rare words. If a technical term is needed, explain it in one simple line.
- Japanese text may appear only inside example data (for example labels in the demo app), always with an English meaning next to it.

## 6. Communication preferences
- The user writes informal English, so reply simply and concisely.
- Use markdown with clickable file links.
- Ask before changing the roadmap structure.

