from enum import StrEnum, auto
from typing import Any

from pydantic import BaseModel, Field
import yaml

from tools import make_unique

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

def load_yaml(filename):
    with open(filename, "r") as f:
        return yaml.load(f, Loader=Loader)

class MitigationKind(StrEnum):
    prevention = auto()
    detection = auto()
    impact = auto()

    def to_int(self):
        return {
                MitigationKind.prevention: 0,
                MitigationKind.detection: 1,
                MitigationKind.impact: 2,
                }[self]

class MitigationTime(StrEnum):
    preparation = auto()
    before = auto()
    during = auto()
    after = auto()
    onfailure = auto()

    def to_int(self):
        return {
                MitigationTime.preparation: 0,
                MitigationTime.before: 1,
                MitigationTime.during: 2,
                MitigationTime.after: 3,
                MitigationTime.onfailure: 4,
                }[self]


class Mitigation(BaseModel):
    name: None | str = None
    kind: MitigationKind
    time: MitigationTime
    description: str


def _get_mitigation_priority(mitigation: Mitigation):
    return mitigation.time.to_int() * 10 + mitigation.kind.to_int()

def sort_mitigations(mitigations):
    return sorted(mitigations, key=_get_mitigation_priority)


class Impact(BaseModel):
    name: None | str = None
    description: str
    mitigations: list[str] = []
    mitigation_links: None | list[Mitigation] = None


class Failure(BaseModel):
    name: None | str = None
    description: str
    mitigations: list[str] = []
    impacts: list[str] = []
    
    impact_links: None | list[Impact] = None
    mitigation_links: None | list[Mitigation] = None
class Risk(BaseModel):
    failure: str
    impacts: list[str] = []
    mitigations: list[str] = []

    failure_link: None | Failure = None
    impact_links: None | list[Impact] = None
    mitigation_links: None | list[Mitigation] = None

class Category(BaseModel):
    name: None | str = None
    risks: list[Risk]

class DataModel(BaseModel):
    failures: dict[str, Failure]
    impacts: dict[str, Impact]
    mitigations: dict[str, Mitigation]
    specific: dict[str, Category]

def apply_names_to_dict(d: dict[str, Any]):
    for key, value in d.items():
        value.name = key

def apply_names(data: DataModel):
    apply_names_to_dict(data.failures)
    apply_names_to_dict(data.impacts)
    apply_names_to_dict(data.mitigations)
    apply_names_to_dict(data.specific)

def find_in_dict(d: dict[str, Any], key: str, tag: str):
    try:
        return d[key]
    except KeyError as e:
        e.add_note(f"while searching for {tag}")
        e.add_note(f"options are: {sorted(d.keys())}")
        raise

def find_mitigations(data: DataModel, mitigations: list[str]):
    assert isinstance(mitigations, list)
    return [find_in_dict(data.mitigations, m, "mitigations") for m in mitigations]

def find_impacts(data: DataModel, impacts: list[str]):
    assert isinstance(impacts, list)
    return [find_in_dict(data.impacts, i, "impacts") for i in impacts]


def link(data: DataModel):
    for impact in data.impacts.values():
        impact.mitigation_links = find_mitigations(data, impact.mitigations)

    for failure in data.failures.values():
        failure.impact_links = find_impacts(data, failure.impacts)
        failure.mitigation_links = find_mitigations(data, failure.mitigations)
        for impact in failure.impact_links:
            failure.mitigation_links += impact.mitigation_links

    for category in data.specific.values():
        for risk in category.risks:
            risk.failure_link = find_in_dict(data.failures, risk.failure, "failures")
            risk.impact_links = make_unique(find_impacts(data, risk.impacts) + risk.failure_link.impact_links)
            risk.mitigation_links = make_unique(find_mitigations(data, risk.mitigations) + risk.failure_link.mitigation_links + [ml for impact in risk.impact_links for ml in impact.mitigation_links])


def load(filename):
    raw = load_yaml(filename)
    data = DataModel(**raw)
    apply_names(data)
    link(data)
    return data


