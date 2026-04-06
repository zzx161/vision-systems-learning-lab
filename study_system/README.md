# Linux System and Computer Architecture Study System

This directory is your long-term study workspace for:

- Linux system fundamentals
- Performance analysis and troubleshooting
- Computer architecture for engineers
- Camera pipeline and data-path engineering thinking

The goal is not to "read everything once".
The goal is to build durable understanding through:

1. A stable roadmap
2. Small experiments
3. Repeated review
4. Written notes in your own words
5. Ongoing iteration across sessions

## How We Will Use This

- `roadmap.md`
  The full module map and learning sequence.
- `integrated_route.md`
  The career-oriented route that combines system engineering, camera pipeline, edge deployment, and robotics transition.
- `course_plan.md`
  The lesson-by-lesson teaching order.
- `current_sprint.md`
  What you are learning right now.
- `dashboard.md`
  The main Obsidian home note for tracking progress.
- `courses/`
  Structured lesson content.
- `memory/`
  Long-term notes and concept cards.
- `labs/`
  Small hands-on exercises and experiment ideas.
- `reviews/`
  Weekly review logs and confusion tracking.
- `tracking/`
  Bases views plus generated progress snapshots.
- `templates/`
  Reusable note templates for sessions and reviews.
- `scripts/`
  Small automation helpers for updating progress and creating session notes.
- `public/`
  Generated static site for public hosting.

Every time you come back, we can:

1. Check `current_sprint.md`
2. Continue the next item
3. Update your notes
4. Add review questions
5. Adjust the roadmap

This folder is the "external memory" so progress does not disappear with the chat.

## Tracking Workflow

This vault is now set up to work well in Obsidian:

1. Open `dashboard.md`
2. Read or study from the lesson notes
3. Create a session note with:
   `python3 scripts/new_session.py`
4. Refresh the progress snapshot with:
   `python3 scripts/update_progress.py`
5. Open the generated web dashboard:
   `tracking/index.html`
6. If you are in WSL, open it in Windows with:
   `python3 scripts/open_dashboard.py`
7. If you want a better browser URL, open it on localhost with:
   `python3 scripts/open_dashboard_localhost.py`
8. If you want a public static site build, run:
   `python3 scripts/build_public_site.py`

If the Bases core plugin is enabled in Obsidian, the files in `tracking/` provide sortable database views.
