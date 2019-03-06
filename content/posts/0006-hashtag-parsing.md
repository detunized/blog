---
title: "Giving Go another chance: hashtag parsing"
description: I'm writing a simple time tracking tool and rediscovering Go at the same time.
date: 2019-01-25
published: true
series:
    - Making a time tracking tool in Go
tags:
    - go
    - time tracking
    - cli
---

Last time I added the `--tag/-t` flag. This time I'd like to add hashtag parsing. I'd like to simply mention tags in the comment and have to tool fish them out for me. For example:

```bash
$ klk in 'Writing some #tests to find a #bug'
```

My first impulse is to look for a library. And there is [one](https://github.com/gernest/mention) for exactly this purpose. But who wants to introduce a [left-pad timebomb](https://www.theregister.co.uk/2016/03/23/npm_left_pad_chaos/) into their own codebase? *(Answer: almost anybody).* I'd rather reinvent the wheel and [solve the problem with a regex](https://blog.codinghorror.com/regular-expressions-now-you-have-two-problems/). Two problems are better than one.

Go has the `regexp` package in its standard library just for this purpose. So it's really a two-liner:

```go
func extractTags(text string) []string {
    re := regexp.MustCompile("#\\S+")
    // TODO: Strip out #
    return re.FindAllString(text, -1)
}
```

Notice a TODO? That one of those cases where you'd have to take a dive from Python heights into C depths and roll you own loop. The two-liner becomes a six-liner. This where I start missing Ruby, Python, C#, Scala, Kotlin, hell, even C++.

```go
func extractTags(comment string) []string {
    re := regexp.MustCompile("#\\S+")
    tags := re.FindAllString(comment, -1)

    // Strip #s
    for i, tag := range tags {
        tags[i] = strings.TrimLeft(tag, "#")
    }

    return tags
}
```

Done with C? Back to Python. Now we have to join tags that come from the `--tag` switch with the ones we fished out from the comment. That is surprisingly easy:

```go
tags := append(tagFlag, extractTags(comment)...)
```

As was promised earlier, we have another problem now. Tags duplicate when the same tag comes from different places or when the same tag mentioned more than once. That should be quick to fix with in a language with such an amazing runtime, right? No, not really. One of the solutions would be to create a map and put all the tags in it, then iterate over its keys and put them into an array.

```go
tagSet := map[string]bool{}

for _, tag := range tags {
    tagSet[tag] = true
}

uniqueTags := []string{}
for tag := range tagSet {
    uniqueTags = append(uniqueTags, tag)
}
```

Compare to Ruby:

```ruby
uniqueTags = tags.uniq
```

Anywho, the final code looks like this:

```go
func getTags(comment string) []string {
    tags := map[string]bool{}

    // Add all flags from --tag
    for _, tag := range tagFlag {
        tags[tag] = true
    }

    // Add all flags from #tag
    for _, tag := range extractTags(comment) {
        tags[tag] = true
    }

    // Deduplicate
    uniqueTags := []string{}
    for tag := range tags {
        uniqueTags = append(uniqueTags, tag)
    }

    return uniqueTags
}
```

After all this hard work I can write this in the terminal:

```bash
$ klk in --at '15 min ago' --tag coding "Writing some #tests"
Adding an entry: Writing some #tests at Fri Jan 25 01:53:05 CET 2019 with tags #coding #tests
```

The dream time tracking tool is coming along. And I'm relearning myself some C loops. Double win!

---

Google searches that went into getting this to work:

- golang tag parser
- golang hashtag parser
- go regex
- golang map
- golang unique slice of strings
- golang merge slices unique
- golang merge slices
- golang set
- golang map keys as slice
- golang map get keys as slice
- go for
- go foreach
- go for range modify
- go for range update

---

- Time spent: 1 hour
- Total time spent: 6:35 hours
