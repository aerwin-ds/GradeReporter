# Grade Reporter — Minimal Collaborative Setup

This is a *minimal* starting point so a team of 4 can collaborate **today** using branching + PRs while the code still lives in a single notebook.

## What's here
- `notebooks/GradeReporter_Demo_1.ipynb` — your current Colab notebook
- `.jupytext.toml` — tells Jupytext to pair the notebook with a `.py` script for readable diffs
- `requirements.txt` — start list; add to it as you import new libraries
- `.gitignore` — keeps repos clean

## Team workflow (quick)
1) **Clone & venv**
```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
pip install jupytext
```
2) **Pair the notebook with a .py for code reviews**
```bash
jupytext --set-formats ipynb,py:percent notebooks/GradeReporter_Demo_1.ipynb
# After edits, keep the .py in sync:
jupytext --sync notebooks/GradeReporter_Demo_1.ipynb
```
3) **Branch & PR**
```bash
git checkout -b feat/<short-topic>
git add notebooks/GradeReporter_Demo_1.ipynb notebooks/GradeReporter_Demo_1.py
git commit -m "feat: <what you changed>"
git push -u origin feat/<short-topic>
# Open a Pull Request to main
```
4) **Rule of thumb**
- Never push to `main` directly
- Always update the paired `.py` (`jupytext --sync`) before committing
- Keep outputs in the notebook if you need them; reviewers can rely on the `.py` for diffs

## Optional (nice-to-have, still simple)
- Add branch protections for `main` (1 review required)
- Enable "Require PRs to be up to date with base branch"

---

When you're ready to go beyond the notebook, create `src/` and start moving functions into modules. Until then, this setup lets everyone collaborate without friction.
