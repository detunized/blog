---
title: "Giving Go another chance: refactoring"
description: I'm writing a simple time tracking tool and rediscovering Go at the same time.
date: 2019-01-26
published: true
series:
    - Making a time tracking tool in Go
tags:
    - go
    - time tracking
    - cli
---

In this session I wanted to add another command. I imagined I'd have to factor out some common code and put it elsewhere. So I started by duplicating a file and trying to build it. And then I had another Go WTF moment. Apparently I cannot have a variable or function with the same name in different files. That I didn't expect to run into. I guess it's kinda like in C, only there that would be a link error. But any intuition I had so far built up for this language just evaporated at this point.

I started googling around and found out that all the files in a package could be essentially treated as one single file. There's no such thing as a variable or a function local to a file. Can have many `init`s though. Anything starting with a capital letter is public and exported from the package (not file). Identifiers starting with a lowercase letter are private or hidden and are not exposed to the users of the package.

I normally refactor all the time. I move code around. I add, delete and re-add functions all the time. I rename everything constantly until I'm happy with the result. Go in general doesn't prevent this style of developing, but it makes it a bit harder by not allowing to have any unused variables or imports. The imports are easily fixed the `goimports` or `goreturns` formatting tools. The local variables have to be removed by hand. This slows down the progress for me quite a bit. I'd rather have the compiler show me a warning instead. I'd get stuff to work first and then I'd clean up the warning. Go doesn't forgive or forget.

As a result of this session I have all shared code extracted and tucked away in a separate file. I have two commands now: `in` and `out`. Things are cleaned up and are ready to be made into a great app.

Next time I start coding something more serious. Enough with the baby stuff, I'm a senior developer after all.

---

Google searches that went into getting this to work:

- go private function
- go function local to a file

---

- Time spent: 35 minutes
- Total time spent: 7:10 hours
