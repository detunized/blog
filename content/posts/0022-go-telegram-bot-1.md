---
title: Telegram bot in Go
date: 2019-03-28
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

This is my fourth or fifth attempt to like Go. Kinda didn't work all the previous times. I blame myself, though. I believe I chose Go for the wrong types of projects. This time it's what's it was made to do. It's a backend application, it's deployed to a remote server, it's using concurrency and not too complex. It's a Telegram bot that helps me track random things.


## Idea

I want to be able to send simple commands to the chat and let the bot remember what happened and when. It's a bit like a log file. I want to be able to ask the bot when or how often something happened. This is what it could look like:

```
me: eat
bot: Recorded 'eat'. Last 'eat' happened 8 hours ago.

me: sleep, 10 hours ago
bot: Recorded 'sleep' at 23:15, yesterday.
     Last 'sleep' happened 1 day 12 hours ago.

me: /since run
bot: Last 'run' happened 2 days 15 hours ago.

me: /stats blog
bot: So far 'blog' happened 20 times, average
     time between events is 4 days 5 hours.
```

The questions and answers are a bit clumsy, but I don't think I'm going to implement the whole natural language processing thing here. It's a simple bot, remember? I have ideas for many more commands that could be useful, but I'll start small with recording and basic querying.


## Architecture

It's kind of a big word, eh? To talk to the Telegram servers I'm going to use [Go bindings for the Telegram Bot API](https://github.com/go-telegram-bot-api/telegram-bot-api). I'm planning on using webhooks in the final version. I'll start with the poll loop though since it's possible to run the polling bot locally.

I'm planning to use SQLite to store the data. I like zero configuration and setup. I like that I could just copy the database anywhere I want. This way I could organize backups very easily. For example, I could just email it to myself every now and then. Unless I open the bot to the world, I don't expect the database to grow much.

## Code

Let's jump straight to coding then. The Go Telegram Bot API provides a good [starting point](https://github.com/go-telegram-bot-api/telegram-bot-api/blob/master/README.md#example) in the README. It's an echo bot. It just sends the received text back to the user. I'll start with that.

For the bot to connect to the Telegram network it has to have a username and an API token. Both thing you could get by talking to a special bot on Telegram. The bot is called [The Botfather](https://t.me/BotFather).

![The Botfather](https://i.imgur.com/zQRcF0w.png)

The interaction is quite trivial and pleasant. Just follow the dialog and he'll give you what you need. Just make sure not to ask for too much.

![20 bots](https://i.imgur.com/eCAQ4q5.jpg)

The API token I got from the Botfather should be kept private. Who owns the token owns the bot. To keep it out of the repo I added a bit of code to read it from a simple JSON config. Besides that, it's just the code from the README.

```go
// Config represents the structure of the config.json file
type Config struct {
    Token string `json:"token"`
}

func readConfig() Config {
    file, err := os.Open("config.json")
    if err != nil {
        log.Panic(err)
    }

    defer file.Close()
    bytes, err := ioutil.ReadAll(file)
    if err != nil {
        log.Panic(err)
    }

    var config Config
    err = json.Unmarshal(bytes, &config)
    if err != nil {
        log.Panic(err)
    }

    return config
}
```

That should do it for day 1. If you're curious, the code is [available on GitHub](https://github.com/detunized/since-bot/tree/day-1). This version is tagged `day-1`.

*Also published on [DEV](https://dev.to/detunized/telegram-bot-in-go-3hd4) and [Medium](https://medium.com/@detunized/telegram-bot-in-go-9956786f60d0)*
