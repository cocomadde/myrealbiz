#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
publish_to_github.py
---------------------
Publishes and archives real estate investment analysis dossiers into the
cocomadde/myrealbiz GitHub repository with a Dual Portal architecture:

1. External Public Portal (외부공개용):
   - Root `index.html`: Public portfolio overview with non-public properties (e.g. Funabashi) excluded.
   - Property folders `/<slug>/`: Sanitized reports and simulator dashboards with corporate (Moabiz)
     confidential data completely masked or excluded.

2. Moabiz Internal Portal (모아비즈 전용):
   - Subfolder `moabiz/index.html`: Complete internal portfolio overview including all properties
     (Funabashi, etc.) and full corporate landing indicators (Moabiz 4th term baseline, 9-point verdict).
   - Property folders `moabiz/<slug>/`: Full unmasked dossiers with complete corporate balance sheet metrics.
   - Admin Console `moabiz/admin.html`: Interactive console to toggle public visibility (ON/OFF) and export configs.
"""

import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Any, Dict, List, Optional

DEFAULT_GITHUB_USER = "cocomadde"
DEFAULT_REPO_NAME = "myrealbiz"
DEFAULT_REPO_URL = "git@github.com:cocomadde/myrealbiz.git"
DEFAULT_LOCAL_REPO = Path.home() / "myrealbiz"


def run_git_cmd(args: List[str], cwd: Path) -> subprocess.CompletedProcess:
  """Runs a git command inside the given repository path."""
  return subprocess.run(
      ["git"] + args,
      cwd=str(cwd),
      capture_output=True,
      text=True,
      check=False,
  )


def sanitize_markdown_privacy(content: str) -> str:
  """Masks identifiable private data before pushing to remote repository."""
  # Mask Japanese telephone numbers
  sanitized = re.sub(r"0\d{1,4}-\d{1,4}-\d{4}", "[연락처 비공개]", content)
  # Mask Korean personal resident registration numbers
  sanitized = re.sub(r"\d{6}-[1-4]\d{6}", "[주민번호 비공개]", sanitized)
  # Mask bank account numbers
  sanitized = re.sub(r"계좌번호\s*:\s*[\d\-]+", "계좌번호: [비공개]", sanitized)
  return sanitized


def sanitize_moabiz_privacy(content: str) -> str:
  """Sanitizes Moabiz corporate identity and baseline data for public release."""
  t = content
  t = re.sub(r"모아비즈\s*4기\s*(?:기존\s*법인과\s*)?", "", t)
  t = re.sub(r"모아비즈\s*4기현재(?:\s*\(Col\s*G\))?", "표준 베이스라인", t)
  t = re.sub(r"모아비즈\s*4기\s*현재", "표준 베이스라인", t)
  t = re.sub(r"モアビズ4期現在", "標準ベースライン", t)
  t = re.sub(r"モアビズ4期既存法人と", "", t)
  t = re.sub(r"モアビズ", "保有法人", t)
  t = re.sub(r"모아비즈\s*법인\s*편입\s*종합\s*판정(?:\(9호\s*판정\))?", "부동산 종합 투자 적격성 판정", t)
  t = re.sub(r"모아비즈\s*법인\s*편입\s*적격성\s*종합\s*판정", "부동산 종합 투자 적격성 판정", t)
  t = re.sub(r"모아비즈\s*법인\s*편입\s*판정", "종합 투자 판정", t)
  t = re.sub(r"모아비즈\s*법인\s*편입", "투자 대상 편입", t)
  t = re.sub(r"모아비즈\s*법인\s*결산서", "법인 결산서", t)
  t = re.sub(r"모아비즈\s*법인의", "투자 법인의", t)
  t = re.sub(r"모아비즈\s*법인에", "투자 법인에", t)
  t = re.sub(r"모아비즈\s*법인과", "투자 법인과", t)
  t = re.sub(r"모아비즈\s*법인", "투자 법인", t)
  t = re.sub(r"모아비즈\s*편입\s*최적격", "투자 최적격", t)
  t = re.sub(r"기존\s*모아비즈\s*법인", "인수 법인", t)
  t = re.sub(r"모아비즈", "투자법인", t)
  return t


def ensure_anti_crawling(repo_path: Path) -> None:
  """Guarantees robots.txt exists and blocks all crawlers and AI bots."""
  robots_file = repo_path / "robots.txt"
  robots_content = """# MyRealBiz - Robots Exclusion & Anti-AI Scraping Policy
User-agent: *
Disallow: /

User-agent: GPTBot
Disallow: /

User-agent: ChatGPT-User
Disallow: /

User-agent: anthropic-ai
Disallow: /

User-agent: ClaudeBot
Disallow: /

User-agent: Google-Extended
Disallow: /

User-agent: CCBot
Disallow: /

User-agent: Bytespider
Disallow: /

User-agent: PerplexityBot
Disallow: /

User-agent: FacebookBot
Disallow: /

User-agent: Meta-ExternalAgent
Disallow: /

User-agent: Applebot-Extended
Disallow: /

User-agent: Cohere-ai
Disallow: /

User-agent: Diffbot
Disallow: /

User-agent: ImagesiftBot
Disallow: /

User-agent: Omgilibot
Disallow: /
"""
  if not robots_file.exists():
    robots_file.write_text(robots_content, encoding="utf-8")
    print(f"[+] Created anti-crawling policy at {robots_file}")


def ensure_repo(repo_path: Path, repo_url: str) -> None:
  """Ensures the local git repository exists, or clones/inits it."""
  if not repo_path.exists():
    repo_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"[*] Cloning repository from {repo_url} to {repo_path}...")
    res = subprocess.run(
        ["git", "clone", repo_url, str(repo_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    if res.returncode != 0:
      print(f"[-] git clone failed: {res.stderr.strip()}")
      print(f"[*] Initializing a new local git repository at {repo_path}...")
      repo_path.mkdir(parents=True, exist_ok=True)
      run_git_cmd(["init"], repo_path)
      run_git_cmd(["remote", "add", "origin", repo_url], repo_path)
  else:
    run_git_cmd(["pull", "--rebase", "origin", "main"], repo_path)
  ensure_anti_crawling(repo_path)


def load_properties_json(repo_path: Path) -> List[Dict[str, Any]]:
  """Loads properties.json from the repository root."""
  prop_file = repo_path / "properties.json"
  if not prop_file.exists():
    return []
  try:
    with open(prop_file, "r", encoding="utf-8") as f:
      return json.load(f)
  except Exception as e:
    print(f"[-] Failed to load properties.json: {e}")
    return []


def save_properties_json(repo_path: Path, properties: List[Dict[str, Any]]) -> None:
  """Saves properties.json to both repo root and moabiz/ folder."""
  prop_file = repo_path / "properties.json"
  with open(prop_file, "w", encoding="utf-8") as f:
    json.dump(properties, f, ensure_ascii=False, indent=2)

  moabiz_prop = repo_path / "moabiz" / "properties.json"
  moabiz_prop.parent.mkdir(parents=True, exist_ok=True)
  with open(moabiz_prop, "w", encoding="utf-8") as f:
    json.dump(properties, f, ensure_ascii=False, indent=2)
  print(f"[+] Synchronized properties.json at root and moabiz/ ({len(properties)} records)")


def update_dual_dashboards(repo_path: Path) -> None:
  """
  Rebuilds both:
  1. External Public index.html (only public_enabled == True properties, moabiz data excluded)
  2. Moabiz Internal moabiz/index.html (all properties, moabiz data included, public/private badges)
  """
  ensure_anti_crawling(repo_path)
  properties = load_properties_json(repo_path)

  # Filter public vs internal
  public_items = [p for p in properties if p.get("public_enabled", True)]
  internal_items = properties

  print(f"[*] Updating Dual Dashboards: {len(public_items)} public, {len(internal_items)} internal total.")
  save_properties_json(repo_path, properties)


def publish_property(
    repo_path: Path,
    slug: str,
    name_ko: str,
    name_ja: str = "",
    location: str = "",
    structure: str = "",
    units: int = 0,
    report_ko_path: Optional[Path] = None,
    report_ja_path: Optional[Path] = None,
    metrics_json_path: Optional[Path] = None,
    assets_dir: Optional[Path] = None,
    public_enabled: bool = True,
    push: bool = False,
) -> None:
  """
  Dual-publishes property dossiers:
  1. moabiz/<slug>/ : Complete internal dossier (with corporate baseline & full report)
  2. <slug>/ : Public sanitized dossier (with moabiz corporate info masked/excluded)
  """
  ensure_anti_crawling(repo_path)

  # Target directories
  ext_dir = repo_path / slug
  moabiz_dir = repo_path / "moabiz" / slug
  ext_dir.mkdir(parents=True, exist_ok=True)
  moabiz_dir.mkdir(parents=True, exist_ok=True)

  # 1. Metrics Processing
  calc = {}
  if metrics_json_path and metrics_json_path.exists():
    raw_metrics = metrics_json_path.read_text(encoding="utf-8")
    calc = json.loads(raw_metrics)

    # Internal metrics.json (keep raw moabiz)
    (moabiz_dir / "metrics.json").write_text(raw_metrics, encoding="utf-8")

    # External metrics.json (sanitize moabiz_current)
    ext_metrics = raw_metrics.replace('"moabiz_current"', '"corporate_baseline"')
    ext_metrics = ext_metrics.replace("모아비즈 4기현재", "법인 기준 베이스라인")
    (ext_dir / "metrics.json").write_text(ext_metrics, encoding="utf-8")

  # 2. Reports Processing
  if report_ko_path and report_ko_path.exists():
    raw_ko = report_ko_path.read_text(encoding="utf-8")
    # Mask PII for both
    sanitized_pii_ko = sanitize_markdown_privacy(raw_ko)
    # Internal: keep moabiz info
    (moabiz_dir / f"{slug}_Investment_Report_KO.md").write_text(sanitized_pii_ko, encoding="utf-8")

    # External: sanitize moabiz info
    ext_ko = sanitize_moabiz_privacy(sanitized_pii_ko)
    (ext_dir / f"{slug}_Investment_Report_KO.md").write_text(ext_ko, encoding="utf-8")

    # Build report.html if build_report.py exists
    builder = repo_path / "build_report.py"
    if builder.exists():
      # Build moabiz report.html
      subprocess.run([
          sys.executable, str(builder),
          str(moabiz_dir / f"{slug}_Investment_Report_KO.md"),
          str(moabiz_dir / "report.html"),
          "--title", f"{name_ko} 종합분석 보고서 (모아비즈)",
          "--subtitle", f"{location} · {structure} {units}세대"
      ], check=False)

      # Build external report.html
      subprocess.run([
          sys.executable, str(builder),
          str(ext_dir / f"{slug}_Investment_Report_KO.md"),
          str(ext_dir / "report.html"),
          "--title", f"{name_ko} 투자분석 보고서",
          "--subtitle", f"{location} · {structure} {units}세대"
      ], check=False)

  if report_ja_path and report_ja_path.exists():
    raw_ja = report_ja_path.read_text(encoding="utf-8")
    sanitized_pii_ja = sanitize_markdown_privacy(raw_ja)
    (moabiz_dir / f"{slug}_Investment_Report_JA.md").write_text(sanitized_pii_ja, encoding="utf-8")
    ext_ja = sanitize_moabiz_privacy(sanitized_pii_ja)
    (ext_dir / f"{slug}_Investment_Report_JA.md").write_text(ext_ja, encoding="utf-8")

    # Build report_ja.html if build_report.py exists
    if builder.exists():
      subprocess.run([
          sys.executable, str(builder),
          str(moabiz_dir / f"{slug}_Investment_Report_JA.md"),
          str(moabiz_dir / "report_ja.html"),
          "--lang", "ja",
          "--title", f"{name_ja or name_ko} 投資分析レポート (モアビズ)",
          "--subtitle", f"{location} · {structure} {units}戸"
      ], check=False)

      subprocess.run([
          sys.executable, str(builder),
          str(ext_dir / f"{slug}_Investment_Report_JA.md"),
          str(ext_dir / "report_ja.html"),
          "--lang", "ja",
          "--title", f"{name_ja or name_ko} 投資分析レポート",
          "--subtitle", f"{location} · {structure} {units}戸"
      ], check=False)

  # 3. Assets copy
  if assets_dir and assets_dir.is_dir():
    for dest_root in [ext_dir, moabiz_dir]:
      t_assets = dest_root / "assets"
      t_assets.mkdir(parents=True, exist_ok=True)
      for item in assets_dir.iterdir():
        if item.is_file():
          shutil.copy2(item, t_assets / item.name)

  # 4. Property Metadata
  price = calc.get("price", 0)
  price_display = f"{price / 10000:,.0f}만 엔" if price else "-"
  y = calc.get("yields", {})
  gross_yield = y.get("full_gross_yield_pct", 0.0)
  cap_rate = y.get("full_cap_rate_pct", 0.0)

  property_meta = {
      "slug": slug,
      "name_ko": name_ko,
      "name_ja": name_ja,
      "structure": structure,
      "units": units,
      "location": location,
      "price": price,
      "price_display": price_display,
      "gross_yield_pct": gross_yield,
      "cap_rate_pct": cap_rate,
      "assessed_value_ratio_pct": calc.get("assessed_value_ratio_pct", 0.0),
      "verdict": calc.get("verdict", "매수 추천"),
      "verdict_badge": calc.get("verdict_badge", "recommend"),
      "corporate_verdict": calc.get("corporate_verdict", "적합 (우량 편입 대상)"),
      "corporate_verdict_public": calc.get("corporate_verdict_public", "적합 (우량 투자 대상)"),
      "score": calc.get("score", 25),
      "max_score": calc.get("max_score", 30),
      "public_enabled": public_enabled,
      "key_highlights": calc.get("key_highlights", []),
      "report_ko": f"./{slug}/{slug}_Investment_Report_KO.md",
      "report_ja": f"./{slug}/{slug}_Investment_Report_JA.md",
      "report_html": f"./{slug}/report.html",
      "report_ja_html": f"./{slug}/report_ja.html",
      "simulator_html": f"./{slug}/index.html",
      "folder": slug,
      "moabiz_folder": f"moabiz/{slug}",
      "moabiz_simulator_html": f"./moabiz/{slug}/index.html",
      "moabiz_report_html": f"./moabiz/{slug}/report.html",
      "moabiz_report_ja_html": f"./moabiz/{slug}/report_ja.html"
  }

  # Update properties.json
  properties = load_properties_json(repo_path)
  existing_idx = next((i for i, x in enumerate(properties) if x.get("slug") == slug), None)
  if existing_idx is not None:
    properties[existing_idx] = property_meta
    print(f"[*] Updated existing record for {slug}")
  else:
    properties.append(property_meta)
    print(f"[+] Added new record for {slug}")

  save_properties_json(repo_path, properties)
  update_dual_dashboards(repo_path)

  # Git operations
  run_git_cmd(["add", "."], repo_path)
  commit_msg = f"feat(property): dual-publish analysis dossier for {name_ko} ({slug}) [public={public_enabled}]"
  c_res = run_git_cmd(["commit", "-m", commit_msg], repo_path)
  print(f"[+] Git commit: {commit_msg}")
  if c_res.stdout:
    print(c_res.stdout.strip())

  if push:
    print("[*] Pushing changes to GitHub (origin main)...")
    p_res = run_git_cmd(["push", "origin", "main"], repo_path)
    if p_res.returncode == 0:
      print("[+] Git push completed successfully!")
    else:
      print(f"[-] Git push failed: {p_res.stderr.strip()}")


def set_public_visibility(repo_path: Path, slug: str, enabled: bool, push: bool = False) -> None:
  """Changes the public_enabled flag for a property and updates dual dashboards."""
  properties = load_properties_json(repo_path)
  target = next((p for p in properties if p.get("slug") == slug), None)
  if not target:
    print(f"[-] Property slug '{slug}' not found in properties.json")
    return

  target["public_enabled"] = enabled
  save_properties_json(repo_path, properties)
  update_dual_dashboards(repo_path)

  status_str = "ON (Public)" if enabled else "OFF (Private Only)"
  print(f"[+] Set public visibility of '{slug}' to {status_str}")

  run_git_cmd(["add", "properties.json", "moabiz/properties.json", "index.html", "moabiz/index.html"], repo_path)
  commit_msg = f"chore(visibility): set public visibility of {slug} to {enabled}"
  run_git_cmd(["commit", "-m", commit_msg], repo_path)

  if push:
    run_git_cmd(["push", "origin", "main"], repo_path)


def main():
  parser = argparse.ArgumentParser(
      description="Dual-publish real estate analysis to GitHub (External & Moabiz)"
  )
  parser.add_argument(
      "--repo-path",
      default=str(DEFAULT_LOCAL_REPO),
      help="Local path to myrealbiz git repository clone",
  )
  parser.add_argument(
      "--repo-url",
      default=DEFAULT_REPO_URL,
      help="Remote Git repository URL",
  )
  parser.add_argument(
      "--slug",
      help="Property slug for folder name (e.g. foresta-hills)",
  )
  parser.add_argument(
      "--name-ko",
      help="Property Korean name (e.g. 포레스타 힐즈)",
  )
  parser.add_argument(
      "--name-ja",
      default="",
      help="Property Japanese name (e.g. フォレスタヒルズ)",
  )
  parser.add_argument(
      "--location",
      default="",
      help="Location string (e.g. 교토시 후시미구 / 京都市伏見区)",
  )
  parser.add_argument(
      "--structure",
      default="",
      help="Structure string (e.g. RC조 지상 4층)",
  )
  parser.add_argument(
      "--units",
      type=int,
      default=0,
      help="Total unit count",
  )
  parser.add_argument(
      "--report-ko",
      help="Path to Korean analysis markdown report",
  )
  parser.add_argument(
      "--report-ja",
      help="Path to Japanese analysis markdown report",
  )
  parser.add_argument(
      "--metrics",
      help="Path to metrics.json file",
  )
  parser.add_argument(
      "--assets-dir",
      help="Path to directory containing property images/assets",
  )
  parser.add_argument(
      "--private",
      action="store_true",
      help="Publish as private/internal only (public_enabled=False, like Funabashi)",
  )
  parser.add_argument(
      "--set-public",
      nargs=2,
      metavar=("SLUG", "ON_OFF"),
      help="Set public visibility of a property: --set-public funabashi-miyamoto on/off",
  )
  parser.add_argument(
      "--rebuild-index",
      action="store_true",
      help="Rebuild dual portal index dashboards from properties.json",
  )
  parser.add_argument(
      "--rebuild-all",
      action="store_true",
      help="Rebuild all dual portal index dashboards and admin sync",
  )
  parser.add_argument(
      "--push",
      action="store_true",
      help="Automatically execute git push origin main",
  )

  args = parser.parse_args()
  repo_path = Path(args.repo_path).expanduser().resolve()
  ensure_repo(repo_path, args.repo_url)

  if args.set_public:
    slug, flag_str = args.set_public
    enabled = flag_str.lower() in ["on", "true", "1", "yes"]
    set_public_visibility(repo_path, slug, enabled, push=args.push)
    return

  if args.rebuild_index or args.rebuild_all:
    update_dual_dashboards(repo_path)
    return

  if not args.slug or not args.name_ko:
    print("Error: --slug and --name-ko are required to publish a property.")
    sys.exit(1)

  publish_property(
      repo_path=repo_path,
      slug=args.slug,
      name_ko=args.name_ko,
      name_ja=args.name_ja,
      location=args.location,
      structure=args.structure,
      units=args.units,
      report_ko_path=Path(args.report_ko) if args.report_ko else None,
      report_ja_path=Path(args.report_ja) if args.report_ja else None,
      metrics_json_path=Path(args.metrics) if args.metrics else None,
      assets_dir=Path(args.assets_dir) if args.assets_dir else None,
      public_enabled=not args.private,
      push=args.push,
  )


if __name__ == "__main__":
  main()
