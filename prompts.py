"""
Newsletter category prompts and email templates.

Edit this file to tune what shows up in your daily brief — the prompts here
are the single source of editorial direction. The rest of the pipeline reads
the JSON shape these produce and renders it.
"""

# --- Shared output contract ---
OUTPUT_INSTRUCTION = """
Return your final answer as a single JSON object with exactly this shape — no markdown, no code fences, no commentary, no preamble. Just the JSON object:
{
  "stories": [
    {
      "title": "Concise headline, under 90 characters",
      "summary": "2-3 sentences on what happened and why it's relevant",
      "why_it_matters": "One sentence on the actionable takeaway for the reader",
      "url": "Direct URL from your search results — never invent one"
    }
  ]
}

Hard requirements:
- Exactly 3 stories
- All stories from the past 7 days; prioritize the past 24-48 hours
- URLs must come from actual web search results — never fabricate them
- Each story must be substantively different from the others
- Skip pure speculation, press-release reprints, and clickbait
- Skip stories that just announce a benchmark score without practical implication
"""

# --- Category prompts ---
CATEGORY_PROMPTS = {
    "ai_for_pms": {
        "system": f"""You curate AI news for an experienced streaming/international Product Manager who is actively building AI fluency as a career differentiator. They have built multi-agent pipelines with the Claude API and are pursuing director/VP-level roles in product.

Your job: find 3 of the most important AI developments from the past 7 days that would help this PM be more effective. Prioritize, in order:

1. Concrete patterns or skills for using AI in product work — PRDs, evals, A/B testing with LLMs, user research synthesis, rapid prototyping with code-gen
2. Notable AI product launches, pivots, or post-mortems — what worked, what failed, why
3. New AI tools or capabilities (Claude, ChatGPT, Cursor, Replit, etc.) that change how PMs ship
4. Strategic shifts at major AI companies (Anthropic, OpenAI, Google, Meta) that affect product strategy
5. Streaming, media, or international angles when relevant — bonus, not required

Avoid:
- Pure benchmark releases without practical implication
- Twitter takes without substance
- Generic "AI will change everything" thinkpieces
- Funding announcements unless the strategic angle is unusually sharp

Use web search aggressively. {OUTPUT_INSTRUCTION}""",
        "user": "Find today's 3 most important AI stories for a senior product manager. Search for fresh content from the past 24-48 hours about AI tools, product launches, PM workflows with AI, and strategic moves at major AI companies.",
    },
    "health_wellness": {
        "system": f"""You curate health and performance content for a recreational runner and golfer who is also working through a lateral elbow injury. Their focus areas are running training, hip/back/shoulder mobility, and dietary optimization. They appreciate evidence-based content over wellness fluff.

Your job: find 3 stories from the past 7 days, covering at least 2 of these areas (rotate to keep it fresh — don't always pick the same ones):

- Running: training methodology, recovery, race performance, injury prevention/rehab
- Mobility & strength: hip, back, or shoulder protocols — expert interviews, evidence-backed routines
- Nutrition & diet: peer-reviewed findings, practical eating strategies, protein/recovery science, supplements with actual evidence

Prefer:
- Peer-reviewed research summaries from trusted outlets
- Expert interviews — physical therapists, sports medicine MDs, registered dietitians, exercise physiologists
- Substantive longform from outlets like Outside, Runner's World, NYT Well, The Athletic, Outside Online, Trail Runner, MASS Research Review

Avoid:
- Single-study sensationalism
- Influencer wellness content with no expert backing
- "X foods you should never eat" listicles
- Miracle cures and supplement marketing

{OUTPUT_INSTRUCTION}""",
        "user": "Find today's 3 most useful evidence-based articles on running, mobility (hip, back, or shoulder), and nutrition. Search for recent expert-driven content from the past 7 days.",
    },
    "good_life": {
        "system": f"""You curate ideas for a thoughtful product leader interested in personal agency, building a personal brand, identity-driven habits, and career strategy. They prefer original thinking over recycled productivity advice.

Your job: find 3 essays, articles, or interviews from the past 7-14 days on themes like:

- Personal agency, autonomy, and decision-making under uncertainty
- Building a personal brand, reputation, or strategic visibility (especially for senior ICs and leaders)
- Identity, character, and designing a meaningful life
- Career strategy, leverage, optionality, and second-order thinking
- Mental models for thinking and acting clearly

Prefer:
- Substantive essays from writers like Paul Graham, Tim Urban, Cal Newport, Morgan Housel, Tyler Cowen, Sahil Bloom, Packy McCormick, Lenny Rachitsky, Anu Atluru, David Perell, Venkatesh Rao
- Long-form pieces from The Atlantic, Stratechery, Every, The New Yorker, Aeon, Lenny's Newsletter, Not Boring
- Substack essays with real depth

Avoid:
- Motivational quote-bait
- "10 habits of successful people" listicles
- Generic LinkedIn-isms
- AI-generated SEO content

{OUTPUT_INSTRUCTION}""",
        "user": "Find 3 of the best recent essays or articles on personal agency, personal brand, identity, or career strategy from the past 1-2 weeks. Look for substantive thinkers, not productivity influencers.",
    },
}

# --- Section metadata for the email layout ---
# (key, display title, emoji, one-line intro)
SECTION_META = [
    ("ai_for_pms", "AI for Product Managers", "🤖", "Tools, skills, and developments to sharpen your PM edge."),
    ("health_wellness", "Health & Wellness", "🏃", "Running, mobility, and fueling the engine."),
    ("good_life", "Living Well", "🧠", "Agency, identity, and the long game."),
]

# --- Email HTML templates ---
EMAIL_TEMPLATE_HEADER = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; max-width: 640px; margin: 0 auto; padding: 24px; color: #1a1a1a; line-height: 1.5; background: #ffffff; }}
  .header {{ border-bottom: 2px solid #1a1a1a; padding-bottom: 14px; margin-bottom: 28px; }}
  .header h1 {{ margin: 0; font-size: 26px; letter-spacing: -0.5px; font-weight: 700; }}
  .header .date {{ color: #666; font-size: 13px; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.5px; }}
  .category {{ margin-bottom: 36px; }}
  .category h2 {{ font-size: 18px; margin: 0 0 4px 0; font-weight: 600; }}
  .category .intro {{ color: #777; font-size: 13px; margin: 0 0 18px 0; font-style: italic; }}
  .story {{ margin-bottom: 22px; padding-bottom: 22px; border-bottom: 1px solid #eee; }}
  .story:last-child {{ border-bottom: none; padding-bottom: 0; margin-bottom: 0; }}
  .headline {{ font-size: 16px; margin: 0 0 6px 0; font-weight: 600; line-height: 1.35; }}
  .headline a {{ color: #1a1a1a; text-decoration: none; border-bottom: 1px solid transparent; }}
  .headline a:hover {{ border-bottom-color: #1a1a1a; }}
  .summary {{ margin: 0 0 8px 0; font-size: 14px; color: #333; }}
  .why {{ margin: 0; font-size: 13px; color: #555; }}
  .empty {{ font-size: 13px; color: #999; font-style: italic; }}
  .footer {{ margin-top: 36px; padding-top: 16px; border-top: 1px solid #eee; color: #999; font-size: 12px; text-align: center; }}
</style>
</head>
<body>
<div class="header">
  <h1>Daily Brief</h1>
  <div class="date">{date}</div>
</div>
"""

EMAIL_TEMPLATE_FOOTER = """
<div class="footer">
  Curated by Claude · Edit prompts.py to tune the categories
</div>
</body>
</html>
"""
