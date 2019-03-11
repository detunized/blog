---
title: "NUnit to xUnit automatic test convertion"
date: 2019-03-11
published: true
draft: true
tags:
    - c-sharp
    - refactoring
    - roslyn
---

I'm currently working on a major refactoring of a C# library which has many NUnit tests. I decided, without having any good reason, it would be a good idea to migrate them to xUnit. I did a few by hand and it turns out to be tedious. Like really tedious. The most common pattern is the following:

The test in NUnit

```c#
Assert.That(actual, Is.EqualTo(expected));
```

becomes the test in xUnit:

```c#
Assert.Equal(expected, actual);
```

To convert each by hand requires a lot of patience and stamina. Since I don't have either, after doing a few dozens manually I decided to automate the whole thing. The first most obvious approach would be to use a regexp and convert one to the other like so:

```
/Assert\.That\((.*?), Is\.EqualTo\((.*)\)\)/ -> Assert.Equal($2, $1)
```

It does work for some simple cases, but throw in something a bit hairier and the whole thing goes sideways. A perfectly valid small test tears this regexp to shreds:

```c#
Assert.That("));", Is.EqualTo("));")); -> Assert.Equal(", "));");;"));
```

Not good.

The better way to do that would be to parse the source file into an AST (Abstract Syntax Tree) and perform source to source transformations on it. I've done a bit of this in the past with C++ using [Clang/LLVM](https://clang.llvm.org/) and with JavaScript using [Acorn parser](https://github.com/acornjs/acorn). For C# there's [Roslyn](https://github.com/dotnet/roslyn).

How difficult could this be? Let's find out. There's some amount of documentation out there and some samples. Also it's possible to generate a starter project with VS2017 that would do the file loading and minimal AST traversal. It's a good start, we can build on it. Here's a good [starting point](https://github.com/dotnet/roslyn/wiki/Getting-Started-C%23-Syntax-Transformation) for source transformation, for example.

So here's a simplest NUnit module:

```c#
using NUnit.Framework;

namespace Test
{
    [TestFixture]
    class DumpTests
    {
        [Test]
        public void One_plus_one_should_be_two()
        {
            Assert.That(1 + 1, Is.EqualTo(2));
        }
    }
}
```

When converted to xUnit, it becomes this:

```c#
using Xunit;

namespace Test
{
    class DumpTests
    {
        [Fact]
        public void One_plus_one_should_be_two()
        {
            Assert.Equal(2, 1 + 1);
        }
    }
}
```

Precisely the following needs to be done:

- change `using` directive
- remove `TextFixture` class attribute
- replace `Test` attribute with `Fact`
- change `Assert.That` to `Assert.Equal` and swap arguments

The syntax rewriter does all the work, we just need to fill in some logic:

```c#
public class NunitToXunitRewriter: CSharpSyntaxRewriter
{
    ...
}
```

Let's start with the easiest, removing the `TextFixture` attribute:

```c#
public class NunitToXunitRewriter: CSharpSyntaxRewriter
{
    public override SyntaxNode VisitAttributeList(AttributeListSyntax node)
    {
        if (ShouldRemoveTestFixture(node))
            return null;

        return base.VisitAttributeList(node);
    }

    // Checks if the node is "[TestFixture]" and should be removed
    private bool ShouldRemoveTestFixture(AttributeListSyntax node)
    {
        return node.Attributes.Count == 1
            && node.Attributes[0].Name.ToString() == "TestFixture"
            && node.Parent is ClassDeclarationSyntax;
    }
}
```

The code is this case is quite simple. The `VisitAttributeList` function get called for every attribute in the source file. We just check it's the attribute list has only one attribute, that its name is TextFixture and the parent node is a class. If it's all true, then we just return `null` from the visitor method to indicate that the node should be deleted from the syntax tree. Easy.

Next up is the `Test` attribute:

```c#
public class NunitToXunitRewriter: CSharpSyntaxRewriter
{
    public override SyntaxNode VisitAttributeList(AttributeListSyntax node)
    {
        var newNode = TryConvertTestAttribute(node);
        if (newNode != null)
            return newNode;

        return base.VisitAttributeList(node);
    }

    // Converts "[Test]" to "[Fact]"
    private SyntaxNode TryConvertTestAttribute(AttributeListSyntax node)
    {
        if (node.Attributes.Count != 1)
            return null;

        if (node.Attributes[0].Name.ToString() != "Test")
            return null;

        if (!(node.Parent is MethodDeclarationSyntax))
            return null;

        return
            AttributeList(
                AttributeList<AttributeSyntax>(
                    Attribute(
                        IdentifierName("Fact"))))
            .NormalizeWhitespace()
            .WithTriviaFrom(node);
    }
}
```

What we do here is quite similar to the previous example, with one exception that we're not deleting the node, but replacing it with something else. First, we check that it's a single attribute named `Test` and it's attached to a function. To replace it with, we need to construct a new syntax node. In this case it's the same thing, just the name is different. To build the syntax node we use `SyntaxFactory` methods, like `AttributeList`, `Attribute` and so on. The small quirk is the `NormalizeWhitespace` and
`WithTriviaFrom` bits. Those make sure the resulting code is formatted and has the whitespace copied from the original node. Otherwise the output code would look out of place and would require reformatting.



{{* *Also published on [DEV](https://dev.to/detunized/?) and [Medium](https://medium.com/@detunized/?)* *}}
