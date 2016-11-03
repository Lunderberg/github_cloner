#!/usr/bin/env python3

from ensure_venv import ensure_venv
ensure_venv(requirements='requirements.txt')

import argparse
import itertools
import os

import github3
import git

def clone_all(usernames, output_dir):
    all_repos = itertools.chain(
        *[github3.iter_user_repos(username) for username in usernames])

    for repo in all_repos:
        repo_path = os.path.join(output_dir, repo.name)

        if not os.path.exists(repo_path):
            os.makedirs(repo_path)

        if not os.path.isdir(repo_path):
            raise RuntimeError('{} exists and is not a directory'.format(repo_path))

        # Find the repository, clone it if it does not exist
        try:
            working = git.Repo(repo_path)
        except git.InvalidGitRepositoryError:
            working = git.Repo.clone_from(repo.clone_url, repo_path, recursive=True)

        # Make sure that we're looking at something cloned from the right spot.
        if all(repo.clone_url not in remote.urls for remote in working.remotes):
            raise RuntimeError("{} exists, but doesn't point to {}".format(
                repo_path, repo.clone_url))

        # Pull from origin if working_dir is clean.
        # Fetch everything else
        for remote in working.remotes:
            if (remote.name=='origin' and
                not working.is_dirty()):
                remote.pull()
            else:
                remote.fetch()




def main():
    parser = argparse.ArgumentParser(description="Clone a github accounts repositories")
    parser.add_argument('-u','--user', dest='user', nargs='+',
                        type=str, required=True)
    parser.add_argument('-o','--output-directory', dest='dir', action='store',
                        type=str, required=True)
    args = parser.parse_args()

    clone_all(args.user, args.dir)

if __name__=='__main__':
    main()
