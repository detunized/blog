---
title: "Telegram bot in Go: speak human"
date: 2019-04-04
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

[Last time]({{<ref "/posts/0024-go-telegram-bot-3.md">}}) I was bulletproofing my SQLite access foundation. Let's see if it holds in production. Too bad I'm never gonna get that high load that is supposed to break things. Oh well, let's wait and see. Maybe I get lucky and two sad concurrent requests would eventually make my Go binary panic.

Today, I'm going to focus on features. I'd like to make my bot *intelligent*. Not really AI like, rather just sounding a bit better than `cmd.exe` when you type in a wrong command. I'm not gonna make anything big, more like dipping the toe in the water to see how it is.

First, I'd like to find the last event with the same name, since I'm storing them in the database, and send back the date the event. Imagine the interaction like this:

```
me: eat
bot: Previous 'eat' happened 6 hours ago
```

To find the event with the same name I have to ask SQLite to give me the row where the user is the same, the name of the event it the same and I want the last row after it's sorted by date. Converting English to SQL I get:

```sql
SELECT date FROM events
    WHERE user = ? AND name = ?
    ORDER BY date
    DESC LIMIT 1
```

Pretty simple, eh? Now, converting this to Go and `crawshaw.io/sqlite` I get the following:

```golang
// Default response
response := fmt.Sprintf("Fist time for '%s'", name)

// Get the last event with the same name and format the response
err := sqlitex.Exec(connection,
    "SELECT date FROM events "+
        "WHERE user = ? AND name = ? "+
        "ORDER BY date "+
        "DESC LIMIT 1",
    func(s *sqlite.Stmt) error {
        response = formatResponse(s.GetInt64("date"), name)
        return nil
    },
    message.From.ID,
    name)

// Send the message back to the user
go func() {
    bot.Send(tgbotapi.NewMessage(message.Chat.ID, response))
}()
```

Where `formatResponse` is very rudimentary:

```golang
func formatResponse(date int64, name string) string {
    last := time.Unix(date, 0)
    return fmt.Sprintf("Previous '%s' happened on '%v'", name, last)
}
```

Now the interaction looks like this:

![since-bot-1](https://i.imgur.com/mqD0QVf.png)

Not exactly the smartest bot on the planet, but we're going somewhere.

Now, I would like to make it sound a bit less dumb and bit more human, which are not always going together. In this case, they are. I don't want the bot to say things like `happened on '2019-04-04 14:13:57 +0200 CEST'`, but rather something like `8 minutes since` or `1 year since`. Believe it or not, but there's a package for exactly that. Welcome [hako/durafmt](https://github.com/hako/durafmt). With its help it's very easy to turn the conversation into something like this:

![since-bot-2](https://i.imgur.com/1SBahPw.png)

It is much more readable. To make it work I just had to modify the `formatResponse` function a bit (now it also has to take the current message date):

```golang
func formatResponse(name string, date int64, prevDate int64) string {
    prev := time.Unix(prevDate, 0)
    now := time.Unix(date, 0)
    duration := durafmt.ParseShort(now.Sub(prev))
    return fmt.Sprintf("%s since last '%s'", duration, name)
}
```

Easy peasy. With not so many lines and in under an hour of work I have a bot that speaks human and can tell me when something happened the last time. Ship it! 🚢

If you're curious, the code is [available on GitHub](https://github.com/detunized/since-bot/tree/day-4). This version is tagged `day-4`.
