---
title: "Git-Fu: reposurgeon"
date: 2019-02-17
published: true
tags:
    - git
    - madness
    - failure
    - reposurgeon
---

In a [comment](https://dev.to/610yesnolovely/comment/8nk8) to my previous [post]({{< ref "/posts/12-git-fu-merge-multiple-repos-with-linear-history.md" >}}) [@610yesnolovely](https://dev.to/610yesnolovely) mentioned a tool called [reposurgeon](https://gitlab.com/esr/reposurgeon) that is supposed to take care of the exact problem I had (merging a bunch of Git repos). I installed it and tried it out. I won't keep you in suspense here, it didn't work for me.

I spent a bunch of time going through the giant [documentation page](http://www.catb.org/~esr/reposurgeon/reposurgeon.html), which seems to be both detailed and vague at the same time. It feels too formal and yet doesn't give you a good idea what the whole thing is about. There's a lot of terminology that is unique to this tool and not a lot of introduction into the lingo. There are very few examples of anything. No quick start section with trivial cases covered. Quite difficult to figure out where to start. I also didn't find a lot of resources online. Hardly any, actually. Not many people seem to use this tool.

I'm sure reposurgeon is a beast. It seems to have more commands and switches than `git`, `openssl` and [`mogrify`](https://imagemagick.org/script/mogrify.php) combined. It has a query language that makes Oracle green with envy. But for the life of me, I couldn't figure out how to use any of it. It's just not intuitive at all. Some commands are pretty arbitrary, like `append`, that lets you append text to the commit message. Yet, there's no `prepend`.

The query language is quite obscure and doesn't resemble anything I'm familiar with. Here's an example from the docs:

```
define lastchange {
    @max(=B & [/ChangeLog/] & /{0}/B)? list
}
```

And the description:

> List the last commit that refers to a ChangeLog file containing a specified string. (The trick here is that ? extends the singleton set consisting of the last eligible ChangeLog blob to its set of referring commits, and listonly notices the commits.)

That makes zero sense to me, though I've spent quite a bit of time trying to understand the docs.

To me this looks like a well run project. It seems to have good [pace of releases](http://www.catb.org/~esr/reposurgeon/NEWS), vast and detailed [documentation](http://www.catb.org/esr/reposurgeon/), clean and documented source code (I wouldn't put everything in [one 21k line file](https://gitlab.com/esr/reposurgeon/blob/master/src/goreposurgeon/goreposurgeon.go) though).

What I think went wrong is that it's got too many very specific features and it tries to handle everything. Probably the author(s) have been spending too much time in their silo perfecting and adding features to their software.

I think they should have been spending more time on Stack Overflow answering questions about reposurgeon, writing introduction to the tool and blogging about it. I understand this tool is pretty niche and is designed for some very special use cases, but that should not mean "experts only". A casual user should not be intimidated by the advanced features right away. It should be possble to do a trivial conversion with some minimal command set.

Look at Git. I know it's a train wreck of a user experience. It's got commands for everything. Mastering Git could take a lifetime. But if you stick to `pull-add-commit-push` workflow, it's not that bad. Powerful, shouldn't mean unapproachable.
