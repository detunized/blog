---
title: "Fuzzy search and download files with rsync in the terminal"
date: 2019-03-01
published: true
tags:
    - bash
    - terminal
    - fzf
    - cli
---

I use `rsync` **a lot**. I use it to copy files to USB drives, to VMs or Docker containers, to share files between computers at home, to backup stuff to remote machines or simply copy to the local Dropbox folder. And most of the time I download files from a couple of remote folders to my computer.

I do all my file operations in the terminal. I find this faster and more convenient than clicking in the GUI file manager of some sort. Actually I'm so clumsy with those that I usually end up moving something important somewhere where it doesn't belong. Many, many years ago, when I was a young junior developer on my first job, I moved an important project on a network share to a sibling folder. All I wanted to do is to put a mouse on the other side of the keyboard and I grabbed it with my left hand. Oh, that was a major disaster: people were running around looking for the project folder, thought we are being hacked. I found it 10 minutes later.

Not to repeat those grave mistakes of the past, I simply stick to the command line these days. The problem with the command line though, is that it's not very visual. Especially when it comes to remote systems. Local file completion in `zsh` is pretty good. And once paired with a fuzzy matcher like [`fzf`](https://github.com/junegunn/fzf), it becomes a pleasure to do almost any file operations in the terminal.

For a few years I relied on `zsh` remote path autocompletion for `rsync`. It works almost as good as it does for the local files. Just type some characters, press TAB and it autocompletes the filename for you. If the name is ambiguous a list of matches would pop up where you can select a name with the arrow keys. A pretty standard shell experience.

There's a problem though. Since it's a remote system, it takes a second or two to autocomplete. It's annoying. Plus it only autocompletes in the current directory and I would have to press TAB many times before I get the full path. And I can only download one file or folder at a time. Here's a demo. It's painful to watch how slow it is:

[![asciicast](https://asciinema.org/a/EIc6s9XzvncvUAl7DYgVuWLvp.svg)](https://asciinema.org/a/EIc6s9XzvncvUAl7DYgVuWLvp?autoplay=1)

Where's problem, there must be a solution. And how it usually happens with the command line, the solution is a Bash script:

```bash
#!/bin/bash
set -eo pipefail

HOST=${DL_HOST:-dev.somehost.to}
DIR=${DL_DIR:-files}

if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    echo "USAGE: dl [dir [host]]"
    exit
fi;

if [[ "$1" != "" ]]; then
    DIR="$1"

    if [[ "$2" != "" ]]; then
        HOST="$2"
    fi
fi;

REMOTE="$HOST:$DIR/"

rsync -a "$REMOTE" \
    | ruby -ne 'puts $_.split(/\s+/, 5).last' \
    | fzf -m --height 50% \
    | rsync -avP --no-relative --files-from - "$REMOTE" .
```

It works like this:

[![asciicast](https://asciinema.org/a/BwmSUZ7lK0mCk9Ot7797QNqQv.svg)](https://asciinema.org/a/BwmSUZ7lK0mCk9Ot7797QNqQv?autoplay=1)

First it uses `rsync` to list all the files in the remote folder in the format similar to `ls -l`:

```
drwxr-xr-x          4,096 2019/03/01 23:23:25 src
-rw-r--r--            261 2019/02/20 23:11:49 src/PasswordManagerAccess.csproj
drwxr-xr-x          4,096 2019/03/01 23:23:25 src/Common
-rw-r--r--            379 2019/02/20 23:11:49 src/Common/BaseException.cs
-rw-r--r--            906 2019/03/01 23:23:25 src/Common/ClientException.cs
-rw-r--r--          3,454 2019/03/01 23:23:25 src/Common/Crypto.cs
-rw-r--r--            241 2019/02/20 23:11:49 src/Common/ExposeInternals.cs
-rw-r--r--          6,868 2019/03/01 23:23:25 src/Common/Extensions.cs
-rw-r--r--          1,178 2019/02/20 23:11:49 src/Common/HttpClient.cs
-rw-r--r--            487 2019/02/20 23:11:49 src/Common/IHttpClient.cs
-rw-r--r--          7,267 2019/02/20 23:11:49 src/Common/JsonHttpClient.cs
...
```

That gets piped into an inline Ruby script that extracts the 5th column and all the spaces it might have. And the result of that goes into `fzf` for interactive selection. Once finished, that is now finally piped into another instance of `rsync`, which is receiving a list of files on the standard input (`--files-from -`). Pretty cool. The added benefit: now I can pick multiple files easily.

The script takes the remote folder name and the host optionally from the command line parameters or the environment variables. The most commonly used path I decided to hardcode to push back my RSI by a couple of years.
