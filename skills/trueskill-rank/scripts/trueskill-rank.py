#!/usr/bin/env python3
import argparse
import concurrent.futures
import json
import math
import os
import random
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from collections import defaultdict

try:
    import trueskill
except ImportError:
    trueskill = None


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def read_text(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def normalize_text(value):
    if value is None:
        return "[no text]"
    text = str(value)
    if not text.strip():
        return "[no text]"
    return text


def cap_text(text, text_cap):
    if text_cap is None or text_cap <= 0:
        return text
    if len(text) <= text_cap:
        return text
    return text[:text_cap]


def load_items(input_path):
    data = json.loads(read_text(input_path))
    items = data.get("items") if isinstance(data, dict) else None
    if not isinstance(items, list) or not items:
        raise ValueError("Input JSON must contain non-empty 'items' array.")

    normalized = []
    seen = set()
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(f"Item at index {i} must be an object.")
        if "id" not in item:
            raise ValueError(f"Item at index {i} is missing 'id'.")
        item_id = str(item["id"])
        if item_id in seen:
            raise ValueError(f"Duplicate item id: {item_id}")
        seen.add(item_id)
        metadata = item.get("metadata", {})
        if metadata is None:
            metadata = {}
        normalized.append(
            {
                "id": item_id,
                "text": normalize_text(item.get("text")),
                "metadata": metadata,
            }
        )

    return normalized


def build_items_index(items):
    index = {}
    for item in items:
        index[item["id"]] = {
            "text": item["text"],
            "metadata": item.get("metadata", {}),
        }
    return index


def rubric_name_from_path(path):
    return os.path.splitext(os.path.basename(path))[0]


def weighted_choice(rng, candidates, weights):
    return rng.choices(candidates, weights=weights, k=1)[0]


def generate_batch_subsets(item_ids, overlap, subset_size, seed):
    rng = random.Random(seed)
    n_items = len(item_ids)
    effective_subset_size = min(subset_size, n_items)
    n_subsets = max(1, math.ceil((n_items * overlap) / effective_subset_size))

    total_slots = n_subsets * effective_subset_size
    base = total_slots // n_items
    remainder = total_slots % n_items

    targets = {item_id: base for item_id in item_ids}
    extra_items = rng.sample(item_ids, remainder) if remainder > 0 else []
    for item_id in extra_items:
        targets[item_id] += 1

    # Keep retrying with weighted sampling while honoring exact target counts.
    for _ in range(300):
        remaining = dict(targets)
        appearances = defaultdict(int)
        subsets = []
        ok = True

        for _subset_idx in range(n_subsets):
            subset = []
            for _slot in range(effective_subset_size):
                candidates = [
                    item_id
                    for item_id in item_ids
                    if item_id not in subset and remaining[item_id] > 0
                ]
                if not candidates:
                    ok = False
                    break

                weights = []
                for item_id in candidates:
                    deficit = remaining[item_id]
                    inv_freq = 1.0 / (1.0 + appearances[item_id])
                    weights.append((deficit * deficit) + inv_freq)

                chosen = weighted_choice(rng, candidates, weights)
                subset.append(chosen)
                remaining[chosen] -= 1
                appearances[chosen] += 1

            if not ok:
                break
            subsets.append(subset)

        if ok and all(v == 0 for v in remaining.values()):
            low = overlap - 1
            high = overlap + 1
            if all(low <= appearances[item_id] <= high for item_id in item_ids):
                return subsets, dict(appearances), effective_subset_size

    # Fallback strategy if exact target-constrained generation is hard.
    appearances = defaultdict(int)
    subsets = []
    for _ in range(n_subsets):
        subset = []
        for _ in range(effective_subset_size):
            candidates = [item_id for item_id in item_ids if item_id not in subset]
            weights = [1.0 / (1.0 + appearances[item_id]) for item_id in candidates]
            chosen = weighted_choice(rng, candidates, weights)
            subset.append(chosen)
            appearances[chosen] += 1
        subsets.append(subset)

    return subsets, dict(appearances), effective_subset_size


def round_robin_rounds(item_ids):
    players = list(item_ids)
    if len(players) < 2:
        return []

    bye = None
    if len(players) % 2 == 1:
        players.append(bye)

    rounds = []
    n = len(players)
    arr = list(players)
    for _ in range(n - 1):
        pairs = []
        for i in range(n // 2):
            a = arr[i]
            b = arr[n - 1 - i]
            if a is not bye and b is not bye:
                pairs.append((a, b))
        rounds.append(pairs)
        arr = [arr[0]] + [arr[-1]] + arr[1:-1]

    return rounds


def generate_pairwise_matchups(item_ids, overlap, target_matchups, seed):
    rng = random.Random(seed)
    appearances = defaultdict(int)
    pair_counts = defaultdict(int)
    matchups = []

    if len(item_ids) < 2:
        return matchups, dict(appearances), dict(pair_counts)

    rounds = round_robin_rounds(item_ids)
    min_coverage = overlap * 4

    # Phase 1: round-robin passes with per-pair cap of 2.
    while min(appearances[item_id] for item_id in item_ids) < min_coverage:
        progress = False
        for round_pairs in rounds:
            shuffled_pairs = list(round_pairs)
            rng.shuffle(shuffled_pairs)
            for a, b in shuffled_pairs:
                pair_key = tuple(sorted((a, b)))
                if pair_counts[pair_key] >= 2:
                    continue
                if appearances[a] >= min_coverage and appearances[b] >= min_coverage:
                    continue
                matchups.append((a, b))
                pair_counts[pair_key] += 1
                appearances[a] += 1
                appearances[b] += 1
                progress = True

                if min(appearances[item_id] for item_id in item_ids) >= min_coverage:
                    break
            if min(appearances[item_id] for item_id in item_ids) >= min_coverage:
                break
        if not progress:
            break

    # Phase 2: weighted random fill to target, per-pair cap of 3.
    all_pairs = []
    for i in range(len(item_ids)):
        for j in range(i + 1, len(item_ids)):
            all_pairs.append((item_ids[i], item_ids[j]))

    while len(matchups) < target_matchups:
        candidates = []
        weights = []
        for a, b in all_pairs:
            pair_key = tuple(sorted((a, b)))
            if pair_counts[pair_key] >= 3:
                continue
            candidates.append((a, b))
            weights.append((1.0 / (1.0 + appearances[a])) * (1.0 / (1.0 + appearances[b])))

        if not candidates:
            break

        a, b = weighted_choice(rng, candidates, weights)
        pair_key = tuple(sorted((a, b)))
        matchups.append((a, b))
        pair_counts[pair_key] += 1
        appearances[a] += 1
        appearances[b] += 1

    return matchups, dict(appearances), dict(pair_counts)


def build_batch_prompt(subset, items_index, rubric_text, text_cap):
    subset_size = len(subset)
    parts = [
        (
            f"You are ranking items by quality. You will receive {subset_size} items. "
            f"Rank them from BEST (rank 1) to WORST (rank {subset_size})."
        ),
        "",
        "SCORING CRITERIA:",
        rubric_text,
        "",
        "IMPORTANT: Your response must be valid JSON and nothing else. No explanations, no commentary.",
        "Every item_id must appear exactly once. No ties allowed.",
        "",
        "Format your response as JSON:",
        '{"ranking": [{"item_id": "...", "rank": 1}, {"item_id": "...", "rank": 2}, ...]}',
        "",
        "ITEMS TO RANK:",
        "",
    ]

    for item_id in subset:
        text = cap_text(items_index[item_id]["text"], text_cap)
        parts.append(f"--- ITEM {item_id} ---")
        parts.append(text)
        parts.append("")

    return "\n".join(parts).rstrip() + "\n"


def build_pairwise_prompt(batch, rubric_text, text_cap):
    parts = [
        "You are evaluating items for quality. For each pair, pick the winner -- the item with higher quality.",
        "",
        "SCORING CRITERIA:",
        rubric_text,
        "",
        'For each matchup, respond with ONLY the winner: "A" or "B". If truly equal, pick whichever has more original thinking.',
        "",
        "IMPORTANT: Your response must be valid JSON and nothing else. No explanations, no commentary.",
        "",
        "Format your response as JSON:",
        '{"results": [{"match_id": N, "winner": "A"}, ...]}',
        "",
        "MATCHUPS:",
        "",
    ]

    for matchup in batch:
        parts.append(f"--- MATCHUP {matchup['match_id']} ---")
        parts.append(f"ITEM A ({matchup['item_a']}):")
        parts.append(cap_text(matchup["text_a"], text_cap))
        parts.append("")
        parts.append(f"ITEM B ({matchup['item_b']}):")
        parts.append(cap_text(matchup["text_b"], text_cap))
        parts.append("")

    return "\n".join(parts).rstrip() + "\n"


def prepare_batch(items, overlap, subset_size, rubric_text, rubric_name, output_dir, seed, text_cap):
    item_ids = [item["id"] for item in items]
    items_index = build_items_index(items)

    subsets, appearances, effective_subset_size = generate_batch_subsets(
        item_ids=item_ids,
        overlap=overlap,
        subset_size=subset_size,
        seed=seed,
    )

    prompts_dir = os.path.join(output_dir, "prompts")
    os.makedirs(prompts_dir, exist_ok=True)

    for i, subset in enumerate(subsets, start=1):
        prompt = build_batch_prompt(subset, items_index, rubric_text, text_cap)
        prompt_path = os.path.join(prompts_dir, f"subset-{i:02d}.txt")
        with open(prompt_path, "w", encoding="utf-8") as f:
            f.write(prompt)

    manifest = {
        "subsets": subsets,
        "mode": "batch",
        "overlap": overlap,
        "rubric": rubric_name,
        "items_index": items_index,
        "subset_size": effective_subset_size,
    }

    write_json(os.path.join(output_dir, "subsets.json"), manifest)

    low = overlap - 1
    high = overlap + 1
    in_range = sum(1 for item_id in item_ids if low <= appearances.get(item_id, 0) <= high)
    eprint(
        f"Prepared batch mode: items={len(items)} subsets={len(subsets)} subset_size={effective_subset_size} "
        f"appearance_in_range={in_range}/{len(item_ids)}"
    )


def prepare_pairwise(items, overlap, subset_size, rubric_text, rubric_name, output_dir, seed, text_cap):
    item_ids = [item["id"] for item in items]
    items_index = build_items_index(items)

    target_matchups = math.ceil(len(item_ids) * overlap * 4)
    matchups, appearances, pair_counts = generate_pairwise_matchups(
        item_ids=item_ids,
        overlap=overlap,
        target_matchups=target_matchups,
        seed=seed,
    )

    batches = []
    match_id = 1
    for i in range(0, len(matchups), subset_size):
        batch_pairs = matchups[i : i + subset_size]
        batch = []
        for a, b in batch_pairs:
            batch.append(
                {
                    "match_id": match_id,
                    "item_a": a,
                    "text_a": items_index[a]["text"],
                    "item_b": b,
                    "text_b": items_index[b]["text"],
                }
            )
            match_id += 1
        batches.append(batch)

    prompts_dir = os.path.join(output_dir, "prompts")
    os.makedirs(prompts_dir, exist_ok=True)

    for i, batch in enumerate(batches, start=1):
        prompt = build_pairwise_prompt(batch, rubric_text, text_cap)
        prompt_path = os.path.join(prompts_dir, f"batch-{i:02d}.txt")
        with open(prompt_path, "w", encoding="utf-8") as f:
            f.write(prompt)

    manifest = {
        "subsets": batches,
        "mode": "pairwise",
        "overlap": overlap,
        "rubric": rubric_name,
        "items_index": items_index,
        "subset_size": subset_size,
    }

    write_json(os.path.join(output_dir, "subsets.json"), manifest)

    min_cov = overlap * 4 if item_ids else 0
    covered = sum(1 for item_id in item_ids if appearances.get(item_id, 0) >= min_cov)
    max_pair_repeats = max(pair_counts.values()) if pair_counts else 0
    eprint(
        f"Prepared pairwise mode: items={len(items)} target_matchups={target_matchups} "
        f"generated_matchups={len(matchups)} batches={len(batches)} "
        f"coverage_at_least_{min_cov}={covered}/{len(item_ids)} max_pair_repeats={max_pair_repeats}"
    )


def resolve_subset_size(mode, subset_size):
    if subset_size is None:
        return 10 if mode == "batch" else 25
    return subset_size


def cmd_prepare(args):
    try:
        items = load_items(args.input)
    except Exception as exc:
        eprint(f"ERROR: failed to load input items: {exc}")
        return 1

    subset_size = resolve_subset_size(args.mode, args.subset_size)
    if subset_size <= 0:
        eprint("ERROR: --subset-size must be > 0")
        return 1

    try:
        rubric_text = read_text(args.rubric)
    except Exception as exc:
        eprint(f"ERROR: failed to read rubric file: {exc}")
        return 1

    os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs(os.path.join(args.output_dir, "results"), exist_ok=True)

    rubric_name = rubric_name_from_path(args.rubric)

    eprint(
        f"Preparing mode={args.mode} items={len(items)} overlap={args.overlap} "
        f"subset_size={subset_size} seed={args.seed}"
    )

    if args.mode == "batch":
        prepare_batch(
            items=items,
            overlap=args.overlap,
            subset_size=subset_size,
            rubric_text=rubric_text,
            rubric_name=rubric_name,
            output_dir=args.output_dir,
            seed=args.seed,
            text_cap=args.text_cap,
        )
    else:
        prepare_pairwise(
            items=items,
            overlap=args.overlap,
            subset_size=subset_size,
            rubric_text=rubric_text,
            rubric_name=rubric_name,
            output_dir=args.output_dir,
            seed=args.seed,
            text_cap=args.text_cap,
        )

    return 0


def extract_mode_payload(obj, mode):
    if mode == "batch":
        if isinstance(obj, dict) and isinstance(obj.get("ranking"), list):
            return obj["ranking"]
        if isinstance(obj, list):
            return obj
        return None

    if isinstance(obj, dict) and isinstance(obj.get("results"), list):
        return obj["results"]
    if isinstance(obj, list):
        return obj
    return None


def layered_parse_text(text, mode):
    text = (text or "").strip()
    if not text:
        return None

    # 1) Whole-text JSON parse.
    try:
        obj = json.loads(text)
        payload = extract_mode_payload(obj, mode)
        if payload is not None:
            return payload
    except Exception:
        pass

    # 2) Embedded JSON object with ranking/results.
    object_pattern = (
        r'(\{\s*"ranking"\s*:\s*\[[\s\S]*?\]\s*\})'
        if mode == "batch"
        else r'(\{\s*"results"\s*:\s*\[[\s\S]*?\]\s*\})'
    )
    for match in re.finditer(object_pattern, text):
        snippet = match.group(1)
        try:
            obj = json.loads(snippet)
            payload = extract_mode_payload(obj, mode)
            if payload is not None:
                return payload
        except Exception:
            continue

    # 3) Bare JSON array extraction.
    for match in re.finditer(r'(\[[\s\S]*?\])', text):
        snippet = match.group(1)
        try:
            arr = json.loads(snippet)
            payload = extract_mode_payload(arr, mode)
            if payload is not None:
                return payload
        except Exception:
            continue

    return None


def parse_result_content(raw_text, mode):
    text = raw_text or ""

    # First, try parsing whole file as JSON to support agent-mux wrappers.
    try:
        top = json.loads(text)
        if isinstance(top, dict) and "response" in top:
            response = top.get("response")
            if isinstance(response, str):
                payload = layered_parse_text(response, mode)
                if payload is not None:
                    return payload
            else:
                payload = extract_mode_payload(response, mode)
                if payload is not None:
                    return payload

        payload = extract_mode_payload(top, mode)
        if payload is not None:
            return payload
    except Exception:
        pass

    # Fallback to layered text parsing of the full content.
    return layered_parse_text(text, mode)


def infer_result_index(filename):
    match = re.search(r"(\d+)", filename)
    if not match:
        return None
    try:
        return int(match.group(1)) - 1
    except ValueError:
        return None


def normalize_batch_ranking(entries, subset_ids):
    if not isinstance(entries, list):
        return None, "ranking payload is not a list"

    subset_set = set(subset_ids)
    ranked_with_scores = []
    ranked_in_order = []

    for pos, entry in enumerate(entries):
        if isinstance(entry, dict):
            item_id = entry.get("item_id")
            rank = entry.get("rank")
        elif isinstance(entry, str):
            item_id = entry
            rank = None
        else:
            continue

        if item_id is None:
            continue

        item_id = str(item_id)
        if item_id not in subset_set:
            continue

        if isinstance(rank, (int, float)):
            ranked_with_scores.append((float(rank), pos, item_id))
        else:
            ranked_in_order.append((pos, item_id))

    ordered = []
    if ranked_with_scores:
        ranked_with_scores.sort(key=lambda x: (x[0], x[1]))
        for _, _, item_id in ranked_with_scores:
            ordered.append(item_id)
    for _, item_id in ranked_in_order:
        ordered.append(item_id)

    deduped = []
    seen = set()
    for item_id in ordered:
        if item_id in seen:
            continue
        seen.add(item_id)
        deduped.append(item_id)

    missing = [item_id for item_id in subset_ids if item_id not in seen]
    missing_ratio = (len(missing) / len(subset_ids)) if subset_ids else 1.0
    if subset_ids and missing_ratio > 0.30:
        return None, f"too many missing items ({len(missing)}/{len(subset_ids)})"

    deduped.extend(missing)

    # Ensure exact one-pass coverage of subset ids.
    final_order = []
    final_seen = set()
    for item_id in deduped:
        if item_id in subset_set and item_id not in final_seen:
            final_order.append(item_id)
            final_seen.add(item_id)

    for item_id in subset_ids:
        if item_id not in final_seen:
            final_order.append(item_id)
            final_seen.add(item_id)

    return final_order, None


def normalize_pairwise_results(entries):
    if not isinstance(entries, list):
        return []

    normalized = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        match_id = entry.get("match_id")
        winner = entry.get("winner")
        try:
            match_id = int(match_id)
        except Exception:
            continue

        if not isinstance(winner, str):
            continue
        winner = winner.strip().upper()
        if winner not in {"A", "B"}:
            continue

        normalized.append((match_id, winner))

    return normalized


def build_rankings_output(ratings, appearances, wins, losses):
    rows = []
    for item_id, rating in ratings.items():
        conservative = rating.mu - 3.0 * rating.sigma
        rows.append(
            {
                "id": item_id,
                "mu": rating.mu,
                "sigma": rating.sigma,
                "conservative": conservative,
                "appearances": int(appearances.get(item_id, 0)),
                "wins": int(wins.get(item_id, 0)),
                "losses": int(losses.get(item_id, 0)),
            }
        )

    rows.sort(key=lambda r: (r["conservative"], r["mu"], r["id"]), reverse=True)
    for i, row in enumerate(rows, start=1):
        row["rank"] = i
    return rows


def cmd_aggregate(args):
    if trueskill is None:
        eprint("ERROR: trueskill package is required. Install with: pip install trueskill")
        return 1

    subsets_path = os.path.join(args.run_dir, "subsets.json")
    if not os.path.isfile(subsets_path):
        eprint(f"ERROR: missing subsets.json at {subsets_path}")
        return 1

    try:
        manifest = json.loads(read_text(subsets_path))
    except Exception as exc:
        eprint(f"ERROR: failed to read subsets.json: {exc}")
        return 1

    mode = manifest.get("mode")
    if mode not in {"batch", "pairwise"}:
        eprint(f"ERROR: invalid mode in subsets.json: {mode}")
        return 1

    subsets = manifest.get("subsets", [])
    items_index = manifest.get("items_index", {})
    all_item_ids = list(items_index.keys())

    if not all_item_ids:
        eprint("ERROR: subsets.json contains no items_index")
        return 1

    results_dir = os.path.join(args.run_dir, "results")
    result_files = []
    if os.path.isdir(results_dir):
        for name in sorted(os.listdir(results_dir)):
            path = os.path.join(results_dir, name)
            if os.path.isfile(path):
                result_files.append(path)
    else:
        eprint(f"WARNING: results directory not found at {results_dir}")

    eprint(
        f"Aggregating mode={mode} items={len(all_item_ids)} subsets={len(subsets)} result_files={len(result_files)}"
    )

    if mode == "batch":
        env = trueskill.TrueSkill(draw_probability=0.0)
    else:
        env = trueskill.TrueSkill(draw_probability=0.05)

    ratings = {item_id: env.create_rating() for item_id in all_item_ids}
    appearances = defaultdict(int)
    wins = defaultdict(int)
    losses = defaultdict(int)

    results_parsed = 0
    parse_errors = 0

    if mode == "batch":
        for file_idx, path in enumerate(result_files):
            name = os.path.basename(path)
            raw = read_text(path)
            payload = parse_result_content(raw, mode="batch")
            if payload is None:
                parse_errors += 1
                eprint(f"Parse error in {name}: unable to parse ranking payload")
                continue

            subset_idx = infer_result_index(name)
            if subset_idx is None or subset_idx < 0 or subset_idx >= len(subsets):
                subset_idx = file_idx
            if subset_idx < 0 or subset_idx >= len(subsets):
                parse_errors += 1
                eprint(f"Parse error in {name}: cannot map result file to subset")
                continue

            subset_ids = subsets[subset_idx]
            ranking, err = normalize_batch_ranking(payload, subset_ids)
            if ranking is None:
                parse_errors += 1
                eprint(f"Invalid ranking in {name}: {err}; discarded")
                continue

            # TrueSkill update for ordered finish (best -> worst).
            teams = [[ratings[item_id]] for item_id in ranking]
            new_ratings = env.rate(teams)
            for i, item_id in enumerate(ranking):
                ratings[item_id] = new_ratings[i][0]

            # Every higher-ranked item beats all lower-ranked items.
            for i, winner_id in enumerate(ranking):
                appearances[winner_id] += 1
                for loser_id in ranking[i + 1 :]:
                    wins[winner_id] += 1
                    losses[loser_id] += 1

            results_parsed += 1

    else:
        match_map = {}
        for batch in subsets:
            if not isinstance(batch, list):
                continue
            for match in batch:
                if not isinstance(match, dict):
                    continue
                match_id = match.get("match_id")
                a = match.get("item_a")
                b = match.get("item_b")
                if match_id is None or a is None or b is None:
                    continue
                try:
                    match_id = int(match_id)
                except Exception:
                    continue
                match_map[match_id] = (str(a), str(b))

        for path in result_files:
            name = os.path.basename(path)
            raw = read_text(path)
            payload = parse_result_content(raw, mode="pairwise")
            if payload is None:
                parse_errors += 1
                eprint(f"Parse error in {name}: unable to parse pairwise payload")
                continue

            results = normalize_pairwise_results(payload)
            if not results:
                parse_errors += 1
                eprint(f"Invalid pairwise results in {name}: no valid match rows")
                continue

            processed_any = False
            for match_id, winner in results:
                if match_id not in match_map:
                    continue
                item_a, item_b = match_map[match_id]
                winner_id = item_a if winner == "A" else item_b
                loser_id = item_b if winner == "A" else item_a

                winner_rating, loser_rating = env.rate_1vs1(ratings[winner_id], ratings[loser_id])
                ratings[winner_id] = winner_rating
                ratings[loser_id] = loser_rating

                wins[winner_id] += 1
                losses[loser_id] += 1
                appearances[item_a] += 1
                appearances[item_b] += 1
                processed_any = True

            if processed_any:
                results_parsed += 1
            else:
                parse_errors += 1
                eprint(f"Invalid pairwise results in {name}: no known match_ids")

    rankings = build_rankings_output(ratings, appearances, wins, losses)
    coverage_gaps = sum(1 for item_id in all_item_ids if appearances.get(item_id, 0) == 0)

    stats = {
        "total_items": len(all_item_ids),
        "subsets": len(subsets),
        "results_parsed": results_parsed,
        "parse_errors": parse_errors,
        "coverage_gaps": coverage_gaps,
        "mode": mode,
        "overlap": manifest.get("overlap"),
        "rubric": manifest.get("rubric"),
    }

    output_obj = {
        "rankings": rankings,
        "stats": stats,
    }

    output_dir = os.path.dirname(os.path.abspath(args.output))
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    write_json(args.output, output_obj)

    eprint(
        f"Aggregate complete: parsed={results_parsed} parse_errors={parse_errors} "
        f"coverage_gaps={coverage_gaps} output={args.output}"
    )

    return 0


def _find_agent_mux():
    """Return path to agent-mux binary, or None if not available.

    Resolution order:
      1. AGENT_MUX_PATH env var (explicit override)
      2. shutil.which("agent-mux") (on PATH)
      3. Relative to skill dir — works when skills are co-located in
         fieldwork (skills/agent-mux/scripts/agent-mux) or coordinator
         (.claude/skills/agent-mux/scripts/agent-mux)
    """
    # 1. Explicit env var
    env_path = os.environ.get("AGENT_MUX_PATH")
    if env_path and os.path.isfile(env_path) and os.access(env_path, os.X_OK):
        return env_path

    # 2. On PATH
    found = shutil.which("agent-mux")
    if found:
        return found

    # 3. Resolve relative to this script's location
    from pathlib import Path
    skill_dir = Path(__file__).resolve().parent.parent  # scripts/ -> trueskill-rank/
    for ancestor in (skill_dir.parent, skill_dir.parent.parent):
        candidate = ancestor / "agent-mux" / "scripts" / "agent-mux"
        if candidate.is_file() and os.access(str(candidate), os.X_OK):
            return str(candidate)

    return None


def _dispatch_one_agent_mux(agent_mux_bin, prompt_text, result_path):
    """Dispatch a single prompt via agent-mux. Returns True on success."""
    try:
        proc = subprocess.run(
            [
                agent_mux_bin,
                "--engine", "codex",
                "--model", "gpt-5.3-codex-spark",
                "--reasoning", "low",
                "--effort", "low",
                prompt_text,
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        output = proc.stdout if proc.stdout else proc.stderr
        with open(result_path, "w", encoding="utf-8") as f:
            f.write(output)
        return proc.returncode == 0
    except Exception as exc:
        error_payload = json.dumps({"success": False, "error": str(exc)})
        with open(result_path, "w", encoding="utf-8") as f:
            f.write(error_payload)
        return False


def _dispatch_one_openai(prompt_text, result_path):
    """Dispatch a single prompt via OpenAI API (stdlib urllib fallback). Returns True on success."""
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        error_payload = json.dumps({"success": False, "error": "OPENAI_API_KEY not set"})
        with open(result_path, "w", encoding="utf-8") as f:
            f.write(error_payload)
        return False

    payload = json.dumps({
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt_text}],
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = resp.read().decode("utf-8")
        data = json.loads(body)
        choices = data.get("choices") or []
        if not choices:
            raise ValueError("missing choices in API response")
        message = choices[0].get("message") or {}
        content = message.get("content", "")
        if isinstance(content, list):
            content = "".join(
                item.get("text", "")
                for item in content
                if isinstance(item, dict) and item.get("type") == "text"
            )
        if not isinstance(content, str):
            content = str(content)
        result_payload = json.dumps({"success": True, "response": content})
        with open(result_path, "w", encoding="utf-8") as f:
            f.write(result_payload)
        return True
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8") if exc.fp else str(exc)
        error_payload = json.dumps({"success": False, "error": body})
        with open(result_path, "w", encoding="utf-8") as f:
            f.write(error_payload)
        return False
    except Exception as exc:
        error_payload = json.dumps({"success": False, "error": str(exc)})
        with open(result_path, "w", encoding="utf-8") as f:
            f.write(error_payload)
        return False


def dispatch_workers(run_dir, mode):
    """
    Find all prompt files for the given mode in {run_dir}/prompts/, dispatch each
    to agent-mux (or OpenAI API fallback) in parallel, write results to
    {run_dir}/results/. Returns (succeeded, failed) counts.
    """
    prompts_dir = os.path.join(run_dir, "prompts")
    results_dir = os.path.join(run_dir, "results")
    os.makedirs(results_dir, exist_ok=True)

    if mode == "pairwise":
        pattern = "batch-"
    else:
        pattern = "subset-"

    prompt_files = sorted(
        os.path.join(prompts_dir, name)
        for name in os.listdir(prompts_dir)
        if name.startswith(pattern) and name.endswith(".txt")
    )

    if not prompt_files:
        eprint(f"ERROR: no prompt files found for mode '{mode}' in {prompts_dir}")
        return 0, 0

    agent_mux_bin = _find_agent_mux()
    if agent_mux_bin:
        eprint(f"Dispatch: using agent-mux at {agent_mux_bin} ({len(prompt_files)} prompts, max_workers=6)")
    else:
        eprint(f"agent-mux not found; using OpenAI API fallback ({len(prompt_files)} prompts, max_workers=6)")
        if not os.environ.get("OPENAI_API_KEY"):
            eprint("ERROR: OPENAI_API_KEY is required for fallback mode")
            return 0, len(prompt_files)

    def _dispatch_one(prompt_path):
        base_name = os.path.splitext(os.path.basename(prompt_path))[0]
        result_path = os.path.join(results_dir, f"{base_name}.json")
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                prompt_text = f.read()
        except Exception as exc:
            eprint(f"ERROR: failed to read {prompt_path}: {exc}")
            return base_name, False

        if agent_mux_bin:
            ok = _dispatch_one_agent_mux(agent_mux_bin, prompt_text, result_path)
        else:
            ok = _dispatch_one_openai(prompt_text, result_path)

        if not ok:
            eprint(f"FAILED: {base_name}")
        return base_name, ok

    succeeded = 0
    failed = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(_dispatch_one, p): p for p in prompt_files}
        for future in concurrent.futures.as_completed(futures):
            try:
                _name, ok = future.result()
                if ok:
                    succeeded += 1
                else:
                    failed += 1
            except Exception as exc:
                eprint(f"ERROR: unexpected exception during dispatch: {exc}")
                failed += 1

    eprint(f"Dispatch complete: total={len(prompt_files)} succeeded={succeeded} failed={failed}")
    return succeeded, failed


def cmd_run(args):
    eprint("Run mode: starting prepare step")
    prepare_rc = cmd_prepare(args)
    if prepare_rc != 0:
        return prepare_rc

    eprint(f"Run mode: dispatching workers for mode={args.mode}")
    succeeded, failed = dispatch_workers(args.output_dir, args.mode)

    if succeeded == 0 and failed > 0:
        eprint("ERROR: all dispatches failed, aborting")
        return 1

    if failed > 0:
        eprint(f"WARNING: {failed} dispatch(es) failed; continuing with partial results")

    eprint("Dispatch complete, starting aggregate step")
    agg_args = argparse.Namespace(run_dir=args.output_dir, output=args.output)
    return cmd_aggregate(agg_args)


def add_prepare_arguments(parser):
    parser.add_argument("--input", required=True, help="JSON file with items")
    parser.add_argument("--mode", choices=["batch", "pairwise"], default="batch")
    parser.add_argument("--overlap", type=int, choices=[2, 3, 4], default=3)
    parser.add_argument("--subset-size", type=int, default=None)
    parser.add_argument("--rubric", required=True, help="Path to rubric markdown file")
    parser.add_argument("--output-dir", required=True, help="Output directory")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--text-cap", type=int, default=1500)


def build_parser():
    parser = argparse.ArgumentParser(description="TrueSkill batch ranking CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare_parser = subparsers.add_parser("prepare", help="Prepare subsets and prompts")
    add_prepare_arguments(prepare_parser)
    prepare_parser.set_defaults(func=cmd_prepare)

    aggregate_parser = subparsers.add_parser("aggregate", help="Aggregate result files into final ranking")
    aggregate_parser.add_argument("--run-dir", required=True, help="Directory containing subsets.json and results/")
    aggregate_parser.add_argument("--output", required=True, help="Output JSON path for final rankings")
    aggregate_parser.set_defaults(func=cmd_aggregate)

    run_parser = subparsers.add_parser("run", help="Prepare, dispatch, and aggregate")
    add_prepare_arguments(run_parser)
    run_parser.add_argument("--output", required=True, help="Output JSON path for final rankings")
    run_parser.set_defaults(func=cmd_run)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
