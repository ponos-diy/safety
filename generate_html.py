import sys
import os

from load import load, MitigationTime, MitigationKind, sort_mitigations
from tools import make_unique

_, data_file = sys.argv

data = load(data_file)

with open("template.html", "r") as f:
    template = f.read()

def print_mitigation(mitigation):
    kind_tag = {
            MitigationKind.prevention: "bi-shield-check",
            MitigationKind.detection: "bi-eye",
            MitigationKind.impact: "bi-bandaid",
            }[mitigation.kind]
    time_tag = {
            MitigationTime.longterm: "bi-calendar3",
            MitigationTime.preparation: "bi-clock",
            MitigationTime.before: "bi-list-check",
            MitigationTime.during: "bi-repeat",
            MitigationTime.after: "bi-door-open",
            MitigationTime.onfailure: "bi-exclamation-triangle",
            }[mitigation.time]

    return f"""<span class="bi {time_tag}"/><span class="bi {kind_tag}"/> {mitigation.description}"""

def make_full_table(data):
    table = ""
    for category in data.specific.values():
        rowspan = len(category.risks)
        for i, risk in enumerate(category.risks):
            table+= "<tr>"
            if i == 0:
                table += f"""<td rowspan="{rowspan}">{category.name}"""
                for base in category.specializations:
                    table += f'<br/>see also {base.name}'
                table += """</td>"""

            inherited_text = f'<span class="fw-lighter">(inherited from {risk.inherited_from})</span>' if risk.inherited_from else ""
            table += f"""
            <td>{risk.failure_link.description}{inherited_text}</td>
            <td>{'<br/>'.join(il.description for il in risk.impact_links)}</td>
            <td>{'<br/>'.join(print_mitigation(ml) for ml in sort_mitigations(risk.mitigation_links))}</td>
            </tr>
            """
    return table

def make_short_table(data):
    table = ""
    for i_category, category in enumerate(data.specific.values()):
        mitigations = make_unique([ml for risk in category.risks for ml in risk.mitigation_links])
        accordion_body = "".join(f"<p>{print_mitigation(ml)}</p>" for ml in sort_mitigations(mitigations))
        table += f"""
            <div class="accordion-item">
                <h2 class="accordion-header">
                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#shortAccordion{i_category}" aria-expanded="false" aria-controls="shortAccordion{i_category}">
                    {category.name}
                </button>
                </h2>
                <div id="shortAccordion{i_category}" class="accordion-collapse collapse">
                    <div class="accordion-body">{accordion_body}</div>
                </div>
            </div>"""
    return table

full_table = make_full_table(data)
short_table = make_short_table(data)

def make_intro():
    with open("intro.txt", "r") as f:
        intro_lines = f.readlines()
    return "".join(f"<p>{line}</p>" for line in intro_lines)

intro = make_intro()

html = template.format(full_table=full_table, short_table=short_table, title="safety tables", intro=intro, version="version")


os.makedirs("output", exist_ok=True)

with open("output/safety.html", "w") as f:
    f.write(html)
