# Demo Script

## Setup

- Empty folder, no git
- Have a terminal ready to run `uv run python app.py` when needed

## Act 1: Research

> I want to build a tool that implements the human fatigue stress models developed by sesek, schall, and others at auburn university. dyor to find that work and identify the key implementation details

*Agent does web research. Takes a few minutes. Produces research summary with formulas, constants, references.*

Additional prompts (use as needed to steer):
- > can you extract the details from the published python models?
- > are there other primary authors of this work gallager, others?
- > stick with auburn pubs. stop and tell me where you are at
- > keep looking for the duet and shoulder tool models. use agents

> write up your findings so far

*Creates RESEARCH.md. Review it briefly - point out the three tools, the S-N curve, the key constants.*

## Act 2: Vibe coding

> what should we build with it? propose something simple to start with that can be developed into a full-featured interactive web app

*Agent proposes CLI → API → frontend roadmap. Scenario comparison surfaces as the key differentiator.*

> please build a simple cli calculator based on what you know about those models. start with one model but make it extensible

*Creates fatigue_calc.py - single file, ~200 lines, LiFFT only. Run it:*

```
python3 fatigue_calc.py lifft -t 10,0.4,500
python3 fatigue_calc.py lifft -t 10,0.4,500,Palletizing -t 5,0.3,200,Stacking
```

> please write some tests for this

*Creates test file, runs tests. All pass.*

> expand it to cover the other models

*Adds DUET + Shoulder Tool to calculator and tests. Note: a bug surfaced in shoulder CLI parsing - tests caught it.*

Additional prompts (use as needed to polish):
- > how do I use it?
- > add examples to the help text for other models
- > write a script that I could use to demo this tool
- > add colored output
- > is this all complete: [original CLI proposal]
- > my instructor says I should use version control. what does that mean and can you help me set it up?

## Act 3: Structured approach

> I'd like to do this next: [paste the web app feature list]
> my professor says that we should separate the work into these items:
> 1. Define the problem clearly
> 2. Research the domain
> 3. Write a constitution
> 4. Write a specification
> 5. Develop a plan
> 6. Identify tasks and prioritize
> 7. Implement incrementally
> 8. Verify and validate at each stage
> please propose a plan for steps 3 thru 6

*Agent proposes constitution, spec, plan, tasks. Review together.*

> please write them up

*Creates SPEC.md with constitution, spec, plan, 7 tasks with acceptance criteria.*

## Act 4: Incremental build

> should we do all 7 tasks at once or take it step by step?

*Agent recommends step by step. Tasks 1-4 together, then 5-6, then 7.*

> yes [start tasks 1-4]

*Creates app.py (FastAPI) + static/index.html. Can't bind port in sandbox.*

> can you run it for me

*No - sandbox limitation. Run it yourself:*

```
uv run python app.py
```

*Open http://localhost:8000 - show model selector, task form, live results.*

> add tests?

*Creates test_app.py - 19 API tests, all pass. 95 total.*

> is it safe to do that with other tasks?

*Agent says 5+6 are independent, safe to batch. 7 should be separate.*

> [tasks 5-6: gauge + chart]

*Adds semicircular SVG probability gauge, stacked damage bar chart, example tasks per model.*

> [task 7: scenario comparison]

*Adds save baseline, side-by-side view, delta display with green/red coding.*

Additional prompts (use as needed during build):
- > commit those changes?
- > what's next?
- > what's left?
- > can you add some default tasks for each model so that I can quickly test things?

## Act 5: Reflection

> where should we go from here?

*Discussion of polish, model extensions, hosting, mobile. Shows the tool is a foundation, not a finished product.*

> what should I learn from this effort?

*Key takeaways:*
- Research first, build second
- Start with math, not UI
- Tests catch bugs early (shoulder parser)
- Incremental delivery = always working
- The contrast between vibe coding and structured approach is the demo's point

Additional prompts (use to explore scope):
- > could you build a mobile friendly version of this?
- > could you help me host it somewhere?
- > what about an ios or android native app?

## Key moments to highlight

1. Research agent finds formulas, reverse-engineers missing coefficients
2. Vibe coding produces working software fast but rough
3. Tests immediately catch a bug in the shoulder tool parser
4. Spec forces clarity on what "scenario comparison" actually means
5. Each commit is a working state - 4 clean commits tell the story
6. The web app never reimplements math - just wraps tested code

## Commit history (for reference)

```
b08df38 Initial commit: fatigue failure MSD risk calculator
202075d Add web app with FastAPI API and interactive frontend
2aa2e3f Add probability gauge, stacked damage chart, and example tasks
2f3c97d Add scenario comparison and mark all spec tasks complete
```
