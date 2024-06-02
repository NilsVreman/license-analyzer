import importlib.metadata as distmeta
import sys
from typing import Iterator, Optional

from license_analyzer import models, util

__distname__ = "license-analyzer"


SYSTEM_PACKAGES = (
    __distname__,
    "pip",
    "prettytable",
    "wcwidth",
    "setuptools",
    "wheel",
)

PRIORITY_URLS = (
    "documentation",
    "homepage",
    "source",
    "repository",
)


def _get_url_from_metadata(dist: distmeta.Distribution) -> Optional[str]:
    if (url := dist.metadata.get("home-page", None)) is not None:
        return url

    candidate_urls = {
        link_name.lower(): link_url
        for link in dist.metadata.get_all("Project-URL", [])
        for link_name, link_url in [link.split(", ", 1)]
        if link_name.lower() in PRIORITY_URLS
    }

    return next((candidate_urls[link_name] for link_name in PRIORITY_URLS if link_name in candidate_urls), None)


def _get_licenses_from_classifiers(dist: distmeta.Distribution) -> list[str]:
    return [
        lic.split(" :: ")[-1]
        for lic in filter(
            lambda c: c.startswith("License"),
            dist.metadata.get_all("classifier", []),
        )
    ]


def get_dist_metadata(dist: distmeta.Distribution) -> models.DistributionMetadata:
    return models.DistributionMetadata(  # type: ignore[call-arg]
        name=util.normalize_dist_name(dist.metadata["name"]),
        version=dist.version,
        license=dist.metadata.get("license", None),
        license_classifiers=_get_licenses_from_classifiers(dist),
        author=dist.metadata.get("author", None),
        maintainer=dist.metadata.get("maintainer", None),
        url=_get_url_from_metadata(dist),
        # description=dist.metadata.get("description", None),
    )


def get_distributions() -> Iterator[models.DistributionMetadata]:
    search_paths = sys.path
    dists = distmeta.distributions(path=search_paths)

    for dist in dists:
        if util.normalize_dist_name(dist.metadata["name"]) in SYSTEM_PACKAGES:
            continue

        dist_metadata = get_dist_metadata(dist)

        yield dist_metadata


def build_dependency_graph() -> models.DependencyGraph:
    graph = models.DependencyGraph()  # type: ignore[call-arg]
    search_paths = sys.path
    dists = distmeta.distributions(path=search_paths)

    # Add all distributions to the graph
    for dist in dists:
        if util.normalize_dist_name(dist.metadata["name"]) in SYSTEM_PACKAGES:
            continue

        dist_metadata = get_dist_metadata(dist)
        graph.distributions[dist_metadata.name] = dist_metadata

    # Add dependencies to the distributions
    dists = distmeta.distributions(path=search_paths)
    for dist in dists:
        dist_name = util.normalize_dist_name(dist.metadata["name"])
        dependencies = util.parse_dependencies(dist.requires) if dist.requires else []
        filtered_dependencies = util.filter_dependencies(dependencies)

        for dep in filtered_dependencies:
            if dep.name in SYSTEM_PACKAGES:
                continue

            assert dep.name in graph.distributions, f"Dependency {dep.name} not in graph"
            graph.distributions[dist_name].dependencies.append(graph.distributions[dep.name])

    return graph


def main() -> None:

    graph = build_dependency_graph()
    for dist in graph.distributions.values():
        print(dist.model_dump_json(indent=4, exclude_none=True, exclude={"description"}))


if __name__ == "__main__":
    main()
