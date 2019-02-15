---
title: "Git-Fu: merge multiple repos with linear history"
date: 2019-02-15
published: true
tags:
    - git
    - madness
    - reinventing the wheel
---

The other day I invented myself a new headache: I wanted to merge a few libraries I've built over the years into one repo and refactor them together. It looks simple at first glance, copy all the files into subfolders, add and commit:

```shell
$ git add .
$ git commit -m 'All together now!'
```

Done!

No, not really. This would eliminate the history. And I really wanted to keep it. I often go back to see what changes have been made to a file, I use blame to see when and why certain code was modified. I looked around to see how to get it done quickly. I found a whole bunch blog posts describing similar undertakings. I also found code snippets, shell and Python scripts and even Java programs to do just that.

After trying some of those (not the Java though, no thank you) I realized they don't do exactly what I want. Some of the authors tried to keep the original commit hashes. Some authors wanted to have the original file paths. I wanted to be able to track changes from the beginning of the history.

Most of the approaches I found were not compatible with my goals. Usually people try to import a repo into a branch (usually by adding a `remote` from another repo), move all the files into a subfolder in one commit and then merge that branch into `master`. This creates one big commit where all the files get moved to a subfolder. And then another giant merge commit, where all the changes from one branch get copied to another branch. When you view such a repo on GitHub, you'd see that file history gets broken (`blame` still works though).

I also discovered a built-in built-in command `git subtree` and it turns out it suffers from the same problems as all the third party tools I tried before that. So no go! Need to reinvent the wheel here and come up with my own solution.

So, basically, I needed to find a way to merge all the repos without creating any merge commits. And I need to move the original files into subfolders. Tho Git tools come to mind: `cherry-pick` and `filter-branch`.

A sidenote. I used use Mercurial at work a few years back and it was great! The user experience on Mercurial is amazing. I kinda wish it didn't die a slow death and let the inferior product to take over the dev scene. As Mercurial was intuitive and user friendly as Git is powerful and versatile. Git is like a really twisted Lego set: you can build whatever you want out of it.

So here's the plan:

- put each repo in its own branch
- rewrite the history to move all the files in each commit into a subfolder
- rewrite the history to prepend the repo name to the commit message
- cherry pick all the commits from all the branches in chronological order into `master`
- delete branches
- garbage collect to shrink the repo

Easy peasy. Feel kinda masochistic today, so let's do in Bash.

First, like always we need to make sure the whole script fails when any of the commands fails. This usually saves a lot of time when something goes wrong. And it usually does.

```bash
#!/bin/bash
set -euo pipefail
```

List of repos I'd like to join:

```bash
repos="1password bitwarden dashlane lastpass opvault passwordbox roboform stickypassword truekey zoho-vault"
```

Make sure we start form scratch:

```bash
rm -rf joined
git init joined
cd joined
```

Now, here's a tough one:

```bash
for repo in $repos; do
    git remote add $repo $REPO_DIR/repo
    git fetch $repo
    git checkout -b $repo $repo/master
    echo -n "$repo: " > prefix
    git filter-branch \
        -f \
        --tree-filter "mkdir -p .original/$repo && rsync -a --remove-source-files ./ .original/$repo/" \
        --msg-filter "cat $(pwd)/prefix -" \
        --env-filter 'GIT_COMMITTER_DATE="$GIT_AUTHOR_DATE"' \
        $repo
    rm prefix
done
```

Let's go over it piece by piece. First, I import a repo into its own branch. `lastpass` repo would end up in a branch named `lastpass`. Nothing difficult so far.

```bash
git remote add $repo $REPO_DIR/repo
git fetch $repo
git checkout -b $repo $repo/master
```

In the next step I rewrite the history for each repo to move files into a subfolder for each commit. For example, all the files coming from the repo `lastpass` would end up in the `.original/lastpass/` folder. And it would be changed for all the commits in the history, like all the development was done inside this folder and not at the root.

```bash
git filter-branch \
    -f \
    --tree-filter "mkdir -p .original/$repo && rsync -a --remove-source-files ./ .original/$repo/" \
    --msg-filter "cat $(pwd)/prefix -" \
    --env-filter 'GIT_COMMITTER_DATE="$GIT_AUTHOR_DATE"' \
    $repo
```

The `filter-branch` command is a multifunctional beast. It's possible to change the repo beyond any recognition with all the possible switches it provides. It's possible to FUBAR it too. Actually it's super easy. That's why it creates a backup under `refs/original/refs/heads` branch. To force the the backup to be overwritten if it's already there I specify `-f`.

When the `--tree-filter` switch is used, every commit is checked out to a temporary directory and using regular file operations I can rewrite the commit. So for every commit, I create a directory `.original/$repo` and move all the file into it using `rsync`.

The `--mag-filter` switch allows me to rewrite the commit message. I'd like to add the repo name to the message. So that all the commits that are coming from the `lastpass` repo would look like `lastpass: original commit message`. For each commit the script would receive the commit message on `stdin` and whatever comes out to `stdout` would become the new commit message. In this case I use `cat` to join `prefix` and `stdin`(`-`). For some reason I couldn't figure out why simple `echo -n` wouldn't work, so I had to save the message prefix into a file.

And the last bit with `--env-filter` is needed to reset the commit date to the original date (author date in Git terminology). If I didn't do, Git would change the timestamp to the current time. I didn't want that.

Next step would be to copy all those commits to the `master` branch to flatten the history. There's no `master` branch yet. Let's make one. For some reason Git creates a branch with all the files added to the index. Kill them with `git rm`.

```bash
git checkout --orphan master
git rm -rf .
```

To copy the commits, I need to list them first. That is done with the `log` command:

```bash
git log --pretty='%H' --author-date-order --reverse $repos
```

This command produces a list of all the commit hashes sorted from the oldest to newest across all the branches I created earlier. The output of this step looks like this:

```
7d62b1272b4aa37f07eb91bbf46a33609d80155f
a8673683cb13a2040299dcb9c98a6f1fcb110dbd
f3876d3a4900e7f6012efeb0cc06db241b0540d6
7209ecf519475e59494504ca2a75e36ad9ea6ebe
```

Now that I have the list, I iterate and `cherry-pick` each commit into `master`:

```bash
for i in $(git log --pretty='%H' --author-date-order --reverse $repos); do
    GIT_COMMITTER_DATE=$(git log -1 --pretty='%at' $i) \
        git cherry-pick $i
done
```

The `GIT_COMMITTER_DATE` environment variable is again used to reset the commit date to the original creation time, which I get with the `log` command again like this:

```bash
git log -1 --pretty='%at' <COMMIT-HASH>
```

After these steps I have a repo with flat history, where each original repo lives in its own subdirectory under `.original/`. I can use GitHub file history and blame to see all the changes that happened to the original files since their birth. And since Git tracks renames I could just move these files to their new home inside the megarepo and I would still get the history and blame working.

The only thing left to do is to clean up the repo, delete all the branches I don't need anymore and run the garbage collector to take out the trash.

```bash
for repo in $repos; do
    git branch -D $repo
    git remote remove $repo
    git update-ref -d refs/original/refs/heads/$repo
done

git gc --aggressive
```

The resulting repo lives [here](https://github.com/detunized/password-manager-access). I feel like it was worth the time I put into that. It gave me an opportunity to learn more about the Git low level commands. And now I have a repo that I can browse with ease and don't need to jump between the branches every time I want to check some file history.

The script I used could be found [here](https://gist.github.com/detunized/7c41718863ab94e7072f99a55a5bf9d4).
