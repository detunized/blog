---
title: "Giving Go another chance: more ambitious parsing"
description: I'm writing a simple time tracking tool and rediscovering Go at the same time.
date: 2019-01-23
published: true
series:
    - Making a time tracking tool in Go
tags:
    - go
    - time tracking
    - cli
---

Last time I was able to add some simple command line switches and it was easy. Now let's try something harder. First of all I'd like to be able to override the current time with a user specified one. I'd like to able to log a task at a specific time. Sometimes I'm so itching to get something done, that I forget about all those good habits I'm trying to acquire and start hacking right away. Later I realize that I forgot to log a task I'm working on. With [timetrap](https://github.com/samg/timetrap) it's quite easy to start a task 15 minutes ago instead of now:

```bash
$ timetrap in --at '15 min ago' 'Implementing --at parsing'
```

I'd like to be able to do exactly the same. I looked around and found a library with ungogleable name [when](https://github.com/olebedev/when). Actually, Go also is tough to google. I wonder if Google had to hack their algorithms to promote their language when people look for Go.

With some copying from the README and minor googling I was able to get it done in under 10 minutes. Not bad at all.

```go
import (
    "github.com/olebedev/when"
    "github.com/olebedev/when/rules/common"
    "github.com/olebedev/when/rules/en"
)

func parseAt(at string) time.Time {
    now := time.Now()
    if len(at) == 0 {
        return now
    }

    w := when.New(nil)
    w.Add(en.All...)
    w.Add(common.All...)

    parsed, err := w.Parse(at, now)
    if err != nil || parsed == nil {
        fmt.Printf("Don't know how to parse '%s'\n", at)
        os.Exit(1)
    }

    return parsed.Time
}
```

Next I wanted to add some tags with `--tag/-t`. The tricky thing is, I want to be able to repeat this flag many times, if I wanted to.

```bash
$ klk in -t coding -t tests "Writing some tests"
```

It turned out to be quite easy with Cobra. I didn't have to write much code for that. I compensated with a lot of googling, though.

```go
// Declare a variable
var tags []string

// Add a flag
inCmd.Flags().StringSliceVarP(&tags, "tag", "t", []string{}, "tags to use with this entry")
```

I could even do `-t 'tag1,tag2'` instead of `-t tag1 -t tag2` now. It's important to save keystrokes. No one wants to type when they don't have to, and I don't want people to abandon my software when they see how much they need to type.

This thing is really taking shape now. It's got custom timestamp and tags. It's already much better than Microsoft Project.

---

Google searches that went into getting this to work:

- go natural language date
- go check string empty
- go cobra repeated flag *(led to a lot of reading on Github)*
- golang strings

---

- Time spent: 20 minutes
- Total time spent: 5:35 hours
