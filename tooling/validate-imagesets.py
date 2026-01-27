#!/usr/bin/env python3
# Copyright 2025 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0
# This file was created with assistance from generative AI.

"""
Validate ClusterImageSet YAML files.

This script validates that:
1. YAML files have valid structure (apiVersion, kind, metadata, spec.releaseImage)
2. Release images have valid format (tag or SHA digest)
3. Images exist in the registry (optional, requires network)

Usage:
    python3 tooling/validate-imagesets.py [--check-registry] [--path PATH]
"""

import argparse
import os
import re
import sys
import time
import urllib.request
import urllib.error
import yaml
from concurrent.futures import ThreadPoolExecutor, as_completed

# Constants
REGISTRY_BASE = "quay.io/openshift-release-dev/ocp-release"
QUAY_API_BASE = "https://quay.io/v2/openshift-release-dev/ocp-release/manifests"

# Regex patterns
SHA_PATTERN = re.compile(r"^sha256:[a-f0-9]{64}$")
TAG_PATTERN = re.compile(r"^[\w][\w.\-]*$")
IMAGE_WITH_SHA = re.compile(r"^quay\.io/openshift-release-dev/ocp-release@(sha256:[a-f0-9]{64})$")
IMAGE_WITH_TAG = re.compile(r"^quay\.io/openshift-release-dev/ocp-release:([\w][\w.\-]*)$")
IMAGE_WITH_TAG_AND_SHA = re.compile(r"^quay\.io/openshift-release-dev/ocp-release:([\w][\w.\-]*)@(sha256:[a-f0-9]{64})$")


class ValidationResult:
    def __init__(self, file_path):
        self.file_path = file_path
        self.errors = []
        self.warnings = []
        self.image_ref = None
        self.image_type = None  # 'sha' or 'tag'

    def add_error(self, message):
        self.errors.append(message)

    def add_warning(self, message):
        self.warnings.append(message)

    @property
    def is_valid(self):
        return len(self.errors) == 0


def validate_yaml_structure(file_path):
    """Validate YAML file structure and extract release image."""
    result = ValidationResult(file_path)

    try:
        with open(file_path, 'r') as f:
            content = yaml.safe_load(f)
    except yaml.YAMLError as e:
        result.add_error(f"Invalid YAML: {e}")
        return result
    except Exception as e:
        result.add_error(f"Failed to read file: {e}")
        return result

    if content is None:
        result.add_error("Empty YAML file")
        return result

    if not isinstance(content, dict):
        result.add_error(f"Invalid YAML structure: expected mapping, got {type(content).__name__}")
        return result

    # Check required fields
    api_version = content.get('apiVersion')
    if api_version != 'hive.openshift.io/v1':
        result.add_error(f"Invalid apiVersion: {api_version} (expected hive.openshift.io/v1)")

    kind = content.get('kind')
    if kind != 'ClusterImageSet':
        result.add_error(f"Invalid kind: {kind} (expected ClusterImageSet)")

    metadata = content.get('metadata') or {}
    if not metadata.get('name'):
        result.add_error("Missing metadata.name")

    spec = content.get('spec') or {}
    release_image = spec.get('releaseImage')
    if not release_image:
        result.add_error("Missing spec.releaseImage")
        return result

    # Validate release image format
    tag_sha_match = IMAGE_WITH_TAG_AND_SHA.match(release_image)
    sha_match = IMAGE_WITH_SHA.match(release_image)
    tag_match = IMAGE_WITH_TAG.match(release_image)

    if tag_sha_match:
        result.image_ref = tag_sha_match.group(2)  # Use SHA as the primary ref
        result.image_type = 'tag_and_sha'
    elif sha_match:
        result.image_ref = sha_match.group(1)
        result.image_type = 'sha'
    elif tag_match:
        result.image_ref = tag_match.group(1)
        result.image_type = 'tag'
    else:
        result.add_error(f"Invalid releaseImage format: {release_image}")

    return result


def check_image_exists(image_ref, image_type):
    """Check if an image exists in the registry using quay.io API."""
    if image_type == 'sha':
        url = f"{QUAY_API_BASE}/{image_ref}"
    else:
        url = f"{QUAY_API_BASE}/{image_ref}"

    request = urllib.request.Request(url, method='HEAD')
    request.add_header('Accept', 'application/vnd.docker.distribution.manifest.v2+json')

    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.status == 200, None
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False, "Image not found in registry"
        return False, f"HTTP error: {e.code}"
    except urllib.error.URLError as e:
        return False, f"Network error: {e.reason}"
    except Exception as e:
        return False, f"Error: {e}"


def find_yaml_files(base_path):
    """Find all YAML files in clusterImageSets directory."""
    yaml_files = []
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith('.yaml') or file.endswith('.yml'):
                yaml_files.append(os.path.join(root, file))
    return yaml_files


def validate_file(file_path, check_registry=False):
    """Validate a single file."""
    result = validate_yaml_structure(file_path)

    if result.is_valid and check_registry and result.image_ref:
        exists, error = check_image_exists(result.image_ref, result.image_type)
        if not exists:
            result.add_error(f"Registry check failed: {error}")

    return result


def main():
    parser = argparse.ArgumentParser(description='Validate ClusterImageSet YAML files')
    parser.add_argument('--check-registry', action='store_true',
                        help='Check if images exist in the registry (requires network)')
    parser.add_argument('--path', default='clusterImageSets',
                        help='Path to clusterImageSets directory (default: clusterImageSets)')
    parser.add_argument('--parallel', type=int, default=10,
                        help='Number of parallel workers for registry checks (default: 10)')
    parser.add_argument('--quiet', action='store_true',
                        help='Only show errors and summary')
    args = parser.parse_args()

    if not os.path.exists(args.path):
        print(f"Error: Path '{args.path}' does not exist")
        sys.exit(1)

    yaml_files = find_yaml_files(args.path)
    if not yaml_files:
        print(f"No YAML files found in '{args.path}'")
        sys.exit(0)

    print(f"Validating {len(yaml_files)} YAML files...", flush=True)
    if args.check_registry:
        print("Registry checks enabled", flush=True)

    results = []
    total_errors = 0
    total_warnings = 0
    tag_count = 0
    tag_and_sha_count = 0

    start_time = time.time()

    if args.check_registry:
        # Use parallel processing for registry checks
        with ThreadPoolExecutor(max_workers=args.parallel) as executor:
            future_to_file = {
                executor.submit(validate_file, f, True): f
                for f in yaml_files
            }
            for future in as_completed(future_to_file):
                result = future.result()
                results.append(result)
    else:
        # Sequential processing for structure-only validation
        for file_path in yaml_files:
            result = validate_file(file_path, check_registry=False)
            results.append(result)

    elapsed = time.time() - start_time
    print(f"Completed {len(yaml_files)} files in {elapsed:.1f}s", flush=True)

    # Process results
    for result in results:
        if result.image_type == 'tag_and_sha':
            tag_and_sha_count += 1
        elif result.image_type == 'tag':
            tag_count += 1

        if result.errors:
            total_errors += len(result.errors)
            rel_path = os.path.relpath(result.file_path)
            print(f"ERROR: {rel_path}")
            for error in result.errors:
                print(f"  - {error}")

        if result.warnings:
            total_warnings += len(result.warnings)
            if not args.quiet:
                rel_path = os.path.relpath(result.file_path)
                print(f"WARNING: {rel_path}")
                for warning in result.warnings:
                    print(f"  - {warning}")

    # Summary
    print()
    print("=" * 60)
    print("Validation Summary")
    print("=" * 60)
    print(f"Total files:     {len(yaml_files)}")
    print(f"Tag+SHA-based:   {tag_and_sha_count}")
    print(f"Tag-based:       {tag_count}")
    print(f"Errors:          {total_errors}")
    print(f"Warnings:        {total_warnings}")
    print("=" * 60)

    if total_errors > 0:
        print("\nValidation FAILED")
        sys.exit(1)
    else:
        print("\nValidation PASSED")
        sys.exit(0)


if __name__ == '__main__':
    main()
