---
title: "Giving Go another chance: setting everything up"
description: I'm writing a simple time tracking tool and rediscovering Go at the same time.
date: 2019-01-20
published: true
series:
    - Making a time tracking tool in Go
tags:
    - go
    - time tracking
    - vscode
---

First things first: I need to be able to build and run Go programs. I'm using
macOS, so installing Go was very quick:

```bash
$ brew install go
```

Seems to work:

```bash
$ go version
go version go1.11.4 darwin/amd64
```

Now I need to hook it up with my editor. I'd like to have at least some basic features, like format code on save and build and run from the editor. Normally I use Sublime Text 3, but after quickly checking the [installation instructions](https://margo.sh/b/hello-margo/) I decided to rather try Visual Studio Code where I can set everything up with one click.

It's been laying around on my hard drive for a while now and now I finally have an excuse to try it out. So, not only a new language, a new editor as well. Yay!

Setting up the extension took just a couple of minutes, it was quick and absolutely painless. Making the editor format the code on save, on the other hand, was a whole different story. It took me a really long time fiddling with the settings, googling, reading [relevant issues](https://github.com/Microsoft/vscode-go/issues/1419) on Github and so on. VS Code was very helpful most of the time, installing relevant tools, highlighting errors in my config and so forth. The only thing it refused to do is to format my code on save.

It seems I've tried everything and I just gave up and went to bed. As it turned out next morning, all it needed is a restart. How dumb of me. I guess it's that my never dying faith in software and that developers for once will get it right. No such luck this time. At least Windows 95 was honest about this. VS Code makes it look like no restart is needed and everything is kinda working but not 100%. More like 93.76%.

In the end I have it all working: format on save, build, go to definition and even full blown IntelliSense, that autocompletes almost everything for me. Nice!

Let's get to coding next time.

---

This is how much I rely on Google these days to get this little bit of work done:

- go tutorial
- homebrew install golang
- goimports
- goreturns
- goformat
- vscode go fmt on save
- vscode go format on save not working
- go vet
- go build release

---

- Time spent: 3 hours
- Total time spent: 3 hours
