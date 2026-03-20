# AGENTS.md

## Cursor Cloud specific instructions

This is a pure-Python CLI pipeline with no web server, database, or Docker dependencies. Python 3.x (stdlib only) is the sole runtime requirement.

### Running the pipeline end-to-end

```bash
# 1. Download the upstream source
curl -o all.md "https://raw.githubusercontent.com/ttttmr/Wechat2RSS/refs/heads/master/list/all.md"

# 2. Validate the source markdown
python3 scripts/validate_source.py all.md

# 3. Convert to OPML
python3 scripts/convert_to_opml.py all.md wechat2rss.opml
```

### Key notes

- **No external pip packages are needed.** All code uses only stdlib modules (`xml.etree.ElementTree`, `re`, `sys`, `os`).
- **No lint/test framework exists in this repo.** You can syntax-check the scripts with `python3 -m py_compile scripts/convert_to_opml.py scripts/validate_source.py`.
- The `all.md` source file is not committed; it is downloaded at runtime from `ttttmr/Wechat2RSS`.
- The output `wechat2rss.opml` is the committed artifact (~408 lines, ~393 RSS feeds across 4 categories).
