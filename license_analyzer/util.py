import re
import unittest
from collections import namedtuple

from packaging.markers import Marker
from packaging.requirements import Requirement

normalisation_pattern = re.compile(r"[-_.]+")


def normalize_dist_name(dist_name: str) -> str:
    return normalisation_pattern.sub("-", dist_name).lower()


Dependency = namedtuple("Dependency", ["name", "extras", "specifier", "marker"])


def parse_dependencies(reqs: list[str]) -> list[Dependency]:
    parsed_dependencies = []

    for req in reqs:
        requirement = Requirement(req)
        name = normalize_dist_name(requirement.name)
        extras = requirement.extras
        specifier = str(requirement.specifier)
        marker = requirement.marker

        parsed_dependencies.append(Dependency(name, extras, specifier, marker))

    return parsed_dependencies


def filter_dependencies(dependencies: list[Dependency]) -> list[Dependency]:
    valid_dependencies = []

    for req in dependencies:
        if req.marker:
            if Marker(str(req.marker)).evaluate():
                valid_dependencies.append(req)
        else:
            valid_dependencies.append(req)

    return valid_dependencies


class TestDependencyFiltering(unittest.TestCase):

    def test_filter_requirements_python_312(self) -> None:
        dependencies = [
            "requests[security]>=2.24.0; python_version < '3.8'",
            "tomli>=1.1.0; python_version <= '3.11'",
            "somepackage>=1.0.0",
        ]

        expected_valid_dependencies = [Dependency(name="somepackage", extras=set(), specifier=">=1.0.0", marker=None)]

        parsed_dependencies = parse_dependencies(dependencies)
        valid_dependencies = filter_dependencies(parsed_dependencies)

        # Extract the relevant parts for comparison
        valid_dependencies_simplified = [(req.name, req.specifier) for req in valid_dependencies]
        expected_valid_dependencies_simplified = [(req.name, req.specifier) for req in expected_valid_dependencies]

        self.assertEqual(valid_dependencies_simplified, expected_valid_dependencies_simplified)


if __name__ == "__main__":
    unittest.main()
