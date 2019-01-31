---
title: "Giving Go another chance: display command"
description: I'm writing a simple time tracking tool and rediscovering Go at the same time.
date: 2019-01-28
published: true
series:
    - Making a time tracking tool in Go
tags:
    - go
    - time tracking
    - cli
---

So far I got only to **C** in my CRUD application. It's time to move on to **R**. I wanted to display a list of entries in the log similar to what [timetrap](https://github.com/samg/timetrap) does:

```
Id  Day                Start      End        Duration   Notes
40  Sun Jan 20, 2019   22:00:00 - 01:00:00   3:00:00    initial setup
                                             3:00:00
41  Mon Jan 21, 2019   22:37:23 - 00:37:26   2:00:03    cli and cobra
                                             2:00:03
43  Tue Jan 22, 2019   11:40:14 - 12:01:56   0:21:42    tags
44                     12:02:08 - 12:34:00   0:31:52    parse tags from the comment
                                             0:53:34
48  Wed Jan 23, 2019   00:57:40 - 01:34:35   0:36:55    out command
49                     01:34:53 - 02:06:28   0:31:35    fix tag parsing
                                             1:08:30
59  Sat Jan 26, 2019   21:52:17 - 22:42:48   0:50:31    sqlite
60                     23:37:25 - 00:11:05   0:33:40    sqlite
                                             1:24:11
61  Sun Jan 27, 2019   15:12:51 - 15:29:04   0:16:13    sqlite
                                             0:16:13
62  Mon Jan 28, 2019   00:13:13 - 00:47:54   0:34:41    sqlite
63                     22:30:26 - 22:53:47   0:23:21    backend
64                     23:24:25 - 00:37:21   1:12:56    backend
                                             2:10:58
66  Tue Jan 29, 2019   11:19:19 - 11:20:36   0:01:17    display
67                     11:24:10 - 11:42:07   0:17:57    display
68                     11:51:51 - 11:52:53   0:01:02    display
69                     12:57:04 - 13:01:14   0:04:10    display
70                     13:10:37 - 14:03:54   0:53:17    display
71                     15:00:21 - 15:31:03   0:30:42    display
72                     21:11:52 - 21:16:23   0:04:31    display
73                     21:16:29 - 23:18:54   2:02:25    display
                                             3:55:21
74  Wed Jan 30, 2019   18:38:29 - 18:43:57   0:05:28    ids
75                     20:27:47 - 21:42:52   1:15:05    ids
                                             1:20:33
    -------------------------------------------------------
    Total                                   16:09:23
```

This, by the way, is how much time I've dedicated so far to this project. And all those tiny little bits of time I get to work on this between dealing with small kids, changing diapers, feeding them and putting out other fires at home. Talking about programmer productivity and [interruptions](https://heeris.id.au/2013/this-is-why-you-shouldnt-interrupt-a-programmer/).

This feature turned from a quick one into a time sucking endeavor. First the `Backend` interface had to be changed to support retrieval of completed and open entries.

```go
// Backend ...
type Backend interface {
    OpenEntry(comment string, startTime time.Time, tags []string) error
    CloseEntry(endTime time.Time) error

    GetEntries() ([]Entry, error)
    GetOpenEntry() (Entry, error)
}
```

Oh, the error handling! Why not just have `error` a part of **every** function in Go? I'll talk about this in a separate post. So far I could say I'm happy with the simplistic nature of Go. The only thing I'm suffering from so far is the error handling. `if err != nil { return err }`.

My database format now spans three different files. `entries.json` to store the entries themselves. `current.json` to store the currently open entry, which is later moved to `entries.json` once it's closed. And `id.json` which stores the last used index. I'm starting to regret the decision not to use SQLite, which would provide me with all that plumbing and free up some time to learn and google SQL queries. For now I'm also ignoring the problem of preventing two instances of the program trying to modify the database at the same time and turning it all into smoking rubble.

Briefly I tried to return a channel instead of an array of entries. I tried to be smart and find some use of Go channels in my program. Though it was a breeze to write, it was not really fitting into my usage patterns. So I decided to use simple arrays and worry about looking pro and hip later.

To display the entries I shopped around for a library again. And this, I think, is a really strong point of using Go. There's a library for anything. Even though C++ has been around for a lot longer, it's often impossible or really difficult to find libraries that do half of what Go libraries do. Writing a tool like this in C++ would be difficult. Anyhow, the library I found is called [tablewriter](https://github.com/olekukonko/tablewriter). It's pretty flexible and draws nice looking tables.

```bash
$ klk display --grep 'code|test'
+----+-------------+----------+----------+-----------------------------+-------------+
| ID |     DAY     |   TIME   | DURATION |           COMMENT           |    TAGS     |
+----+-------------+----------+----------+-----------------------------+-------------+
|  2 | 30 Jan 2019 | 21:34:17 |    15:14 | Writing tests               | #test       |
|  3 |             | 21:55:04 |    20:08 | Writing code                | #code       |
|  4 |             | 22:20:38 |    25:05 | Writing more code and tests | #code #test |
+----+-------------+----------+----------+-----------------------------+-------------+
|                     TOTAL   | 1:00:27  |
+----+-------------+----------+----------+-----------------------------+-------------+
```

I wasted a huge amount of time trying to make the report look nicer. In the process I figured out I'm not a good UI designer, even if it's just a basic text UI. I think I'll just copy what `timetrap` prints. For now this will do.

Now my application is almost 500 lines of code. That doesn't sound much, but it could already do the most basic time tracking. I'd say 90% of what I use in `timetrap`. Next step would be to worry about **U** and **D**. And more sophisticated tag filtering, the whole reason I started this.

One thing that worries me a little is the executable size. I'm at 11 megabytes now and the app doesn't do very much. When I tried SQLite, it was 16 MB. Sounds a bit excessive. I'll investigate later, but I think the most of the bulk is coming from Cobra. I might consider getting rid of, since I don't use any of the advanced features anyway.

---

Google searches that went into getting this to work:

- golang channel
- golang make empty channel
- golang close channel
- golang read from channel
- golang for range
- golang for range channel with index
- golang display table
- golang read line
- golang unmarshal string
- golang tostring
- golang create empty slice
- golang regexp flags
- golang int to string
- golang golang cannot define new methods on non-local type
- golang format duration
- golang init primitive type
- golang read text file as string
- golang sizeof
- golang sizeof int
- golang log fatal
- golang exit vs panic
- golang recover
- golang fallthrough case
- golang atexit

---

- Time spent: 5:15 minutes
- Total time spent: 16:15 hours
