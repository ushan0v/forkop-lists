#!/usr/bin/env python3
"""Build the rule sets of lists.toml: fetch the sources, merge them, compile with sing-box."""

import argparse
import hashlib
import ipaddress
import json
import os
import re
import shutil
import subprocess
import sys
import time
import tomllib
import urllib.error
import urllib.request
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.abspath(__file__))
RULE_SET_VERSION = 2
USER_AGENT = "forkop-lists (+https://github.com/ushan0v/forkop-lists)"
# A list that shrinks below this share of its last published size is not published.
MIN_SHARE_OF_PREVIOUS = 0.5

SOURCES = {
    "itdog": "https://raw.githubusercontent.com/itdoginfo/allow-domains/main/{}",
    "v2fly": "https://raw.githubusercontent.com/v2fly/domain-list-community/master/data/{}",
    "roscomvpn": "https://raw.githubusercontent.com/hydraponique/roscomvpn-geosite/master/data/{}",
    "grimbird": "https://raw.githubusercontent.com/GrimbirdUsers/ru-routing-dat/main/data-geosite/{}",
    "loyalsoldier": "https://raw.githubusercontent.com/Loyalsoldier/geoip/release/text/{}.txt",
    "asn": "https://stat.ripe.net/data/announced-prefixes/data.json?resource=AS{}",
}
# Sources in the format of v2fly/domain-list-community, include lines and attributes.
V2FLY_KINDS = {"v2fly", "roscomvpn", "grimbird"}
V2FLY_TYPES = {"domain": "suffix", "full": "full", "keyword": "keyword", "regexp": "regex"}
DOMAIN_RE = re.compile(r"[a-z0-9_-]+(\.[a-z0-9_-]+)*")


class SourceError(Exception):
    pass


class Fetcher:
    def __init__(self):
        self.cache = {}

    def get(self, url):
        if url in self.cache:
            return self.cache[url]
        error = None
        for attempt in range(3):
            try:
                request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
                with urllib.request.urlopen(request, timeout=60) as response:
                    text = response.read().decode("utf-8", errors="replace")
                self.cache[url] = text
                return text
            except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
                error = exc
                time.sleep(2 * (attempt + 1))
        raise SourceError(f"{url}: {error}")


def source_url(reference):
    kind, _, name = reference.partition(":")
    if kind in SOURCES and name:
        return SOURCES[kind].format(name)
    if reference.startswith(("https://", "http://")):
        return reference
    raise ValueError(f"unknown source {reference!r}")


def normalize_domain(value):
    value = value.strip().lower().rstrip(".")
    while value.startswith(("*", ".")):
        value = value[1:]
    if not value or any(ch in value for ch in "/: \t"):
        return None
    if not value.isascii():
        try:
            value = value.encode("idna").decode("ascii")
        except UnicodeError:
            return None
    if not DOMAIN_RE.fullmatch(value):
        return None
    try:
        ipaddress.ip_address(value)
        return None
    except ValueError:
        return value


def plain_domains(text):
    """Domains of a plain list: one a line, hosts lines, wildcards and comments allowed."""
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or line.startswith("!"):
            continue
        parts = line.split()
        if len(parts) > 1 and parts[0] in ("0.0.0.0", "127.0.0.1", "::", "::1"):
            line = parts[1]
        else:
            line = parts[0]
        yield ("suffix", line, frozenset())


def keyword_entries(value):
    """A v2fly keyword matches inside any label ("intel." takes mintel.com). One that spells a domain
    becomes that domain, one ending in a dot a whole label: after a dot or at the name's start."""
    if value.endswith(".") and DOMAIN_RE.fullmatch(value[:-1]):
        return [("keyword", "." + value), ("regex", "^" + re.escape(value))]
    if "." in value and DOMAIN_RE.fullmatch(value):
        return [("suffix", value)]
    return [("keyword", value)]


def v2fly_entries(fetcher, kind, name, trail=()):
    """Entries of a v2fly data file, its includes resolved, as (type, value, attributes)."""
    if name in trail:
        raise SourceError(f"{kind}:{name} includes itself through {' > '.join(trail)}")
    text = fetcher.get(SOURCES[kind].format(name))
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        head, *tail = line.split()
        attributes = frozenset(part[1:] for part in tail if part.startswith("@"))
        if head.startswith("include:"):
            # "@attr" keeps the included entries that carry it, "@-attr" those that do not.
            wanted = {a for a in attributes if not a.startswith("-")}
            unwanted = {a[1:] for a in attributes if a.startswith("-")}
            for entry in v2fly_entries(fetcher, kind, head[len("include:"):], trail + (name,)):
                if wanted <= entry[2] and not (unwanted & entry[2]):
                    yield entry
            continue
        prefix, separator, value = head.partition(":")
        if not separator:
            prefix, value = "domain", head
        if prefix not in V2FLY_TYPES:
            raise SourceError(f"{kind}:{name}: unknown entry {head!r}")
        if prefix == "keyword":
            for entry_type, entry_value in keyword_entries(value):
                yield (entry_type, entry_value, attributes)
            continue
        yield (V2FLY_TYPES[prefix], value, attributes)


def prefixes_of(text):
    for raw in text.splitlines():
        token = raw.split("#", 1)[0].strip()
        if not token:
            continue
        try:
            yield ipaddress.ip_network(token.split()[0], strict=False)
        except ValueError:
            continue


def asn_prefixes(text):
    data = json.loads(text)
    for item in data.get("data", {}).get("prefixes", []):
        yield ipaddress.ip_network(item["prefix"], strict=False)


def covered(name, suffixes):
    labels = name.split(".")
    return any(".".join(labels[i:]) in suffixes for i in range(len(labels)))


def minimal_suffixes(suffixes):
    result = set()
    for suffix in sorted(suffixes, key=lambda s: (s.count("."), s)):
        if not covered(suffix, result):
            result.add(suffix)
    return result


class Domains:
    def __init__(self):
        self.suffix, self.full, self.keyword, self.regex = set(), set(), set(), set()

    def add(self, kind, value):
        if kind in ("suffix", "full"):
            value = normalize_domain(value)
            if value is None:
                return False
        getattr(self, kind).add(value)
        return True

    def update(self, other):
        for kind in ("suffix", "full", "keyword", "regex"):
            getattr(self, kind).update(getattr(other, kind))

    def holds(self, name):
        return name in self.full or covered(name, self.suffix)

    def subtract(self, other, wider=False):
        """Drop every name the other list already matches by name; with wider, also every
        suffix of this list that covers one of the other list's names."""
        self.suffix = {s for s in self.suffix if not covered(s, other.suffix) and s not in other.full}
        self.full = {f for f in self.full if not covered(f, other.suffix) and f not in other.full}
        self.keyword -= other.keyword
        self.regex -= other.regex
        if wider:
            parents = set()
            for name in other.suffix | other.full:
                labels = name.split(".")
                parents.update(".".join(labels[i:]) for i in range(1, len(labels)))
            wide = self.suffix & parents
            self.suffix -= wide
            return sorted(wide)
        return []

    def minimize(self, allowed_tlds):
        """Drop whole top-level domains not allowed and every name a wider suffix covers."""
        tlds = {s for s in self.suffix | self.full if "." not in s and s not in allowed_tlds}
        self.suffix = minimal_suffixes(self.suffix - tlds)
        self.full = {f for f in self.full - tlds if not covered(f, self.suffix)}
        return sorted(tlds)

    def count(self):
        return len(self.suffix) + len(self.full) + len(self.keyword) + len(self.regex)


class Built:
    def __init__(self, recipe):
        self.recipe = recipe
        self.domains = Domains()
        self.prefixes = set()
        self.scoped = []
        self.sources = []
        self.failures = []


def collect_domains(fetcher, built, references, skip_attributes):
    for reference in references:
        kind, _, name = reference.partition(":")
        if kind == "file":
            path = os.path.join(ROOT, name)
            built.sources.append(name)
            with open(path, encoding="utf-8") as handle:
                entries = list(plain_domains(handle.read()))
        else:
            built.sources.append(source_url(reference))
            if kind in V2FLY_KINDS:
                entries = list(v2fly_entries(fetcher, kind, name))
            else:
                entries = list(plain_domains(fetcher.get(source_url(reference))))
        added = 0
        for entry_type, value, attributes in entries:
            if attributes & skip_attributes:
                continue
            added += built.domains.add(entry_type, value)
        if added == 0:
            raise SourceError(f"{reference} gave no domain")


def collect_prefixes(fetcher, references, sources):
    prefixes = set()
    for reference in references:
        try:
            prefixes.add(ipaddress.ip_network(reference, strict=False))
            continue
        except ValueError:
            pass
        kind = reference.partition(":")[0]
        if kind == "file":
            name = reference.partition(":")[2]
            sources.append(name)
            with open(os.path.join(ROOT, name), encoding="utf-8") as handle:
                found = set(prefixes_of(handle.read()))
        else:
            url = source_url(reference)
            sources.append(url)
            text = fetcher.get(url)
            found = set(asn_prefixes(text) if kind == "asn" else prefixes_of(text))
        if not found:
            raise SourceError(f"{reference} gave no prefix")
        prefixes |= found
    return prefixes


def collapsed(prefixes):
    v4 = list(ipaddress.collapse_addresses(p for p in prefixes if p.version == 4))
    v6 = list(ipaddress.collapse_addresses(p for p in prefixes if p.version == 6))
    return v4, v6


def build_list(fetcher, recipe, built_lists):
    built = Built(recipe)
    skip = frozenset(recipe.get("skip_attributes", ["ads"]))
    for value in recipe.get("add", []):
        if not built.domains.add("suffix", value):
            raise SystemExit(f"lists.toml: {recipe['name']} adds an invalid domain {value!r}")
    kept = Built(recipe)
    try:
        collect_domains(fetcher, built, recipe.get("domains", []), skip)
        built.prefixes = collect_prefixes(fetcher, recipe.get("ips", []), built.sources)
        for scope in recipe.get("scoped", []):
            built.scoped.append((scope, collect_prefixes(fetcher, scope["ips"], built.sources)))
        collect_domains(fetcher, kept, recipe.get("keep", []), skip)
        built.sources += kept.sources
    except SourceError as exc:
        built.failures.append(str(exc))
        return built
    # Exclusions apply to the list's own sources; included lists come in whole.
    own = Domains()
    own.update(built.domains)
    for other in recipe.get("exclude_lists", []):
        excluded = built_lists[other]
        if excluded.failures:
            built.failures.append(f"excluded list {other} failed")
            return built
        wide = built.domains.subtract(excluded.domains, wider=recipe.get("exclude_wider", False))
        if wide:
            print(f"{recipe['name']}: left out zones that hold names of {other}: {', '.join(wide)}", flush=True)
    restored = [name for name in kept.domains.suffix | kept.domains.full
                if own.holds(name) and not built.domains.holds(name)]
    built.domains.suffix.update(restored)
    if restored:
        print(f"{recipe['name']}: kept {len(restored)} names its exclusions took out", flush=True)
    for other in recipe.get("include_lists", []):
        included = built_lists[other]
        if included.failures:
            built.failures.append(f"included list {other} failed")
            return built
        built.domains.update(included.domains)
        built.prefixes |= included.prefixes
        built.scoped += included.scoped
    drop = {normalize_domain(name) for name in recipe.get("drop", [])}
    built.domains.suffix -= drop
    built.domains.full -= drop
    dropped = built.domains.minimize(set(recipe.get("allow_tlds", [])))
    if dropped:
        print(f"{recipe['name']}: left out whole top-level domains {', '.join(dropped)}", flush=True)
    return built


def rule_set_of(built):
    rules = []
    main = {}
    d = built.domains
    for key, values in (("domain", d.full), ("domain_suffix", d.suffix),
                        ("domain_keyword", d.keyword), ("domain_regex", d.regex)):
        if values:
            main[key] = sorted(values)
    v4, v6 = collapsed(built.prefixes)
    if v4 or v6:
        main["ip_cidr"] = [str(p) for p in v4 + v6]
    if main:
        rules.append(main)
    for scope, prefixes in built.scoped:
        v4, v6 = collapsed(prefixes)
        rule = {"network": [scope["network"]], "port_range": [scope["port_range"]],
                "ip_cidr": [str(p) for p in v4 + v6]}
        rules.append(rule)
    return {"version": RULE_SET_VERSION, "rules": rules}


def counts_of(built):
    v4, v6 = collapsed(built.prefixes)
    for _, prefixes in built.scoped:
        sv4, sv6 = collapsed(prefixes)
        v4 += sv4
        v6 += sv6
    return {"domains": built.domains.count(), "ipv4": len(v4), "ipv6": len(v6)}


def sha256_of(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def compile_rule_set(sing_box, source_path, binary_path):
    result = subprocess.run([sing_box, "rule-set", "compile", source_path, "-o", binary_path],
                            capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"compile {source_path}: {result.stderr.strip() or result.stdout.strip()}")


def matches(sing_box, binary_path, target):
    result = subprocess.run([sing_box, "rule-set", "match", "-f", "binary", binary_path, target],
                            capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"match {target} in {binary_path}: {result.stderr.strip()}")
    return "match rules." in result.stdout + result.stderr


def check_expectations(sing_box, recipe, binary_path):
    problems = []
    for target in recipe.get("expect", []):
        if not matches(sing_box, binary_path, target):
            problems.append(f"{target} is missing")
    for target in recipe.get("expect_not", []):
        if matches(sing_box, binary_path, target):
            problems.append(f"{target} matches but must not")
    return problems


def ordered(recipes):
    by_name = {r["name"]: r for r in recipes}
    done, order = set(), []

    def visit(name, trail):
        if name in done:
            return
        if name in trail:
            raise SystemExit(f"lists.toml: {name} depends on itself")
        for other in by_name[name].get("include_lists", []) + by_name[name].get("exclude_lists", []):
            if other not in by_name:
                raise SystemExit(f"lists.toml: {name} names unknown list {other}")
            visit(other, trail | {name})
        done.add(name)
        order.append(by_name[name])

    for recipe in recipes:
        visit(recipe["name"], set())
    return order


def load_previous(directory):
    if not directory:
        return {}
    path = os.path.join(directory, "manifest.json")
    if not os.path.isfile(path):
        return {}
    with open(path, encoding="utf-8") as handle:
        return json.load(handle).get("lists", {})


def keep_previous(previous_dir, name, out_dir):
    if not previous_dir:
        return False
    for extension in ("srs", "json"):
        source = os.path.join(previous_dir, f"{name}.{extension}")
        if not os.path.isfile(source):
            return False
    for extension in ("srs", "json"):
        shutil.copyfile(os.path.join(previous_dir, f"{name}.{extension}"), os.path.join(out_dir, f"{name}.{extension}"))
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=os.path.join(ROOT, "out"), help="directory for the built lists")
    parser.add_argument("--previous", help="directory of the last published lists, for the guards")
    parser.add_argument("--sing-box", default="sing-box", help="sing-box binary that compiles the lists")
    parser.add_argument("--only", action="append", help="build only these lists and what they need")
    parser.add_argument("--summary", help="append a Markdown report to this file")
    parser.add_argument("--notes", help="write the Markdown report to this file, for the release")
    parser.add_argument("--github-output", help="write changed=true|false to this file")
    args = parser.parse_args()

    with open(os.path.join(ROOT, "lists.toml"), "rb") as handle:
        recipes = tomllib.load(handle)["list"]
    order = ordered(recipes)
    if args.only:
        needed = set()

        def need(name):
            needed.add(name)
            recipe = next(r for r in recipes if r["name"] == name)
            for other in recipe.get("include_lists", []) + recipe.get("exclude_lists", []):
                need(other)

        for name in args.only:
            need(name)
        order = [r for r in order if r["name"] in needed]

    os.makedirs(args.out, exist_ok=True)
    previous = load_previous(args.previous)
    fetcher = Fetcher()
    built_lists, manifest, report, errors = {}, {}, [], []
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    for recipe in order:
        name = recipe["name"]
        built = build_list(fetcher, recipe, built_lists)
        built_lists[name] = built
        if not recipe.get("publish", True):
            # A helper is not published; the lists built from it keep their last version if it fails.
            if built.failures:
                print(f"{name}: failed" + "".join(f"\n  - {n}" for n in built.failures), flush=True)
            continue
        entry = {"title": recipe["title"], "file": f"{name}.srs", "sources": built.sources}
        before = previous.get(name)
        status, notes = "ok", list(built.failures)

        if not built.failures:
            counts = counts_of(built)
            source_path = os.path.join(args.out, f"{name}.json")
            binary_path = os.path.join(args.out, f"{name}.srs")
            with open(source_path, "w", encoding="utf-8", newline="\n") as handle:
                json.dump(rule_set_of(built), handle, indent=2, ensure_ascii=False)
                handle.write("\n")
            compile_rule_set(args.sing_box, source_path, binary_path)
            notes += check_expectations(args.sing_box, recipe, binary_path)
            size = counts["domains"] + counts["ipv4"] + counts["ipv6"]
            if before:
                before_size = before["domains"] + before["ipv4"] + before["ipv6"]
                if size < before_size * MIN_SHARE_OF_PREVIOUS:
                    notes.append(f"shrank from {before_size} to {size} entries")
            if not notes:
                entry.update(counts)
                entry["sha256"] = sha256_of(binary_path)
                changed = not before or before.get("sha256") != entry["sha256"]
                entry["updated"] = now if changed else before.get("updated", now)

        if notes:
            if before and keep_previous(args.previous, name, args.out):
                status = "kept"
                entry.update({k: before[k] for k in ("domains", "ipv4", "ipv6", "sha256", "updated")})
            else:
                status = "failed"
                errors.append(name)
        entry["status"] = status
        manifest[name] = entry
        report.append((name, entry, notes, before))
        print(f"{name}: {status} {entry.get('domains', '-')} domains, {entry.get('ipv4', '-')} IPv4, "
              f"{entry.get('ipv6', '-')} IPv6" + "".join(f"\n  - {n}" for n in notes), flush=True)

    with open(os.path.join(args.out, "manifest.json"), "w", encoding="utf-8", newline="\n") as handle:
        json.dump({"generated": now, "lists": manifest}, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    changed = any(e["status"] == "ok" and (not previous.get(n) or previous[n].get("sha256") != e.get("sha256"))
                  for n, e in manifest.items()) or set(previous) != set(manifest)
    if args.github_output:
        kept = ",".join(n for n, e in manifest.items() if e["status"] == "kept")
        with open(args.github_output, "a", encoding="utf-8") as handle:
            handle.write(f"changed={'true' if changed and not errors else 'false'}\n")
            handle.write(f"kept={kept}\n")
    if args.summary:
        write_summary(args.summary, report, "a")
    if args.notes:
        write_summary(args.notes, report, "w")
    if errors:
        print("failed: " + ", ".join(errors), file=sys.stderr)
        return 1
    return 0


def write_summary(path, report, mode):
    lines = ["| List | Status | Domains | IPv4 | IPv6 | Change |", "|---|---|---:|---:|---:|---|"]
    for name, entry, notes, before in report:
        change = ""
        if before and entry.get("domains") is not None:
            delta = entry["domains"] - before["domains"]
            change = f"{delta:+d} domains" if delta else ""
        lines.append(f"| {name} | {entry['status']} | {entry.get('domains', '')} | {entry.get('ipv4', '')} | "
                     f"{entry.get('ipv6', '')} | {change} |")
    problems = [(name, notes) for name, _, notes, _ in report if notes]
    if problems:
        lines.append("")
        for name, notes in problems:
            for note in notes:
                lines.append(f"- **{name}**: {note}")
    with open(path, mode, encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    sys.exit(main())
