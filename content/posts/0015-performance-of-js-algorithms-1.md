---
title: "Performance measurement of JavaScript solutions to common algorithmic questions (part 1)"
date: 2019-02-21
published: true
tags:
    - javascript
    - performance
    - profiling
---

I stumbled upon a [tweet](https://twitter.com/emmawedekind/status/1097855481052303360) and then a [post](https://dev.to/emmawedekind/breaking-down-javascript-solutions-to-common-algorithmic-questions-part-1-1228) by [Emma Wedekind](https://dev.to/@emmawedekind). She goes over some solutions to most common interview questions for JavaScript positions. There are three different problems. And for each she offers a *brute force* and an *optimized* solution, where the latter is a shorter and more elegant version, that normally uses functional programming style over C-style loops. I wouldn't call them *brute force* and *optimized* though, rather *naive* and *elegant*.

The *naive* solution anyone can write as soon as they grasp the very basic concepts of the language and understand the problem. The *elegant* solution requires a better knowledge of the standard library. The code becomes clearer and more succinct. But that sometimes comes with a performance penalty that is not very obvious at the first glance. In this post I wanted to go over some of those less obvious points.

## Reverse a string

Take the first problem: reverse a string. To make it simpler, let's first assume we have only basic ASCII or single code point UTF-16 characters in our string we want to reverse. I'll touch on what to do if it's not the case later.

```js
function reverseString(str) {
    let reversedString = '';

    for (let i = str.length - 1; i >= 0; i--) {
        reversedString += str.charAt(i);
    }

    return reversedString;
}
```

Here we append the characters from the back of the original string to the begging of an empty string one by one. This way we get the reversed string. A non obvious thing that happens here is the string reallocation. Strings in JavaScript are immutable which means every time we modify a string a copy is created. I'm sure there are some clever optimizations to not to reallocate too much and not to create too many useless copies. But the fact is, some array has to grow and some reallocations and copying must be happening. Every time a reallocation happens some new memory gets reserved and all the bytes of the old string get copied to the new place. This takes extra time which is invisible if you look at the code. It would be best to preallocate the memory, since we know how many characters we are going to need ahead of time. As far as I know there's no way to do that in JavaScript.

```js
function reverseString(str) {
    return str.split('').reverse().join('');
}
```

This solution is for sure much clearer and more elegant. It's much easier to reason about the code. It's instantly obvious what the function does.

The hidden danger here is the additional memory the VM has to allocate to keep the temporaries. This code is roughly equivalent to the following:

```js
function reverseString(str) {
    let chars = str.split('');
    let reversed = chars.reverse();
    let result = reversed.join('');
    return result;
}
```

When it's written like this it becomes clear that during the execution we'd need to keep at least two copies of the string in memory. First `chars`. It has to coexist along with the original `str`. Next `reversed`. For a short time it has to coexist along with `chars`. And then `result` has to coexist along with `reversed`. So worst case 4x the memory. Imagine now the string is 1GB long. And of the garbage collector kicks in in between some of these calls, the total run time is gonna a lot longer than it looks.

Here's some quick and dirty profiling (x-axis is string length, y-axis is milliseconds):

![reverse string](https://i.imgur.com/8szFkSr.png)

The elegant solution here is indeed optimized. I'm guessing that is due to all the work being done in the native functions that are dealing with the string as opposed to JavaScript code that runs on the virtual machine. And as you can see the first two solutions are not quite linear because of the intricacies of the underlying VM and CPU architecture. This would take a separate article (or a few) to explain that.

I briefly mentioned above the character encoding problem. Really it's not safe to just reverse the `utf-16` code points. There are some really complicated rules on how Unicode text is formed and some characters or graphemes could be up to 6 code points together. Look at this [answer](https://stackoverflow.com/questions/958908/how-do-you-reverse-a-string-in-place-in-javascript/16776621#16776621) for some details. Long story short: you need to use a special library to deal with characters. Don't reinvent the wheel.

## The longest word

The second problem from the original post is about finding the length of the longest word in a string where words are separated by spaces. The original solution is to split the original string and then loop over the resulting array to find the longest string:

```js
function findLongestWordLength(str) {
    let maxVal = 0;

    const wordArr = str.split(' ');

    for(let i = 0; i < wordArr.length; i++) {
        let word = wordArr[i];
        if (word.length > maxVal) {
            maxVal = word.length;
        }
    }
    return maxVal;
}
```
This version creates a temporary array to store all the words extracted from the original string. The words themselves also need to be stored somewhere. Since the strings are immutable it's very likely the actual bytes are not really duplicated but rather referenced in the original array. But that's hard to guess without looking at the VM source code. The fact is a bunch extra memory is needed.

The *optimized* version uses more functional approach:

```js
function findLongestWordLength(str) {
    const arrOfWords = str.split(' ');
    const arrOfLengths = arrOfWords.map(item => item.length);

    return Math.max(...arrOfLengths);
}
```

In this version there's even more memory used. `arrOfLengths` also has to be kept around. And in a situation when we have 1GB of input with only 1 letter words (I know, it's kinda extreme), we would have 3GB total roughly wasted on this.

`Math.max` thing is kinda broken actually. The spread operator `...` is substituting the array elements for the function arguments. Which makes a function call with a boatload of parameters. Which in turn causes stack overflow exception with already 200k elements. Not a very big number. In `node` REPL:

```js
> Math.max(...Array(200000))
Thrown:
RangeError: Maximum call stack size exceeded
```

For the benchmarking I fixed this version like this:

```js
function findLongestWordLengthFixed(str) {
    const arrOfWords = str.split(' ');
    const arrOfLengths = arrOfWords.map(item => item.length);

    let maxLength = 0;
    for (let i = 0; i < arrOfLengths.length; ++i) {
        if (arrOfLengths[i] > maxLength) {
            maxLength = arrOfLengths[i];
        }
    }

    return maxLength;
}
```

The really optimized solution would be not to create any temporary arrays, but iterate over the original string in-place and find the longest word:

```js
function findLongestWordLengthFast(str) {
    let maxLength = 0;
    let currentLength = 0;

    for (let i = 0, l = str.length; i < l; ++i) {
        if (str.charCodeAt(i) === 32) {
            if (currentLength > maxLength) {
                maxLength = currentLength;
            }
            currentLength = 0;
        } else {
            ++currentLength;
        }
    }

    // Account for the last word
    return currentLength > maxLength ? currentLength : maxLength;
}
```

This function does **zero** heap allocations and is very cache friendly. Here a quick profile (x-axis is string length, y-axis is milliseconds):

![longest word](https://i.imgur.com/P5rc9nT.png)

As you can see the *brute force/naive* versions are performing much better than the *optimized/elegant* one.

## Conclusion, sort of

It's always tempting to rewrite the code in a more elegant, cleaner and often shorter way. Sometimes it comes with a cost. It's important to understand that cost. Sure, when you're reversing a string of 3 characters any solution would do and none of this matters. But often enough we don't know ourselves in the beginning how big the date will be when the system hits production. Big-O analysis is important, but it's not everything. Those pesky constants in O(n) are important as well. Very important for real systems. They could make a big difference, like double you AWS bill or make response time 5 times larger. Keep that in mind next time you reverse a string in production =)

I used [this code](https://gist.github.com/detunized/17f524d74f9fd567d4be7e4a3bbaf1e6) to profile the functions above. I used `node` on macOS. The number may vary across hardware, browsers, OSes. Keep that in mind as well.
