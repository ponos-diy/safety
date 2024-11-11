import sys
import os

from load import load, Mitigation, MitigationTime, MitigationKind, sort_mitigations
from tools import make_unique


_, data_file = sys.argv
data = load(data_file)


preamble = r"""
\documentclass[a4paper]{article}
\usepackage[a4paper]{geometry}
\usepackage{longtable}
\usepackage{hyperref}
\usepackage{fontawesome5}

\title{Safety tables mitigation checklists}

\begin{document}

\maketitle
\tableofcontents


"""

closing = r"""
\end{document}
"""

def print_mitigation(mitigation: Mitigation):
    kind_tag = {
            MitigationKind.prevention: r"\faUserShield",
            MitigationKind.detection: r"\faEye",
            MitigationKind.impact: r"\faBandAid",
            }[mitigation.kind]
    time_tag = {
            MitigationTime.longterm: r"\faCalendarCheck",
            MitigationTime.preparation: r"\faClock",
            MitigationTime.before: r"\faCheckDouble",
            MitigationTime.during: r"\faCogs",
            MitigationTime.after: r"\faDoorOpen",
            MitigationTime.onfailure: r"\faExclamationTriangle",
            }[mitigation.time]
    return f"{time_tag} {kind_tag} {mitigation.description}"

def make_item_list(items: list[str]) -> str:
    result = r"\begin{itemize}" + "\n"
    for item in items:
        result += rf"\item {item}" + "\n"
    result += r"\end{itemize}" + "\n"
    return result

def make_filtered_mitigation_list(mitigations: list[Mitigation], time_filter: MitigationTime, heading: str) -> str:
    filtered_mitigations = [m for m in mitigations if m.time == time_filter]
    if not filtered_mitigations:
        return ""
    result = rf"\subsection{{{heading}}}"
    result += make_item_list([print_mitigation(m) for m in filtered_mitigations])
    return result

def make_checklists(data):
    checklists = ""
    for category in data.specific.values():
        mitigations = sort_mitigations(make_unique([ml for risk in category.risks for ml in risk.mitigation_links]))
        checklists += rf"\clearpage\section{{{category.name}}}\label{{sec:{category.name}}}"

        for time_filter, heading in (
            (MitigationTime.longterm, "Longterm preparations"),
            (MitigationTime.preparation, "Preparations"),
            (MitigationTime.before, "Before starting"),
            (MitigationTime.during, "During"),
            (MitigationTime.after, "After"),
            (MitigationTime.onfailure, "Emergencies"),
            ):
             checklists += make_filtered_mitigation_list(mitigations, time_filter, heading)

        if category.specializations:
            checklists += r"See also the more specific sections:"
            checklists += make_item_list([rf"{s.name} (\autoref{{sec:{s.name}}})" for s in category.specializations])
    return checklists



content = make_checklists(data)
latex = preamble + content + closing

os.makedirs("output", exist_ok=True)
with open("output/safety.tex", "w") as f:
    f.write(latex)
