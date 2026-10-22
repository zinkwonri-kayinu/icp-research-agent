---
name: icp-search
description: Research a company from its website URL or LinkedIn company URL and work out its Ideal Customer Profile (ICP) — what it sells most, who it sells to (based on its testimonials, case studies, reviews and customer logos), the buyer persona, buying signals and who to avoid. Outputs a Clay list-building filter format plus a table of 5 real example companies that fit, each with the reason and signals. Use when the user shares a company URL/LinkedIn and asks for its ICP, ideal customers, who it sells to, or lookalike target accounts.
---

# ICP Search

Input: a company website URL (`acme.com`) or LinkedIn company URL (`linkedin.com/company/acme`). If there are several, run the whole workflow for each one.

Output: a sourced ICP, a Clay list-building format, and a table of 5 example companies that fit.

Tools: WebFetch / WebSearch for research (load them with ToolSearch if deferred). The Clay MCP tools (`mcp__clay__search-companies`, `mcp__clay__add-company-data-points`, `mcp__clay__search-contacts-by-name`) check firmographics and find example companies. If Clay is unavailable, fall back to web research and say so in the output.

## 1. Resolve the company
- LinkedIn URL: get the company name, website, industry, headcount and description from the LinkedIn page or a web search. Then continue with the website.
- Website URL: get the company name and its LinkedIn page.

## 2. Find what they sell most
Read the homepage, product/solutions pages, pricing page and "customers" page. The main product is the one that:
- sits first in the hero section and navigation
- has pricing or a "book a demo" CTA attached
- appears most in their own marketing elsewhere: LinkedIn posts, G2/Capterra listing, press releases, blog and ad copy (search `"<company>" <product>` and `site:linkedin.com "<company>"`)

Note the main product, the problem it solves, and any industry or role named in the copy ("built for RevOps teams at B2B SaaS").

## 3. Find who they sell to (evidence)
Collect every customer you can find, in this order of strength:
1. **Case studies**: company name, industry, size, results
2. **Testimonials and reviews on the site**: reviewer name, title, company
3. **Third-party reviews**: G2, Capterra, Trustpilot, Product Hunt (reviewer title, company size segment, industry)
4. **Customer logos** on the homepage or customers page
5. **Fallback if there's little or nothing above:** the competitors' customers, their job posts (sales and marketing roles often name target segments), their own LinkedIn posts and webinars

For each named reviewer or customer:
- Look up the person (LinkedIn or web search, or `mcp__clay__search-contacts-by-name`): their title, seniority and department.
- Look up their company with `mcp__clay__add-company-data-points` or the web: industry, headcount, revenue, funding stage, HQ location, business model (B2B/B2C), and notable tools they use.

Aim for 5–15 data points. Put them in a working table, then find the patterns: what most of them have in common is the ICP. A pattern counts only if at least 2 customers share it. Track how many customers share each trait.

Don't count by eye. Save the table as a CSV with the columns `customer,reviewer,title,industry,employees,stage,geography,business_model,tech_stack,source` (multiple tools separated by `;`) and run:

```
python scripts/icp_patterns.py evidence.csv
```

It keeps only traits shared by 2+ customers, buckets headcount and job titles, and returns each field with a confidence grade and the exact count ("5 of 7"). Use its output as the backbone of step 4. Copy those counts word for word and don't round them up.

## 4. Build the ICP
Every field needs evidence ("5 of 7 customers were 50–200 employees") and a confidence level: High (strong, consistent pattern), Medium (some evidence), Low (inferred from copy only).

- **Company:** industry, sub-industry, employee range, revenue range (only if relevant), funding/growth stage, geography, business model, tech stack (only if relevant)
- **Buyer persona:** job titles, seniority and department of the people who buy or champion it (from the reviewers' titles)
- **Buying signals:** events that suggest a company may be ready to buy now, e.g. recent funding, hiring for specific roles, a new leader in the buyer's role, using a competitor or a complementary tool, fast headcount growth, expansion into new markets
- **Who to avoid:** companies that look like a fit but aren't (too small or too big, wrong model, competitors, existing customers)

## 5. Find 5 example companies
- Turn the ICP into filters and run `mcp__clay__search-companies` (industry, headcount, location, keywords). Use web search to confirm signals (funding news, job posts, tools used).
- Small and mid-size companies are fine, even preferred. Don't just list famous brands.
- Exclude the company itself, its competitors, and any customers already found in step 3.
- Each example must show at least one buying signal you actually verified. Never invent a signal: if you couldn't confirm one, say "no live signal found" and explain the fit instead.

## 6. Output format
Print in the terminal, in this layout:

```
# ICP Search: <Company> (<website>)

## What they sell
Main product: ... | Problem it solves: ... | How sure: <High/Med/Low> (why)

## Evidence (customers analysed)
| Customer | Reviewer & title | Industry | Employees | Stage | Source |
(one row per customer found)

## ICP: Clay list-building format
**Company filters**
- Industry: ...
- Company size (employees): ...
- Revenue: ... (omit if not relevant)
- Growth stage / funding: ...
- Geography: ...
- Business model: ...
- Keywords / description contains: ...
- Tech stack: ... (omit if not relevant)

**People filters (buyer persona)**
- Job titles: ...
- Seniority: ...
- Department: ...

**Buying signals to layer on**
- ...

**Who to avoid**
- ...

Each line ends with (Confidence: H/M/L — evidence).

## 5 example companies that fit
| # | Company | Website | Why it fits the ICP | Signals |
|---|---------|---------|---------------------|---------|
| 1 | ... | ... | ... | ... |
```

Finish with a single line offering to pull contacts that match the buyer persona at these 5 companies, or more lookalike companies, with Clay.

## Rules
- Use only facts you found. Name the source for each claim, and say where something is a guess.
- If the site has no customer evidence, say so plainly. Build the ICP from the fallback sources and mark confidence Low/Medium.
- Keep it scannable: tables and short lines, no padding.
