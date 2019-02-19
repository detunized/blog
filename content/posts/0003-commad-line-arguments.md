---
title: "Giving Go another chance: command line arguments"
description: I'm writing a simple time tracking tool and rediscovering Go at the same time.
date: 2019-01-21
published: true
series:
    - Making a time tracking tool in Go
tags:
    - go
    - time tracking
---

To make a usable command line tool one has to parse the arguments first. I shopped around for a command line parsing library and found [cli](https://github.com/urfave/cli) and [cobra](https://github.com/spf13/cobra). I tried cli briefly and then switched to cobra. You gotta go with the stars, Github stars. Cobra's got more of them.

Cobra comes with a cogeden tool which is nice, I guess. Since I'm still shaky with even basic Go concepts, I decided to run and not type up everything from scratch.

```bash
$ ~/go/bin/cobra init klk
Your Cobra application is ready at
/Users/detunized/go/src/klk
```

Why? I ran it in a different folder. And then I have a flashback and I realize why I had that bitter taste in my mouth the last time I used go. It's the `$GOPATH` thing. No other language I know does anything like it. Apparently I cannot have my code where I want it. It has to be where Rob Pike wants it. Okay, I thought to myself, I can just copy the generated files to where I want them and I'm done. And I did.

Cobra provides a way to add a new command with the codegen tool like this:

```bash
$ ~/go/bin/cobra add in
in created at /Users/detunized/go/src/klk/cmd/in.go
```

This adds the subcommand called `in`. To be used like this: `klk in`. So far so good. I copied the newly created file to my repo and kept poking around, editing, running, see what my changes do. And then I had a first WTF moment. I change some files, but Go doesn't pick up the changes and it seems like it runs the old executable. I spent lots of time trying to figure out why the build silently fails and I don't see any error messages. And then it hit me: it keeps building some of the files from the `$GOPATH` and some from my project folder. So copying files from the default place to an external folder is not really an option.

Mmkay. But I still wanted my files in my project folder. Let's see if symlinking my folder into `$GOPATH/src` would trick the compiler:

```bash
$ ln -s `pwd` /Users/detunized/go/src/klk
```

So far it's working and I'm able to use `cobra` tool and the compiler is happy. But let's finally get to coding next time. This time it didn't happen.

---

Google searches that went into getting this to work:

- go cli
- go cli parser
- go cli vs cobra
- cobra Error: Rel: can't make relative to
- gopath
- gopath vs goroot
- go package init
- go build without gopath
- no gopath
- vgo

---

- Time spent: 2 hours
- Total time spent: 5 hours
