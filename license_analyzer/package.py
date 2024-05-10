import subprocess
import sys
from importlib.metadata import Distribution, distributions
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

UNKNOWN = "UNKNOWN"


def get_url_from_metadata(dist: Distribution) -> Optional[str]:
    if (url := dist.metadata.get("home-page", None)) is not None:
        return url

    print("Project-URL: ", dist.metadata.get_all("Project-URL", []))
    candidate_urls = {
        link_name.lower(): link_url
        for link in dist.metadata.get_all("Project-URL", [])
        for link_name, link_url in [link.split(", ", 1)]
        if link_name.lower() in PRIORITY_URLS
    }

    return next((candidate_urls[link_name] for link_name in PRIORITY_URLS if link_name in candidate_urls), None)


def get_licenses_from_classifiers(dist: Distribution) -> list[str]:
    return [
        lic.split(" :: ")[-1]
        for lic in filter(
            lambda c: c.startswith("License"),
            dist.metadata.get_all("classifier", []),
        )
    ]


def get_dist_metadata(dist: Distribution) -> models.DistributionMetadata:
    print("DIST METADATA")
    print("requires", dist.requires)

    return models.DistributionMetadata(
        name=dist.metadata["name"],
        version=dist.version,
        license=dist.metadata.get("license", None),
        license_classifiers=get_licenses_from_classifiers(dist),
        author=dist.metadata.get("author", None),
        maintainer=dist.metadata.get("maintainer", None),
        url=get_url_from_metadata(dist),
        description=dist.metadata.get("description", None),
    )


def get_packages() -> Iterator[models.DistributionMetadata]:
    search_paths = sys.path
    dists = distributions(path=search_paths)

    for dist in dists:
        dist_name = util.normalize_dist_name(dist.metadata["name"])

        if dist_name in SYSTEM_PACKAGES:
            continue

        dist_metadata = get_dist_metadata(dist)

        yield dist_metadata


def main() -> None:
    dists = subprocess.check_output([sys.executable, "-m", "pip", "freeze"]).decode("utf-8").splitlines()
    for dist in dists:
        print(dist)

    print("#" * 80)

    for pkg in get_packages():
        print(pkg.model_dump_json(indent=4, exclude_none=True, exclude={"description"}))

    print("#" * 80)

    raise NotImplementedError("Still not implemented everything you should")


if __name__ == "__main__":
    main()
