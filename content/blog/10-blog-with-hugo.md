---
title: "Blog With Hugo"
date: 2019-02-02T14:25:41+01:00
draft: false
tags:
    - blog
    - hugo
    - netlify
---

I decided to resurrect my personal blog and not rely solely on [dev.to](https://dev.to/detunized) for my blogging needs. Though, it's really pleasant to use dev.to for technical blogging, some aspects of it could be better. I don't like so much to type all my posts in the browser and would rather use a proper text editor. I also don't like to switch between preview and markdown view all the time. And I especially don't like to have no version control for my content.

So far I've been just editing offline and pasting into the browser every 5 minutes to see what it looks like. When I'm done, I commit and then paste the final version and publish. When I find a typo, I fix, commit and publish again. I wanted to have a slightly different workflow.

I used to have a Jekyll blog and it was nice overall, but I had some gripes with it. I wanted to try something else. I was sure many new exciting tools came out while I wasn't looking. And after I looked... I was shocked and overwhelmed with choice. Hugo, Hexo, Gatsby, Next and more. There's even a dedicated [website](https://www.staticgen.com/) to track their GitHub stars, forks and other stuff. Wow!

And this is not it. I'd have to find a theme as well. Each of those projects has a theme shop or two. After browsing some of them and reading a bunch about what is better, easier, more powerful or what have you, I decided to go with Hugo and some theme I picked.

What was cool about Hugo, that it's a one stop shop. It processes everything, from Markdown down to the compiled minified resources for my site. No extra plugins needed. Installing it was super easy. Setting up the blog was even easier:

```shell
$ hugo new site blog
```

Done!

Adding a theme was not much more difficult:

```shell
$ hub clone Track3/hermit themes/hermit
```

Then I deployed that on [Netlify](https://netlify.com). And it was easy too. Just tell Netlify to use the GitHub repo and publish it with Hugo. Now when I push to GitHub, Netlify picks it up, builds it and it's live in under a minute. Amazing!

Can it be all sunshine and rainbows? Sure not. The shit started happening after that. First, I tried to fix myself some CSS. I'm not sure how we as humanity arrived to this technology. I guess, one wrong wrong turn here, another wrong turn there and now we're stuck with this mess. Have you ever tried to center a `div`?

![People who know how to center a div](https://i.imgur.com/sEOwTQo.jpg)

Luckily I didn't need to do that. But I wanted to fix some minor annoyances. I spent way too many hours on that, along with creating pull requests to the original theme and trying to fix the git repo on multiple occasions. Pro tip: use a new branch for each pull request.

Another major breakdown happened with Netlify not picking up my changes in the theme git submodule. I spent again way too many hours tracking this down. I even emailed the support, and they were very responsive and helpful, though they didn't really help with the actual problem. It wasn't obvious. After screwing around for few more hours I arrived at a solution: **put generated CSS into the repo and commit after each change**.

Apparently, Netlify [doesn't support Hugo pipelines](https://github.com/netlify/build-image/issues/182) at the moment. Which means the generated folder `resources` must be included in the repo as a workaround. Since the theme I picked had that in the repo, Hugo was just copying it to the `public` folder and was done with it, skipping all the SCSS processing on the server. Silly me, trying to fix that CSS.

If some poor soul is reading this and has the same problem: commit your top level `resources` folder into the repo.

[Criss](https://github.com/fool) from Netlify wrote to me that I can [join the beta](https://github.com/netlify/build-image/issues/254) and have my SCSS build on the server. I'm gonna give it a try a bit later. Now I want to enjoy stuff working for a little bit.

The preview of my new blog is [here](https://feed-dead-beef.netlify.com/). It's still got many problems and doesn't have a proper home yet. I also would like to merge it with my dormant [photo blog](https://detunized.net) before I make it public. There's always twice as much work still to do, no matter how much is done already.
