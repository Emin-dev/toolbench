#!/usr/bin/env python3
"""One-shot create-only candidate publication and exact temporary-branch cleanup."""
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request

TARGET = "Emin-dev/toolbench"
SOURCE = "Emin-dev/accessproof"
TARGET_MAIN = "19f33debf338dcde40f0960dabf1b6740177d14c"
SOURCE_MAIN = "e745b89219da2c9ac85b2ab9bd0e224164a19920"
CANDIDATE = "e854510b2783502c1132e383f179f497bdc5625c"
CANDIDATE_TREE = "52e3173c16098cc6fbbc2bdfe1303a9df29c62f3"
REVIEW_BRANCH = "consolidate/accessproof"
TEMP_BRANCH = "consolidation/publish-accessproof-e854510"
BUNDLE_HASH = "6946070fc49888660652c7eacc4e7f496814ce132d6217642ae0ef6d701b304f"
MANIFEST_HASH = "bee6363155e3fc68bc0b5f0c2f818186638e7b1d5dbb9ca61a13a9684186bc85"
REMOTE = "https://github.com/Emin-dev/toolbench.git"
SHA = re.compile(r"^[0-9a-f]{40}$")
ZERO = "0" * 40


class Stop(Exception):
    """A closed gate; never authorizes a retry with wider permissions."""


def require(condition, message):
    if not condition:
        raise Stop(message)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise Stop("Unexpected GitHub API redirect; stopped.")


def pre_push_hook(local_sha, remote_sha, branch, deletion=False):
    require(bool(SHA.fullmatch(local_sha)) and bool(SHA.fullmatch(remote_sha)),
            "Invalid expected push identities.")
    require((not deletion and local_sha == CANDIDATE and remote_sha == ZERO and branch == REVIEW_BRANCH)
            or (deletion and local_sha == ZERO and remote_sha != ZERO and branch == TEMP_BRANCH),
            "Unexpected push operation.")
    local_ref = "(delete)" if deletion else local_sha
    # Checks the actual push advertisement; receive-pack checks that old OID
    # again atomically. No force or lease flags, and no repository hooks run.
    return f'''#!/usr/bin/env python3
import sys
updates = [line.split() for line in sys.stdin if line.strip()]
expected = [{local_ref!r}, {local_sha!r}, {("refs/heads/" + branch)!r}, {remote_sha!r}]
valid = len(sys.argv) == 3 and sys.argv[2] == {REMOTE!r} and updates == [expected]
if not valid:
    print("Exact branch advertisement mismatch; stopped.", file=sys.stderr)
sys.exit(0 if valid else 1)
'''


class Adapter:
    def __init__(self, cwd):
        self.cwd = cwd

    def git(self, *args, data=None, write_token=None, expected_remote=None):
        # No inherited Git tracing/configuration, credential helpers or token env.
        env = {
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "LANG": "C.UTF-8",
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_COUNT": "0",
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_AUTHOR_NAME": "Toolbench preservation publisher",
            "GIT_COMMITTER_NAME": "Toolbench preservation publisher",
            "GIT_AUTHOR_EMAIL": "41898282+github-actions[bot]@users.noreply.github.com",
            "GIT_COMMITTER_EMAIL": "41898282+github-actions[bot]@users.noreply.github.com",
        }
        if write_token is not None:
            require(args[:2] == ("push", REMOTE), "Unexpected authenticated Git operation.")
            create = (len(args) == 3 and args[2] == CANDIDATE + ":refs/heads/" + REVIEW_BRANCH
                      and expected_remote == ZERO)
            delete = (len(args) == 3 and args[2] == ":refs/heads/" + TEMP_BRANCH
                      and bool(SHA.fullmatch(expected_remote or "")) and expected_remote != ZERO)
            require(create or delete, "Authenticated push is not an approved exact operation.")
            auth = base64.b64encode(("x-access-token:" + write_token).encode()).decode()
            env.update({
                "GIT_CONFIG_COUNT": "1",
                "GIT_CONFIG_KEY_0": "http.https://github.com/.extraheader",
                "GIT_CONFIG_VALUE_0": "AUTHORIZATION: basic " + auth,
            })
        else:
            require(expected_remote is None, "Unexpected push precondition on a read-only operation.")
        # The ephemeral hook contains public OIDs only, never authentication.
        with tempfile.TemporaryDirectory(prefix="toolbench-push-hook-") as hook_dir:
            hooks_path = "/dev/null"
            if write_token is not None:
                hook = Path(hook_dir) / "pre-push"
                hook.write_text(pre_push_hook(ZERO if delete else CANDIDATE, expected_remote,
                                              TEMP_BRANCH if delete else REVIEW_BRANCH, deletion=delete))
                hook.chmod(0o700)
                hooks_path = hook_dir
            result = subprocess.run(
                ["git", "-c", "core.hooksPath=" + hooks_path, "-c", "credential.helper=",
                 "-c", "http.followRedirects=false", "-c", "protocol.allow=never",
                 "-c", "protocol.file.allow=always", "-c", "protocol.https.allow=always", *args],
                cwd=self.cwd, env=env, input=data, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, timeout=60, check=False,
            )
        # Never emit raw subprocess output from a failed authenticated operation.
        require(result.returncode == 0, f"Git {args[0]} failed; stopped without retry.")
        return result.stdout

    def ref(self, repository, branch):
        allowed = {(SOURCE, "main"), (TARGET, "main"),
                   (TARGET, REVIEW_BRANCH), (TARGET, TEMP_BRANCH)}
        require((repository, branch) in allowed, "Ref read outside the exact allowlist.")
        url = f"https://api.github.com/repos/{repository}/git/ref/heads/{branch}"
        request = urllib.request.Request(url, headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "Toolbench-exact-history-publisher",
            "X-GitHub-Api-Version": "2022-11-28",
        }, method="GET")
        # All repositories are public. No credential is sent for API reads.
        opener = urllib.request.build_opener(NoRedirect())
        try:
            with opener.open(request, timeout=15) as response:
                require(response.status == 200, "Unexpected ref-read response.")
                data = response.read(100_001)
                require(len(data) <= 100_000, "Unexpectedly large ref response.")
                value = json.loads(data)
        except urllib.error.HTTPError as error:
            if error.code == 404:
                return None
            raise Stop(f"GitHub ref read failed with HTTP {error.code}; stopped.") from None
        require(value.get("ref") == "refs/heads/" + branch,
                "GitHub returned a different ref.")
        obj = value.get("object", {})
        require(obj.get("type") == "commit" and SHA.fullmatch(obj.get("sha", "")),
                "GitHub returned an invalid commit ref.")
        return obj["sha"]


def git_text(adapter, *args, **kwargs):
    return adapter.git(*args, **kwargs).decode().strip()


def validate_event(env):
    require(env.get("GITHUB_REPOSITORY") == TARGET, "Wrong repository.")
    require(env.get("GITHUB_EVENT_NAME") == "push", "Wrong event.")
    require(env.get("GITHUB_REF") == "refs/heads/" + TEMP_BRANCH, "Wrong temporary ref.")
    bootstrap = env.get("GITHUB_SHA", "")
    require(bool(SHA.fullmatch(bootstrap)), "Invalid bootstrap SHA.")
    require(bool(env.get("GITHUB_TOKEN")), "Missing job-scoped GitHub token.")
    return bootstrap


def remote_gates(adapter, expected_temp, expected_review=None):
    require(adapter.ref(SOURCE, "main") == SOURCE_MAIN, "Source main changed.")
    require(adapter.ref(TARGET, "main") == TARGET_MAIN, "Target main changed.")
    require(adapter.ref(TARGET, REVIEW_BRANCH) == expected_review, "Review branch changed or already exists.")
    require(adapter.ref(TARGET, TEMP_BRANCH) == expected_temp, "Temporary branch changed.")


def verify_payload(adapter, payload):
    bundle = payload / "accessproof-candidate.bundle"
    manifest_file = payload / "original-objects.json"
    require(hashlib.sha256(bundle.read_bytes()).hexdigest() == BUNDLE_HASH,
            "Bundle checksum mismatch.")
    manifest_bytes = manifest_file.read_bytes()
    require(hashlib.sha256(manifest_bytes).hexdigest() == MANIFEST_HASH,
            "Original-object manifest checksum mismatch.")
    manifest = json.loads(manifest_bytes)
    require(set(manifest) == {"accessproof", "toolbench"}, "Unexpected source manifest.")
    adapter.git("bundle", "verify", str(bundle.resolve()))
    adapter.git("fetch", "--no-tags", str(bundle.resolve()),
                "refs/heads/" + REVIEW_BRANCH + ":refs/remotes/preservation/candidate")
    require(git_text(adapter, "rev-parse", "refs/remotes/preservation/candidate") == CANDIDATE,
            "Candidate ref mismatch.")
    require(git_text(adapter, "rev-parse", CANDIDATE + "^{tree}") == CANDIDATE_TREE,
            "Candidate tree mismatch.")
    adapter.git("fsck", "--full", "--strict")
    for commit in [SOURCE_MAIN, TARGET_MAIN, "0e205f9141aabd77009db077aceead24b54c75c0"]:
        adapter.git("merge-base", "--is-ancestor", commit, CANDIDATE)
    require(git_text(adapter, "rev-list", "--count", SOURCE_MAIN) == "5",
            "Original source commit count mismatch.")
    counts = {}
    for repository, expected_count in [("accessproof", 52), ("toolbench", 15)]:
        objects = manifest[repository]["objects"]
        require(len(objects) == expected_count, "Original object count mismatch.")
        require(len({obj["oid"] for obj in objects}) == expected_count,
                "Duplicate original object entry.")
        for obj in objects:
            require(obj["kind"] in {"commit", "tree", "blob", "tag"}
                    and SHA.fullmatch(obj["oid"]), "Invalid original object entry.")
            data = adapter.git("cat-file", obj["kind"], obj["oid"])
            require(len(data) == obj["bytes"] and hashlib.sha256(data).hexdigest() == obj["sha256"],
                    "Original raw object mismatch.")
        counts[repository] = expected_count
    return counts


def publish_candidate(adapter, env, payload):
    bootstrap = validate_event(env)
    require(git_text(adapter, "rev-parse", "HEAD") == bootstrap, "Checkout is not event head.")
    require(git_text(adapter, "status", "--porcelain") == "", "Checkout is not clean.")
    counts = verify_payload(adapter, payload)
    remote_gates(adapter, bootstrap)
    # The trusted pre-push hook requires an all-zero advertised old OID, so this
    # can create only the absent review ref. Git also rejects a later ref race.
    adapter.git("push", REMOTE, CANDIDATE + ":refs/heads/" + REVIEW_BRANCH,
                write_token=env["GITHUB_TOKEN"], expected_remote=ZERO)
    # Failure, timeout or drift stops before cleanup; an unknown result is never
    # retried. The parent must inspect refs before deciding any recovery action.
    remote_gates(adapter, bootstrap, expected_review=CANDIDATE)
    # Delete only our exact unchanged bootstrap ref after verified publication.
    # Its advertised old OID and receive-pack's atomic check must both match.
    adapter.git("push", REMOTE, ":refs/heads/" + TEMP_BRANCH,
                write_token=env["GITHUB_TOKEN"], expected_remote=bootstrap)
    remote_gates(adapter, None, expected_review=CANDIDATE)
    return {
        "repository": TARGET, "temporary_branch": TEMP_BRANCH,
        "bootstrap": bootstrap, "candidate": CANDIDATE,
        "candidate_tree": CANDIDATE_TREE, "original_objects_verified": counts,
        "main_unchanged": True, "review_branch_created": True,
        "temporary_branch_deleted": True,
        "next_step": "Parent verifies exact candidate/main refs and creates one draft PR.",
    }


if __name__ == "__main__":
    try:
        receipt = publish_candidate(Adapter(Path.cwd()), os.environ, Path(__file__).resolve().parent)
        print(json.dumps(receipt, sort_keys=True))
    except (Stop, OSError, ValueError, KeyError, subprocess.TimeoutExpired,
            urllib.error.URLError) as error:
        # No raw exceptions from external services or subprocess stderr are logged.
        print("Publisher stopped: " + (str(error) if isinstance(error, Stop) else type(error).__name__))
        sys.exit(1)
