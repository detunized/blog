---
title: "Giving Go another chance: error handling"
description: I'm writing a simple time tracking tool and rediscovering Go at the same time.
date: 2019-02-12
published: true
series:
    - Making a time tracking tool in Go
tags:
    - go
    - time tracking
    - rant
    - whining
---

Since the last episode I managed to add a few features here and there: ability to delete entries, minimal editing, some improvements on the file storage. It was quite difficult to find any time to get anything meaningful done, unfortunately. Life happened. It was quite hectic and busy. I had time to think though. I realized I didn't pick the best project to learn Go with.

First of all, I'm trying to recreate a piece of software that I'm mostly happy with. I'd say 99%. I realized that while using it more and more. I should have rather made some pull requests to the original project instead of trying to rewrite it. But then I wouldn't learn Go, would I?

Second, Go doesn't seem to be a good fit for this kind of project. Text processing, no concurrency, no network access. Writing some sort of server or network crawler in Go would be a better fit. I'll try something like this next.

So far I could say things mainly went well. It was not difficult to get productive in a matter of a couple of days. Writing Go feels like writing C most of the time without some of the C headaches. I keep typing the types first, though, and then wonder why it doesn't compile. C habits die slow.

The thing that tripped me up all the time is the error handling. Most often peope complain about the necessity to type `if err != nil ...` after every function call. I'd say it doesn't even bother me that much. It makes error handling explicit with a clear control flow path, versus exception-like implicit secondary control flow.

I think the most difficult part for me is that there's no idiomatic way of dealing with errors. The error itself is too generic:

```go
type error interface {
    Error() string
}
```

That's it. Just something that returns a string. So anything could be an error. And most of the time it's just a string. For example, `os.IsNotExist`. It checks if the error returned from any `file.*` function means that file wasn't found:

```go
func IsNotExist(err error) bool {
    return isNotExist(err)
}
```

In most systems I know of the errors are encoded as enumerations, types or a combination of the two. Something the compiler can actually work with. In Go it's often enough just a string created with `fmt.Errorf`. Handling an error like this is difficult and feels kinda dirty, because the error message *is* the error value and its encoding. This is how it's handled in the standard `os` package:

```go
func isNotExist(err error) bool {
    return checkErrMessageContent(err, "does not exist", "not found",
        "has been removed", "no parent")
}

func checkErrMessageContent(err error, msgs ...string) bool {
    if err == nil {
        return false
    }
    err = underlyingError(err)
    for _, msg := range msgs {
        if contains(err.Error(), msg) {
            return true
        }
    }
    return false
}
```

So to see if the file didn't open because it doesn't exist, I'd have to check the error message for "does not exist" or "not found". What if it's "doesn't exist" or if it's something else that wasn't found? Luckily there are convenience methods provided for this purpose: `os.IsExist` and `os.IsNotExist`. Nice!

This means to handle my own errors, I'd have to create similar methods if I don't want to compare strings all over my program. That's kinda tedious.

Another approach is to create my own error types. Which is also done in many places in the standard lib. At least is then possible to have a [type assertion](https://tour.golang.org/methods/15) to see what type of error I got:

```go
func underlyingError(err error) error {
    switch err := err.(type) {
    case *PathError:
        return err.Err
    case *LinkError:
        return err.Err
    case *SyscallError:
        return err.Err
    }
    return err
}
```

Often enough when the error is handled it's wrapped into another error by simply gluing the error messages together. It's a normal thing to get this from a Go program:

```
Error: Error building site: failed to render pages: render of "page" failed: execute of template failed: template: _internal/opengraph.html:31:19: executing "_internal/opengraph.html" at <.>: range can't iterate over Making a time tracking tool in Go
```

Notice how many colons (`:`) are in that error message. Practically each `:` is a callstack entry, because the typical pattern is to handle an error and wrap it again:

```go
_, err = blah()
if err != nil {
    return fmt.Errorf("blah failed: %v", err)
}
```

There's a library [pkg/errors](https://github.com/pkg/errors) to handle this in a bit better way:

```go
_, err = blah()
if err != nil {
    return errors.Wrap(err, "blah failed")
}
```

It's a step forward. A very small one, but a step forward. The errors are still strings, but they have some idea of structure. Handling such errors is still painful. So far I opted not to handle them properly, just pass along to the poor user to deal with.

To summarize: I have not yet gotten a good feeling on how to return and handle errors in Go. I'll experiment more and see what works for me better. I wish there was something like [`std::result`](https://doc.rust-lang.org/std/result/) in Rust or [`Try`](https://www.scala-lang.org/api/2.12.0/scala/util/Try.html) in Scala.

---

- Total time spent: about 20 hours
