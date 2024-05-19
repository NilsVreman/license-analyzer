import re

normalisation_pattern = re.compile(r"[-_.]+")


def normalize_dist_name(dist_name: str) -> str:
    return normalisation_pattern.sub("-", dist_name).lower()
