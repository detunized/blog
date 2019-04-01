---
title: "Telegram bot in Go: concurrent SQLite"
date: 2019-04-01
published: true
series:
    - Telegram bot in Go
tags:
    - go
    - telegram
    - bot
    - webdev
cover_image: https://images.unsplash.com/photo-1527430253228-e93688616381
---

[Last time]({{<ref "/posts/0023-go-telegram-bot-2.md">}}) I added SQLite to my bot and at the same time I moved the request processing into a goroutine. Which means I introduced concurrent database access to my codebase.

Normally one should think, then do. Though not ideal, it's also possible to do it the other way around when you use `git`. But it's important not to forget to think at some point. Like I almost did and almost moved on to pile on more bugs on top of what I just introduced.

I remembered reading or watching something about SQLite the other day and they made it clear that I'd have to make sure not to access the database from multiple places at the same time. Go is made for concurrency, so I'm sure [go-sqlite3](https://github.com/mattn/go-sqlite3) I was using has it under control. Not exactly, as it turned out.

From the [FAQ](https://github.com/mattn/go-sqlite3#faq):

> Can I use this in multiple routines concurrently?
>
> Yes for readonly. But, No for writable. See [#50](https://github.com/mattn/go-sqlite3/issues/50), [#51](https://github.com/mattn/go-sqlite3/issues/51), [#209](https://github.com/mattn/go-sqlite3/issues/209), [#274](https://github.com/mattn/go-sqlite3/issues/274).

And just like that I went down the major rabbit hole. I searched and researched, googled and binged (no, not really), read the source of `go-sqlite3` and the docs for SQLite (which are pretty good by the way). All of that just to find myself in a situation that I don't know if I can trust the `go-sqlite3` package to handle my database work. Even though the FAQ states that write concurrency is not supported, I found contradicting statements. People were saying it's fine if I use multiple connections. But I wasn't going to open a new connection every time.

Long story short, I found a [blog post](https://crawshaw.io/blog/go-and-sqlite) which addressed exactly the same problem and offered a solution for it (and a couple of others) in a form of a [Go package](https://github.com/crawshaw/sqlite).

```shell
go get -u crawshaw.io/sqlite
```

According to David, the author of the post and the package, I should be able to trust this package to handle concurrency reliably. Now, I don't simply establish a connection to the database, but rather create an explicit pool of those of the size I desire (16 in this case):

```golang
import "crawshaw.io/sqlite/sqlitex"

func openDB() *sqlitex.Pool {
    db, err := sqlitex.Open("./since.db", 0, 16)
    if err != nil {
        log.Panic(err)
    }

    return db
}
```

Now, every time I want to access the database I have to get a connection from the pool and not to forget to put it back when I'm done. Getting a connection from the pool might block until a connection becomes available.

```golang
func execSQL(db *sqlitex.Pool, sql string) {
    connection := db.Get(nil)
    defer db.Put(connection)

    err := sqlitex.Exec(connection, sql, nil)
    if err != nil {
        log.Panic(err)
    }
}
```

A side note on the error handling. I currently do not handle errors on purpose to not slow myself down. But I don't ignore them either. Like any self-respecting software engineer I panic when I receive an error. For some errors, like not being able to open the database on startup, it's totally fine to panic. But if there was an error with one of the messages, panic is not such a good choice. It's like shutting down the server when we should have just returned HTTP/404.

Now, storing the incoming message in the database becomes this:

```golang
func store(message *tgbotapi.Message, db *sqlitex.Pool) {
    connection := db.Get(nil)
    defer db.Put(connection)

    err := sqlitex.Exec(
        connection,
        "INSERT INTO events (user, name, date) VALUES (?, ?, ?);",
        nil,
        message.From.ID,
        message.Text,
        message.Date)

    if err != nil {
        log.Panic(err)
    }
}
```

One small thing I don't like about this is that I'm forced to use positional SQL arguments if I want to use `sqlitex.Exec`. If I wanted to use the column names like `"... VALUES ($user, $name, $date)"`, I'd have to use a much wordier API. Prepare statement myself and then step through it. Like this:

```golang
func store(message *tgbotapi.Message, db *sqlitex.Pool) {
    connection := db.Get(nil)
    defer db.Put(connection)

    insert := connection.Prep("INSERT INTO events (user, name, date) VALUES ($user, $name, $date);")
    insert.SetInt64("$user", int64(message.From.ID))
    insert.SetText("$name", message.Text)
    insert.SetInt64("$date", int64(message.Date))

    _, err := insert.Step()
    if err != nil {
        log.Panic(err)
    }

    // Done with this query
    // TODO: Is it really needed? What happens when this isn't called?
    err = insert.Reset()
    if err != nil {
        log.Panic(err)
    }
}
```

If I see that positional arguments become a problem, I'll switch to this way of doing things.

As much as I wanted to make my bot less dumb this time, I only managed to switch libraries while trying to bullet-proof my SQLite access methods. Just refactoring, no features. Here's a typical day of a software engineer for you. Well, the next day then.

If you're curious, the code is [available on GitHub](https://github.com/detunized/since-bot/tree/day-3). This version is tagged `day-3`.

*Also published on [DEV](https://dev.to/detunized/telegram-bot-in-go-concurrent-sqlite-343i) and [Medium](https://medium.com/@detunized/telegram-bot-in-go-concurrent-sqlite-e6176fac088e)*
