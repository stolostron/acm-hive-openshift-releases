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
Helper script to add a new branch to the acm-hive-openshift-releases repository.
Shows recent branches and suggests the next version.
Automatically updates all required files.
"""

import json
import sys
import os
import re

CRON_WORKFLOW = ".github/workflows/cron-sync-imageset.yml"
POST_SUBMIT_WORKFLOW = ".github/workflows/post-submit-imageset.yml"

def get_backplane_branches():
    """Get all backplane branches from supported-ocp-versions.json"""
    with open("supported-ocp-versions.json", "r", encoding="UTF-8") as file:
        obj = json.load(file)

    backplane_branches = []
    for branch in obj.keys():
        if branch.startswith("backplane-"):
            match = re.match(r'backplane-(\d+)\.(\d+)', branch)
            if match:
                major = int(match.group(1))
                minor = int(match.group(2))
                backplane_branches.append((major, minor, branch, obj[branch]))

    # Sort by version
    backplane_branches.sort(key=lambda x: (x[0], x[1]))
    return backplane_branches

def suggest_next_ocp_versions(current_versions):
    """Suggest next OCP versions based on current pattern"""
    versions = []
    for v in current_versions:
        match = re.match(r'(\d+)\.(\d+)', v)
        if match:
            major = int(match.group(1))
            minor = int(match.group(2))
            versions.append((major, minor))

    if not versions:
        return []

    versions.sort()
    # Shift versions up by 1 minor version
    new_versions = []
    for major, minor in versions:
        new_versions.append(f"{major}.{minor + 1}")

    return new_versions

def generate_cron_job_block(branch_name):
    """Generate the job block for cron-sync-imageset.yml"""
    job_name = branch_name.replace(".", "_")
    return f'''
  sync-clusterimageset-{job_name}:
    name: sync-clusterimageset-{branch_name}
    runs-on: ubuntu-latest
    steps:
      - name: checkout code
        uses: actions/checkout@v2
      - name: sync-clusterimageset
        run: make sync-images-job
        env:
          TARGET_BRANCH: {branch_name}
      - name: Deploy
        uses: peaceiris/actions-gh-pages@v3
        with:
          publish_dir: ./clusterImageSets
          github_token: ${{{{ secrets.GITHUB_TOKEN }}}}
          publish_branch: {branch_name}
          keep_files: true
          destination_dir: clusterImageSets
'''

def generate_post_submit_job_block(branch_name):
    """Generate the job block for post-submit-imageset.yml"""
    job_name = branch_name.replace(".", "_")
    return f'''
  sync-clusterimageset-{job_name}:
    name: sync-clusterimageset-{branch_name}
    runs-on: ubuntu-latest
    steps:
      - name: checkout code
        uses: actions/checkout@v2
      - name: sync-clusterimageset
        run: make sync-images-job
        env:
          TARGET_BRANCH: {branch_name}
      - name: Deploy
        uses: peaceiris/actions-gh-pages@v3
        with:
          publish_dir: ./clusterImageSets
          github_token: ${{{{ secrets.GITHUB_TOKEN }}}}
          publish_branch: {branch_name}
          destination_dir: clusterImageSets
'''

def add_to_versions_json(branch_name, ocp_versions):
    """Add a new branch to supported-ocp-versions.json"""
    with open("supported-ocp-versions.json", "r", encoding="UTF-8") as file:
        obj = json.load(file)

    obj[branch_name] = ocp_versions

    with open("supported-ocp-versions.json", "w", encoding="UTF-8") as file:
        json.dump(obj, file, indent=2)
        file.write("\n")

def add_to_workflow(workflow_path, job_block):
    """Append a job block to a workflow file"""
    with open(workflow_path, "r", encoding="UTF-8") as file:
        content = file.read()

    # Append the job block
    content = content.rstrip() + "\n" + job_block

    with open(workflow_path, "w", encoding="UTF-8") as file:
        file.write(content)

def add_branch(branch_name, ocp_versions):
    """Add a new branch to all required files"""
    # Update supported-ocp-versions.json
    add_to_versions_json(branch_name, ocp_versions)
    print(f"  Updated supported-ocp-versions.json")

    # Update cron workflow
    cron_job = generate_cron_job_block(branch_name)
    add_to_workflow(CRON_WORKFLOW, cron_job)
    print(f"  Updated {CRON_WORKFLOW}")

    # Update post-submit workflow
    post_submit_job = generate_post_submit_job_block(branch_name)
    add_to_workflow(POST_SUBMIT_WORKFLOW, post_submit_job)
    print(f"  Updated {POST_SUBMIT_WORKFLOW}")

def main():
    if not os.path.isfile("supported-ocp-versions.json"):
        print("Error: Run this script from the repository root directory")
        sys.exit(1)

    branches = get_backplane_branches()

    if len(branches) < 3:
        print("Error: Not enough backplane branches found")
        sys.exit(1)

    # Show last 3 branches
    print("\n=== Last 3 Backplane Releases ===")
    print("-" * 50)
    for major, minor, branch, ocp_versions in branches[-3:]:
        print(f"  {branch}: OCP {', '.join(ocp_versions)}")

    # Suggest next branch
    latest = branches[-1]
    next_major = latest[0]
    next_minor = latest[1] + 1
    next_branch = f"backplane-{next_major}.{next_minor}"
    next_ocp_versions = suggest_next_ocp_versions(latest[3])

    print("-" * 50)
    print(f"\n=== Suggested Next Branch ===")
    print(f"  Branch: {next_branch}")
    print(f"  OCP Versions: {', '.join(next_ocp_versions)}")

    # Interactive mode
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        print("\n" + "=" * 50)
        response = input(f"Add {next_branch} with OCP versions {next_ocp_versions}? [Y/n]: ").strip().lower()
        if response in ('', 'y', 'yes'):
            print(f"\nAdding {next_branch}...")
            add_branch(next_branch, next_ocp_versions)
            print(f"\nDone! Files updated:")
            print(f"  - supported-ocp-versions.json")
            print(f"  - {CRON_WORKFLOW}")
            print(f"  - {POST_SUBMIT_WORKFLOW}")
            print(f"\nNext steps:")
            print(f"  1. Review the changes: git diff")
            print(f"  2. Commit and create a PR to main")
            print(f"  3. The {next_branch} branch will be created automatically on first workflow run")
        else:
            print("Aborted.")
    else:
        print("\n=== Files to Update ===")
        print("  1. supported-ocp-versions.json")
        print(f"  2. {CRON_WORKFLOW}")
        print(f"  3. {POST_SUBMIT_WORKFLOW}")
        print("\nRun 'make add-branch' to update all files automatically.")

if __name__ == "__main__":
    main()
