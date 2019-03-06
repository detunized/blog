---
title: "Giving Go another chance: backend"
description: I'm writing a simple time tracking tool and rediscovering Go at the same time.
date: 2019-01-27
published: true
series:
    - Making a time tracking tool in Go
tags:
    - go
    - time tracking
    - cli
---

This time I was ready to do some serious enterprise level work with abstract interfaces and factories. I wanted to finally store the log entries I could create with `in` and `out` commands. After some researching and screwing around with [go-sqlite3](https://github.com/mattn/go-sqlite3) for a bit, I decided not to mess with the database at the moment. I'm not *that* enterprise ready yet. As much as I admire the engineering effort behind SQLite and the idea of *everything-in-one-single-file* storage, I don't really want to have a binary blob anywhere in my `~`. For now at least.

I though it would be a good start to store the entries in a simple text file, where each line is a JSON object. I started using this format a long time ago as I find it a much better alternative to a giant JSON array.

Consider JSON-per-line:

```json
{"id": 0, "comment": "writing tests", "tags":[]}
{"id": 1, "comment": "writing more tests", "tags":[]}
```

vs. regular JSON:

```json
[
    {"id": 0, "comment": "writing tests", "tags":[]},
    {"id": 1, "comment": "writing more tests", "tags":[]}
]
```

Yes, it's possible to load the regular JSON file with one line of code and it's nice. But generating those files is painful. You'd have to worry about surrounding `[]` and trailing commas on every line but the last one. Where the *JSON-per-line* format is much simpler. Just append a line with a JSON object and you're done. Usually parsing is faster too. Probably due to some non-linearities in JSON parsing or reallocation. Basically, it's faster to parse a million small JSON objects than a single JSON array with a million entries.

It would be totally unprofessional of me to write any functions and call them directly. I'd need an interface first. After some googling and fighting with squiggly red and green lines in VS Code I was able to write my first interface in Go.

```go
// Backend ...
type Backend interface {
    OpenEntry(comment string, startTime time.Time, tags []string) error
    CloseEntry(endTime time.Time) error
}
```

Notice the `// Backend ...` comment. It's there for a reason. It makes the linter happy, as I don't want to have green squigglies everywhere. Apparently the linter is not happy about the exported type without a comment. The type is exported if it starts with a capital letter, by the way. Some interesting design decision.

In Go anything that implements these two functions is considered a backend. No explicit interface implementation is needed. Neat and scary. So the simplest form would be a null backend:

```go
// NullBackend ...
type NullBackend struct {
}

// OpenEntry ...
func (backend *NullBackend) OpenEntry(comment string, startTime time.Time, tags []string) error {
    return nil
}

// CloseEntry ...
func (backend *NullBackend) CloseEntry(endTime time.Time) error {
    return nil
}
```

The next step was to write the actual file backing storage. That wasn't that difficult ether. I had to figure out how to serialize a struct into JSON. It's pretty easy in Go:

```go
encoded, err := json.Marshal(entry)
```

And then append it to a file:

```go
f, err := os.OpenFile("entries.json", os.O_RDWR|os.O_CREATE|os.O_APPEND, 0644)
if err != nil {
    return err
}
defer f.Close()

f.Write(encoded)
f.WriteString("\n")
```

And our hand rolled NoSQL database is ready. Might even compete with MongoDB soon, just need to add a couple more features and a bunch of security holes. Ship it! 🚢

---

Google searches that went into getting this to work:

- go sqlite
- go check if file exists
- go implement interface
- go pointer receiver
- golang pointer receiver interface
- go interface
- golang ISO8601 date
- golang write file
- golang serialize to json
- golang marshal unexported fields
- golang writeline

---

- Time spent: 3:50 hours
- Total time spent: 11:00 hours
