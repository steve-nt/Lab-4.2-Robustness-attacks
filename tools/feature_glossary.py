"""Build the feature glossary: what each of the 68 CICIDS2017 features means, in plain words.

The meanings are written by hand below (from the CICFlowMeter feature documentation). Everything
else is measured on the training split, so it always matches the data:
  - direction (forward / backward / both) and unit,
  - distinct values, minimum, median and maximum in the training set, and whether negatives occur,
  - the "twin" group: features linked by |correlation| > 0.95, directly or through a chain.

The group column is only a *proposal* from the name rules in section C1 of the task list; step C1
builds the real GROUP in code.

Writes results/tables/T4_feature_glossary.csv and results/tables/T4_feature_glossary.md.

Usage (from the repository root, environment active):
    python tools/feature_glossary.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.sparse.csgraph import connected_components
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "processed" / "clean.csv"
OUT_CSV = ROOT / "results" / "tables" / "T4_feature_glossary.csv"
OUT_MD = ROOT / "results" / "tables" / "T4_feature_glossary.md"
SEED = 42
TWIN_THRESHOLD = 0.95

US = "microseconds"
# name: (unit, plain-language meaning)
MEANING = {
    "Flow Duration": (US, "How long the whole conversation lasted, first packet to last"),
    "Total Fwd Packets": ("packets", "Number of packets the initiator (client/attacker) sent"),
    "Total Backward Packets": ("packets", "Number of packets the responder (server/victim) sent back"),
    "Total Length of Fwd Packets": ("bytes", "Total payload bytes the initiator sent"),
    "Total Length of Bwd Packets": ("bytes", "Total payload bytes the responder sent back"),
    "Fwd Packet Length Max": ("bytes", "Largest packet payload the initiator sent"),
    "Fwd Packet Length Min": ("bytes", "Smallest packet payload the initiator sent"),
    "Fwd Packet Length Mean": ("bytes", "Average packet payload the initiator sent"),
    "Fwd Packet Length Std": ("bytes", "How much the initiator's packet sizes vary"),
    "Bwd Packet Length Max": ("bytes", "Largest packet payload the responder sent"),
    "Bwd Packet Length Min": ("bytes", "Smallest packet payload the responder sent"),
    "Bwd Packet Length Mean": ("bytes", "Average packet payload the responder sent"),
    "Bwd Packet Length Std": ("bytes", "How much the responder's packet sizes vary"),
    "Flow Bytes/s": ("bytes per second", "Data rate of the whole conversation (bytes / duration)"),
    "Flow Packets/s": ("packets per second", "Packet rate of the whole conversation (packets / duration)"),
    "Flow IAT Mean": (US, "Average gap between two consecutive packets, either direction"),
    "Flow IAT Std": (US, "How much the gaps between packets vary"),
    "Flow IAT Max": (US, "Longest gap between two consecutive packets"),
    "Flow IAT Min": (US, "Shortest gap between two consecutive packets (a few impossible negative values "
                                  "come from clock errors in the recording)"),
    "Fwd IAT Total": (US, "Sum of the gaps between the initiator's packets"),
    "Fwd IAT Mean": (US, "Average gap between two packets of the initiator"),
    "Fwd IAT Std": (US, "How much the gaps between the initiator's packets vary"),
    "Fwd IAT Max": (US, "Longest gap between two packets of the initiator"),
    "Fwd IAT Min": (US, "Shortest gap between two packets of the initiator"),
    "Bwd IAT Total": (US, "Sum of the gaps between the responder's packets"),
    "Bwd IAT Mean": (US, "Average gap between two packets of the responder"),
    "Bwd IAT Std": (US, "How much the gaps between the responder's packets vary"),
    "Bwd IAT Max": (US, "Longest gap between two packets of the responder"),
    "Bwd IAT Min": (US, "Shortest gap between two packets of the responder"),
    "Fwd PSH Flags": ("0/1", "Whether the initiator set the PSH flag (\"deliver this data now\")"),
    "Fwd URG Flags": ("0/1", "Whether the initiator set the URG flag (\"urgent data\"); almost never used"),
    "Fwd Header Length": ("bytes", "Total header bytes of the initiator's packets (negative values are a known "
                                   "CICFlowMeter bug)"),
    "Bwd Header Length": ("bytes", "Total header bytes of the responder's packets (negative values are a known "
                                   "CICFlowMeter bug)"),
    "Fwd Packets/s": ("packets per second", "How fast the initiator sent packets"),
    "Bwd Packets/s": ("packets per second", "How fast the responder sent packets"),
    "Min Packet Length": ("bytes", "Smallest packet payload in the conversation, either direction"),
    "Max Packet Length": ("bytes", "Largest packet payload in the conversation, either direction"),
    "Packet Length Mean": ("bytes", "Average packet payload, both directions together"),
    "Packet Length Std": ("bytes", "How much packet sizes vary, both directions together"),
    "Packet Length Variance": ("bytes squared", "Packet Length Std squared (same information)"),
    "FIN Flag Count": ("0/1", "A packet with FIN (\"I am finished, close the connection\") was seen"),
    "SYN Flag Count": ("0/1", "A packet with SYN (\"let us start a connection\") was seen"),
    "RST Flag Count": ("0/1", "A packet with RST (\"abort the connection\") was seen"),
    "PSH Flag Count": ("0/1", "A packet with PSH (\"deliver this data now\") was seen"),
    "ACK Flag Count": ("0/1", "A packet with ACK (\"I received your data\") was seen"),
    "URG Flag Count": ("0/1", "A packet with URG (\"urgent data\") was seen"),
    "CWE Flag Count": ("0/1", "A packet with CWR (congestion window reduced) was seen"),
    "ECE Flag Count": ("0/1", "A packet with ECE (network congestion warning) was seen"),
    "Down/Up Ratio": ("ratio", "Responder packets divided by initiator packets (download vs. upload)"),
    "Average Packet Size": ("bytes", "Average packet size over the conversation"),
    "Avg Fwd Segment Size": ("bytes", "Average data per initiator packet (practically Fwd Packet Length Mean)"),
    "Avg Bwd Segment Size": ("bytes", "Average data per responder packet (practically Bwd Packet Length Mean)"),
    "Subflow Fwd Packets": ("packets", "Initiator packets per sub-conversation (bursts split by idle time)"),
    "Subflow Fwd Bytes": ("bytes", "Initiator bytes per sub-conversation"),
    "Subflow Bwd Packets": ("packets", "Responder packets per sub-conversation"),
    "Subflow Bwd Bytes": ("bytes", "Responder bytes per sub-conversation"),
    "Init_Win_bytes_forward": ("bytes", "Receive-window size in the initiator's first packet: how much data it "
                                        "accepts at once (-1 = not recorded)"),
    "Init_Win_bytes_backward": ("bytes", "Receive-window size in the responder's first packet, set by the "
                                         "victim's operating system (-1 = not recorded)"),
    "act_data_pkt_fwd": ("packets", "Initiator packets that carried at least 1 byte of data"),
    "min_seg_size_forward": ("bytes", "Smallest header size seen in the initiator's packets (a few huge "
                                      "negative values are the same CICFlowMeter bug as the header lengths)"),
    "Active Mean": (US, "Average length of a busy period (packets flowing) before the flow went quiet"),
    "Active Std": (US, "How much the busy periods vary"),
    "Active Max": (US, "Longest busy period"),
    "Active Min": (US, "Shortest busy period"),
    "Idle Mean": (US, "Average length of a quiet period between busy periods"),
    "Idle Std": (US, "How much the quiet periods vary"),
    "Idle Max": (US, "Longest quiet period"),
    "Idle Min": (US, "Shortest quiet period"),
}

COSTLY = {"Total Fwd Packets", "Total Length of Fwd Packets", "Subflow Fwd Packets", "Subflow Fwd Bytes",
          "act_data_pkt_fwd"}
FREE_SIZES = {"Fwd Header Length", "Avg Fwd Segment Size", "min_seg_size_forward"}


def direction(name):
    if "Bwd" in name or "backward" in name.lower():
        return "backward"
    if "Fwd" in name or "forward" in name.lower():
        return "forward"
    return "both"


def proposed_group(name):
    """The name rules from section C1 of the task list, in the same order."""
    if direction(name) == "backward" or "Flag" in name:
        return "Fixed"
    if any(k in name for k in ("IAT", "Idle", "Active")) or name == "Flow Duration":
        return "Free"
    if name.startswith("Fwd Packet Length") or name in FREE_SIZES:
        return "Free"
    if name in COSTLY:
        return "Costly"
    return "Fixed"


def load_train():
    """The training part of the Lab 1 split (same code as parts/00_setup.ipynb)."""
    df = pd.read_csv(DATA_FILE)
    attack_type = df["Label"]
    X = df.drop(columns=["Label"]).select_dtypes(include=[np.number])
    X_tmp, _, type_tmp, _ = train_test_split(X, attack_type, test_size=0.20, stratify=attack_type,
                                             random_state=SEED)
    X_train, _ = train_test_split(X_tmp, test_size=0.25, stratify=type_tmp, random_state=SEED)
    assert X_train.shape == (267_984, 68), X_train.shape
    return X_train


def twin_groups(X_train):
    """Group id per feature: connected components of the graph |corr| > TWIN_THRESHOLD."""
    corr = np.abs(np.corrcoef(X_train.to_numpy(dtype=float), rowvar=False))
    linked = corr > TWIN_THRESHOLD
    np.fill_diagonal(linked, False)
    _, labels = connected_components(linked, directed=False)
    labels = pd.Series(labels, index=X_train.columns)
    sizes = labels.map(labels.value_counts())
    # Number the real groups (2+ members) 1, 2, ... in column order; singletons get no group.
    order = {g: i + 1 for i, g in enumerate(dict.fromkeys(labels[sizes > 1]))}
    group = labels.map(order)
    members = {g: ", ".join(group.index[group == g]) for g in order.values()}
    return group, group.map(members)


def main():
    X_train = load_train()
    missing = set(X_train.columns) ^ set(MEANING)
    assert not missing, f"meanings and data columns differ: {sorted(missing)}"

    twin, twin_members = twin_groups(X_train)
    table = pd.DataFrame({
        "feature": X_train.columns,
        "meaning": [MEANING[c][1] for c in X_train.columns],
        "unit": [MEANING[c][0] for c in X_train.columns],
        "direction": [direction(c) for c in X_train.columns],
        "group_proposed": [proposed_group(c) for c in X_train.columns],
        "distinct_values": X_train.nunique().to_numpy(),
        "train_min": X_train.min().to_numpy(),
        "train_median": X_train.median().to_numpy(),
        "train_max": X_train.max().to_numpy(),
        "has_negatives": (X_train < 0).any().to_numpy(),
        "twin_group": twin.astype("Int64").to_numpy(),
        "twin_members": twin_members.fillna("").to_numpy(),
    })
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(OUT_CSV, index=False)
    write_markdown(table)

    print(f"Wrote {OUT_CSV.relative_to(ROOT)} and {OUT_MD.relative_to(ROOT)} ({len(table)} features)")
    print("Proposed groups:", table.group_proposed.value_counts().to_dict())
    print("Direction:", table.direction.value_counts().to_dict())
    print(f"Features with negative values: {int(table.has_negatives.sum())}")
    n_groups = table.twin_group.nunique()
    print(f"Twin groups (|corr| > {TWIN_THRESHOLD}): {n_groups}, covering "
          f"{int(table.twin_group.notna().sum())} features")


def fmt(x):
    return f"{x:,.0f}" if abs(x) >= 100 else f"{x:g}"


def write_markdown(table):
    lines = [
        "# Feature glossary (CICIDS2017, 68 features)",
        "",
        "*Generated by `tools/feature_glossary.py` from the training split; do not edit by hand.*",
        "",
        "**Initiator** = the side that opened the conversation (for an attack: the attacker).",
        "**Responder** = the other side (the victim's server). In the names, `Fwd` means sent by the",
        "initiator and `Bwd` sent by the responder. IAT = inter-arrival time, the gap between two packets.",
        "",
        "The *proposed group* follows the name rules in step C1 (Free = the attacker can raise it cheaply,",
        "Costly = with effort, Fixed = cannot change). Step C1 builds the real groups in code.",
        "",
        "## All features",
        "",
        "| Feature | Meaning | Unit | Dir. | Proposed group | Train min / median / max | Twin group |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in table.itertuples():
        twin = "" if pd.isna(r.twin_group) else str(int(r.twin_group))
        neg = " (has negatives)" if r.has_negatives else ""
        lines.append(f"| `{r.feature}` | {r.meaning} | {r.unit} | {r.direction} | {r.group_proposed} | "
                     f"{fmt(r.train_min)} / {fmt(r.train_median)} / {fmt(r.train_max)}{neg} | {twin} |")

    lines += ["", f"## Twin groups (|correlation| > {TWIN_THRESHOLD} on the training set)", "",
              "Features in one group carry almost the same information. Removing one of them alone tells",
              "you little, because its twins still carry the signal (lab sections 3.6, E2 and F1).", "",
              "| Group | Members | Proposed groups of the members |", "|---|---|---|"]
    groups = table.dropna(subset=["twin_group"]).drop_duplicates("twin_group")
    for r in groups.itertuples():
        groups_in = table.loc[table.twin_group == r.twin_group, "group_proposed"].unique()
        mixed = " (**mixed**: the attacker controls only part of it)" if len(groups_in) > 1 else ""
        lines.append(f"| {int(r.twin_group)} | {r.twin_members} | {', '.join(sorted(groups_in))}{mixed} |")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
