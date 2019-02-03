---
title: "Giving Go another chance: easy parameter parsing"
description: I'm writing a simple time tracking tool and rediscovering Go at the same time.
date: 2019-01-22
published: true
series:
    - Making a time tracking tool in Go
tags:
    - go
    - time tracking
    - cli
---

It's good to start with something easy. I already have a command `klk in`, now it would be good to pass some switches and arguments to it. Cobra has a huge [readme](https://github.com/spf13/cobra/blob/master/README.md), but I found that it was easier to check their own command line tool source for examples.

```go
var inCmd = &cobra.Command{
    Use:     "in [comment]",
    Aliases: []string{"i"},
    Short:   "Clock in an entry",
    Run: func(cmd *cobra.Command, args []string) {
        comment := strings.Join(args, " ")
        timestamp := time.Now()
        fmt.Println("Adding an entry:", comment, "at", timestamp.Format(time.UnixDate))
    },
}
```

I had to figure out how to join strings and how to custom format a date. The default date format is somewhat weird. I'm guessing its following the Go path (GOPATH?) on it's journey into the weird. Who wants the date printed like this by default? What's `m=+0.001801899`?

```bash
2019-01-23 12:04:12.760058 +0100 CET m=+0.001801899
```

Outside of this it was quite easy. Overall Go feels like C with some Python sprinkled on top of it. The problem is, you never know when you have to drop from Python to C and try not to bang your head in the process.

Now let's add a switch. The easiest I could think of is `--quiet/-q`. It's just one line with Cobra:

```go
inCmd.Flags().BoolVarP(&quiet, "quiet", "q", false, "be quiet and don't print so much stuff")
```

The final product works like this now:

```bash
$ klk in some work
Adding an entry: some work at Wed Jan 23 12:16:20 CET 2019
```

or

```bash
$ klk in -q some work
```

Ship it! 🚢

---

Google searches that went into getting this to work:

- go join strings
- go time now
- go format date

---

- Time spent: 15 minutes
- Total time spent: 5:15 hours
