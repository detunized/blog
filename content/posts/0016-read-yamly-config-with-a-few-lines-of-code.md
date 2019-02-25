---
title: "Read YAMLy config with a few lines of code"
date: 2019-02-25
published: true
tags:
    - c-sharp
    - javascript
    - ruby
    - go
---

I was working on a C# library and in a simple example application I needed to load a config file. It didn't have to be fancy or very efficient. Something like INI, JSON, TOML or YAML would do. What I didn't want to have is any dependencies, not to bother the user with installing any libraries. Unfortunately, .NET doesn't provide any of those in its standard library. There's XML, but I cannot stomach that.

So I though, I could probably write a simple text config file parser in a few minutes. Why not give it a try. All I need is string keys and values. Comments would be good to have. Something like this:

```yaml
# Login username
username: dude@lebowski.com
# User password
password: no one will guess
# URL
url: https://lebowski.com:443/index.html
```

This is a subset of YAML actually. Very clean and readable. How difficult would it be to write a parser for that. Normally, every time I say something like this to myself, I mentally prepare myself for a huge underestimation. What looks like a ten minute task, could turn out to be a week long project. Strangely, not this time. Thanks to pretty great runtime library and awesome LINQ support in 3 minutes I had a fully working solution:

```c#
Dictionary<string, string> ReadConfig(string filename)
{
    return File
        .ReadAllLines(filename)
        .Select(line => line.Trim())
        .Where(line => line.Length > 0 && !line.StartsWith("#"))
        .Select(line => line.Split(new[] {':'}, 2))
        .Where(parts => parts.Length == 2)
        .ToDictionary(parts => parts[0].Trim(), parts => parts[1].Trim());
}
```

This function is not crazy efficient, but who cares. It's pretty robust, it wouldn't fail with an error as long as it's possible to read a file. It doesn't have any error reporting in case there's a syntax error, though. It would simply ignore it. In my case it's good enough.

Let's see how this works. First, I read the file. This call would return an array of strings, one per line:

```c#
File.ReadAllLines(filename)
```

Next, I trim all the whitespace on both ends. `Select` in LINQ is the same as `map` almost everywhere else, it transforms the sequence by applying a function to each element:

```c#
.Select(line => line.Trim())
```

Next, I filter out all lines that are blank or start with `#`. `Where` filters out the sequence by keeping the elements that satisfy the given predicate:

```c#
.Where(line => line.Length > 0 && !line.StartsWith("#"))
```

Next, I split each line on the first colon. If the rest of the line has more colons they will not be split and become part of the value. That's intentional:

```c#
.Select(line => line.Split(new[] {':'}, 2))
```

Next, I filter out all the lines that didn't get split into exactly two parts. This is the place where syntax errors would get ignored and thrown out:

```c#
.Where(parts => parts.Length == 2)
```

And in the last step I convert the array of two element arrays to a dictionary. What in C# is called a dictionary in other languages might be called *object*, *map* or *hash map*. It's a key-value storage or an associative array. In this step I also trim any trailing whitespace on the key and leading whitespace on the value (other ends are trimmed already):

```c#
.ToDictionary(parts => parts[0].TrimEnd(), parts => parts[1].TrimStart());
```

Done. In a few lines and one statement I've read and parsed a config file.

JavaScript has petty similar functional programming capabilities, so it would be possible to mirror this solution in JS. [Like always](https://www.destroyallsoftware.com/talks/wat), there are some gotchas. In this case JS `String.split` function is acting weird. The limit parameter works differently compared to all the other languages I tried. Instead of returning the rest of the line in the last element, `split` in JavaScript truncates the input. [WAT](https://www.destroyallsoftware.com/talks/wat)?! To fix that I have to `join` the split tail back together in the line before the final `reduce` that converts the array to object.

```js
function readConfig(filename) {
    return require("fs")
        .readFileSync(filename, "utf-8")
        .split("\n")
        .map(x => x.trim())
        .filter(x => x.length > 0 && !x.startsWith("#"))
        .map(x => x.split(":"))
        .filter(x => x.length > 1)
        .map(x => [x[0], x.slice(1).join(":")])
        .reduce((a, x) => (a[x[0].trimEnd()] = x[1].trimStart(), a), {})
}
```

JavaScript has native support for JSON, so it's probably stupid to roll your own config format, when JSON could be read in one short statement. The comments are not supported though.

I think the Ruby version is the cleanest, though it's practically the same:

```ruby
def read_config filename
    File
        .readlines("config.yaml")
        .map(&:strip)
        .reject { |x| x.empty? || x.start_with?("#") }
        .map { |x| x.split ":", 2 }
        .select { |x| x.size == 2 }
        .map { |k, v| [k.rstrip, v.lstrip] }
        .to_h
end
```

Ruby supports both YAML and JSON out of the box. It would be easier to just do

```ruby
YAML.load_file "config.yaml"
```

but then I'd have to quote some of the values as YAML is not that flexible with the whitespace and special characters.


How would I do it Go? I wouldn't! I don't want to drown in `if`s, `for`s, `err`s and `nil`s. Just say no to writing code and `go get` some packages.
