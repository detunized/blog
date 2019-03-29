---
title: "Telegram bot in Go: database"
date: 2019-03-29
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

Today I'm gonna add a database to my bot. As I mentioned in the [previous post]({{<ref "/posts/0022-go-telegram-bot-1.md">}}), I'm going to use SQLite to keep it simple and because the management turned down my budget request for Oracle on this project.

I quickly shopped around for an SQLite package for Go and found [go-sqlite3](https://github.com/mattn/go-sqlite3). This seems to be a very popular package. It allows me to use the standard `database/sql` package and it acts as a driver, which allows the Go database engine to talk to SQLite databases. So far so good. I'll use that then.

Since I'm writing everything in Go, I desperately need to use the goroutines somewhere. So the first thing I did was to move the reply functionality into a goroutine.

```go
for update := range updates {
    go reply(bot, update)
}
```

That should make things go **FAST**! Never mind the fact that Telegram will [not allow](https://core.telegram.org/bots/faq#my-bot-is-hitting-limits-how-do-i-avoid-this) frequent requests for any extended period of time. I've gotta try anyway.

To use the database I have to open it first. It's done like this:

```go
func openDatabase() *sql.DB {
    db, err := sql.Open("sqlite3", "./since.db")
    if err != nil {
        log.Panic(err)
    }

     _, err = db.Exec("CREATE TABLE IF NOT EXISTS events (" +
        "id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, " +
        "user INTEGER, " +
        "name TEXT, " +
        "date INTEGER);")

     if err != nil {
        log.Panic(err)
    }

     return db
}
```

I also create a table if it doesn't exist. Since I barely use SQL, I prefer to SCREAM, so people can hear me. And maybe the DB will get a [sense of urgency](https://stackoverflow.com/a/35684720/362938) and [process my queries faster](https://twitter.com/shipilev/status/703176579191410689).

Once the database successfully opened and no one panicked, it's time to start saving incoming events to it. I do it like this:

```go
func store(message *tgbotapi.Message, db *sql.DB) {
    _, err := db.Exec("INSERT INTO events (user, name, date) VALUES ($1, $2, $3);",
        message.From.ID,
        message.Text,
        message.Date)
    if err != nil {
        log.Panic(err)
    }
}

store(update.Message, db)
```

Now, every time I send a message to my bot it stores its content in the database. It's a start. The bot is still responding with the same reply as before. It's still really dumb. We'll get to make it smarter in the next day.

If you're curious, the code is [available on GitHub](https://github.com/detunized/since-bot/tree/day-2). This version is tagged `day-2`.
