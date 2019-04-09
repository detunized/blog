---
title: "Telegram bot in Go: speak robot"
date: 2019-04-09
published: true
series:
    - Telegram bot in Go
tags:
    - go
    - telegram
    - bot
    - webdev
cover_image: https://i.imgur.com/Q9I9FU6.jpg
---

Last time I taught my bot to [speak human]({{<ref "/posts/0025-go-telegram-bot-4.md">}}). This time I'm gonna teach it to speak robot. I'm going to add a few bot commands. In Telegram the bots receive text exactly as you send it. By convention though, when the first word starts with a backslash (`/`) it's interpreted as a command. Commands are used to tell the bot what to do. It's a bit like shell, where you spend, I assume, most of your time.

The `go-telegram-bot-api/telegram-bot-api` package provides some functions to check whether there's a command in the received message and lets you extract it and its arguments.

```golang
for update := range updates {
    if update.Message.IsCommand() {
        command := update.Message.Command()
        arguments := update.Message.CommandArguments()
    }
}
```

After some light refactoring my bot is ready to accept commands as well as regular text. Actually, the plain text is simply mapped to the `/add` command.

```golang
if message.IsCommand() {
    switch command := message.Command(); command {
    case "a", "add":
        c.add(message.CommandArguments())
    case "e", "export":
        c.export()
    case "h", "help":
        c.help()
    case "s", "since":
        c.since(message.CommandArguments())
    case "t", "top":
        c.top()
    case "test":
        c.test()
    default:
        c.sendText(fmt.Sprintf("Eh? /%s?", command))
    }
} else {
    c.add(message.Text)
}
```


## /test

The simplest command would be `/test`, it just sends some hardcoded text back. It's pretty trivial to implement:

```golang
func (c context) test() {
    c.bot.Send(tgbotapi.NewMessage(c.message.Chat.ID, "It works"))
}
```

![test](https://i.imgur.com/mX4RFc8.png)


## /export

Export is a very important command. I consider it so important that I implemented it first. It allows the user to download all of its data stored in the bot's database. Say no to vendor lock-in.

This is really annoying these days. Take any app, like a fitness tracker app for example. It keeps track of your runs and stores your data somewhere on the phone or in the cloud. And one day it stops working or you decide to start using another app. And what do you do? How do you migrate your data? Usually, there's no easy way or no way at all. You'd have to abandon all of your history and your progress and start over in the new app.

I don't want that for my yet non-existent users. Let them take their data home whenever they want. That's why I have the `/export` command. Just say `/export` to the bot and it's happy to comply:

![export](https://i.imgur.com/pjPYAe1.png)

To generate the CSV file I use the built-in package `encoding/csv`. It's very easy to export all the rows into a CSV file :

```golang
buffer := &bytes.Buffer{}
csv := csv.NewWriter(buffer)

// For each row
for ... {
    csv.Write([]string{name, date})
}

// Flush when done (important!)
csv.Flush()

// Send
c.bot.Send(tgbotapi.NewDocumentUpload(
    c.message.Chat.ID,
    tgbotapi.FileBytes{
        Name:  "data.csv",
        Bytes: buffer.Bytes()}))
```

## /add and /since

The `/add` and the `/since` commands are bread and butter of this bot. As the names imply, one is for adding the events and the other is for checking when the event was last added. `/add` is a 2-in-1 command, like shampoo & conditioner in one bottle, it displays the time before adding.

![since-add](https://i.imgur.com/H2rHcY9.png)

## /top

To practice SQL, I added a relatively useless command to display 10 most logged events.

```sql
SELECT name, COUNT(name) freq FROM events
    WHERE user = <user-id>
    GROUP BY name
    ORDER BY freq DESC
    LIMIT 10
```

On my really dumb dataset it looks like this:

![top](https://i.imgur.com/sRNYKrk.png)

I have to say that I'm pretty impressed with SQL so far. I knew theoretically what it could do. But now I get to try it and it's really cool how I can just write a simple query instead of writing a bunch of code with loops and variables. Probably more efficient too.

## What's next

The bot is getting smarter. Now it could respond in different ways to a few basic commands. More is coming. I'd like the bot to be able to draw charts and show some statistics, like how often something happened or distribution throughout the day/week/month. Do *you* have any ideas?

![ideas](https://i.imgur.com/jR47I5p.png)

If you're curious, the code is [available on GitHub](https://github.com/detunized/since-bot/tree/day-5). This version is tagged `day-5`.
