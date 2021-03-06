#pynads

> A monad is just a monoid in the category of endofunctors, what's the problem?
> [-Philip Wadler](http://james-iry.blogspot.com/2009/05/brief-incomplete-and-mostly-wrong.html)

Just playing around with implementing monads in Python.

There's also a little metaclass muckery thrown in for good measure!

Don't take it too seriously, this is just a toy project.

I was good enough to include a test suite though.


Quick Examples
--------------

Currently `Maybe`, `Either`, `List`, `Reader`, `State` and `Writer` are all 
implemented in either full or partial fashion. I've also included an 
applicative dictionary instance named `Map`.

`pynads` will also export `Reader` aliased to `Function` and `R`, but 
these resolve to the original Reader class.

###A Truly 10+ Developer Example

Every Python library needs to be able to tackle FizzBuzz! Which is universally
considered the premier live coding test for interviews.

```python
from pynads import Writer
from pynads.funcs import multibind
from itertools import repeat
from functools import partial

pairs = ((3, 'fizz'), (5, 'buzz'))

def fizzer(n, pairs):
    fizzed = ''.join([buzz for fizz, buzz in pairs if n and not n % fizz]) or n
    return Writer(n+1, {n:fizzed})

multibind(Writer.unit(1), *repeat(partial(fizzer, pairs=pairs), 15))
# Writer(16, {1:1, 2:2, 3:'fizz', 4:4, 5:'buzz', 6:'fizz', 7:7, 8:8,
#             9:'fizz', 10:'buzz', 11:11, 12:'fizz', 13:13, 14:14
#             15:'fizzbuzz'})
```

Interviewer tried to one up you and asked for multiplies of 7 to evaluate to
bazz? Modify the pairs tuple. Extensible and short. 

You can't out fizzbuzz this.

###Putting values in Context

```python
Maybe.unit(4) # Returns Just(4)
```

Or use a functional approach:

```python
unit(4, Maybe)
```

Unit on other Monads:

```python
Either.unit(4)      # Right 4
List.unit(4)        # List 4
Writer.unit(4)      # Writer (4, Mempty)
Map.unit(('a', 4))  # Map({'a': 4})
Reader.unit(4)      # Reader(const)
State.unit(4)       # State(lambda s: (4, s))
```

The `Maybe` monad abuses `__new__` to perform a check when instantiating
an object. You can pass a checker function to determine if a `Just` or
`Nothing` should be returned. By default, if the value being passed is
`None` you get a `Nothing`.

```python
>>> # only even Justs
>>> is_even = lambda x: not x%2
>>> Maybe(3, checker=is_even)
... Nothing
>>> Maybe(4, checker=is_even)
```

Shamelessly, this is lifted from [PyMonad](https://bitbucket.org/jason_delaat/pymonad>).

`List` makes no promises of splatting iterables when using the unit method:

```python
List.unit("hello")   # List("hello")
List.unit({'a': 4})  # List({'a': 4})
List.unit([4, 5])    # List([4, 5])
```

`Reader`'s unit method puts a value into a closure that ignores any input
and returns the original value.

```Python
r = Reader.unit(4)
print(r(None)) # boom, 4 pops out!
```

Kinda similar to ``Reader``, ``State``'s unit method creates a lambda that
awaits some input but returns a tuple of ``(original_value, passed_value)``

```Python
s = State.unit(4)
print(s(None)) # out pops (4, None)
```

###Bind, Shove, `>>=`, et. al

Use a bastardized version of Haskell's `>>=`:

```python
Just(4) >> (lambda v: Maybe(v+2))
```

Chain them together with excessive parens:

```python
Maybe.unit(4) >> (lambda v: v+2) >> (lambda v: Nothing)
```

Tired of guarding against Nones?

```python
from random import randint

def bad_get_int():
    x = randint(1,10)
    return x if x%2 else None

inc = lambda x: Just(x+1)

Maybe(bad_get_int()) >> inc >> inc
```

Now you can focus *what* your fail condition is, rather than how to handle it!


Use the bind assignment operator:
```python
m = Just(2)
m <<= lambda x: Just(x+2) # now it's Just 4
```

When using Reader and pulling from the environment is needed, nesting
lambdas is necessary, formatted for readability:

```python
>>> from operators import itemgetter as read
>>> from pynads import R # use Reader shortcut
>>> comp = R(read('a')) >> (lambda a:
           R(read('b')) >> (lambda b:
           R.unit(a+b)             ))
>>> comp({'a': 10, 'b': 7})
... 17
```

If you've got more binds than editor columns, you can use
`pynads.funcs.multibind` to chain them all together.

```python
from itertools import repeat
multibind(Just(0), *repeat(lambda x: Just(x+2), 3))
```

###Functors
There are here too! Functor is more a protocol, but also serves as an
interface as well. A class must implement the `fmap` method to fulfill the
protocol or interface.

```python
class FMapDict(dict, Functor):
    def fmap(self, f):
        return FMapDict((k, f(v)) for k,v in self.items())
```

Note: FMapDict is actually implemented at `pynads.concrete.map.Map` as both
a functor and an applicative functor.

Two ways to use!:

```Python
fmd = FMapDict((i,i) for i in range(10))
fmd.fmap(lambda x: x+1)
# or more Haskell-y!
fmap(lambda x: x+1, fmd)
```

I lied, there's three! In Haskell there's `<$>` that serves as an infix fmap.
Of course it'll make an appearance here, too!

```python
(lambda x: x+1) % fmd
```

`%` was chosen because if you squint really hard, ignore the angle brackets,
then `%` and `<$>` kinda look similar. It's also on the same precedence
level as `*`, forcing Python to evaluate it first without extra parens.

###Applicatives
We got applicatives as well!

```python
Just(lambda x: x+2).apply(Just(2))
```

But wait, there's an operator!

```python
Just(lambda x: x+2) * Just(2)
```

*Just* like before, take operator overloading to 11!

```python
from random import randint

def bad_get_int():
    x = randint(1,10)
    return Maybe(x if x%2 else None)

add_two = lambda x: lambda y: x+y

t = add_two % bad_get_int() * bad_get_int()
```

Got a curried function (or just a bunch of nested single argument lambdas)?!

```python
fake_curry = lambda x: lambda y: lambda z: x+y+z

multiapply(Just(fake_curry), Just(1), Just(2), Just(3))
```

###Monoids!
Sure, why not. `pynads` has an abstract Monoid base class at
`pynads.abc.monoid.Monoid` (but just `from pynads import Monoid`).

The Monoid abstract base class allows joining together monoids with the `+`
operator (or `sum` or whatever) by defining an `mappend` method which `+`
will delegate to. In addition, the monoid must define an `mempty` value
which represents its "empty" or "zero" value.

This class also provides a default implementation of mconcat which uses
`functools.reduce` and the `mappend` method defined in the instance.
Subclasses of Monoid are welcome to replace `mconcat` with their own versions.

`pynads` has two monoids: `pynads.List` and `pynads.Map`

But that doesn't stop `pynads` from mappending and mconcatting its way through
built in types. int, float, complex, set, frozenset, bool, list, str, dict...
`pynads` don't care, it'll figure out how to handle it. And it doesn't stop
there, it can determine how to `mappend` a few non-built in types as well
like `decimal.Decimal` or your class that extends from `collections.abc.Set`.
Yes, yes, it uses type checking but it tries its best to do it against
ABCs rather than hard types.

###Mempty
With monoids comes mempty! And `pynads` has a pretty nifty trick up its
sleeve when it comes to dealing with mempty. Haskell allows us to use
mempty as a placeholder value. And so does `pynads` with the special `Mempty`
singleton (didn't need to be a singleton though, just taking your RAM into
consideration). `Mempty` just stands around and waits for a real monoid to
show up. That means if you try to use `mappend` or `mconcat` on it, `Mempty`
goes, "Here, let me step out of the way...". If you try to `mconcat` with
all values set to `Mempty`, you get a `Mempty` back ready to step out of the
way again.

On top of all that, it reminds me Memphis when I type out `Mempty` and just
makes me yearn for real BBQ.

##Coming Soon!
Despite this being a toy implementation of Haskell things in Python, I've
taken quite a shine to it. Currently, these are the things in the works:

- do notation (by abusing the coroutine protocol and decorators)
- Expanded notes section so if something seems really odd, you can see my
thought process and the notes I've taken.
- Continuation Monad -- maybe, I'm not sure if I want to tackle this
- Monad Transformers -- once I fully apperciate them

##Sources
Of course, I didn't come up with this idea on my own. Many implementations
of Haskell-style monads in Python exist. And many sources have informed my
understanding of how each monad operates in Haskell. I doubt I'll list all
of them here as some were found by desperate Google searching and I've
forgotten to record them somewhere.

- [PyMonad](https://bitbucket.org/jason_delaat/pymonad>) (original inspiration)
- [Valued Lessons](http://www.valuedlessons.com/2008/01/monads-in-python-with-nice-syntax.html)
- [All About Monads](https://wiki.haskell.org/All_About_Monads)
- [Learn You A Haskell](http://learnyouahaskell.com/)
- [Dustin Getz - Dustin’s awesome monad tutorial for humans, in Python](http://www.dustingetz.com/2012/04/07/dustins-awesome-monad-tutorial-for-humans-in-python.html)
- [Dustin Gets - Writer, Reader, and State monads in Python](http://www.dustingetz.com/2012/10/02/reader-writer-state-monad-in-python.html)
- [The State Monad](https://acm.wustl.edu/functional/state-monad.php)
- [The Day Python Embarrassed Imperative Programming](http://the-27th-comrade.appspot.com/blog/ahJzfnRoZS0yN3RoLWNvbXJhZGVyDAsSBUVudHJ5GOFdDA)
- [You Could Have Invented Monads](http://blog.sigfpe.com/2006/08/you-could-have-invented-monads-and.html)
- [Monads, or Programmable Semicolons](http://zacharyvoase.com/2014/04/30/monads/)
- [bitemyapp Monad Transformers presentation](https://github.com/bitemyapp/presentations/tree/master/monad_transformers)
- [Don't Fear The Monad (video)](http://www.youtube.com/attribution_link?a=o2IwOJe4Tk3p2xPSEti5Fw&u=%2Fwatch%3Fv%3DZhuHCtR3xq8%26feature%3Dshare)
- [Stephen Boyer - Monads, Part 1: A Design Pattern](http://www.stephanboyer.com/post/9/monads-part-1-a-design-pattern)
- Others which I have forgotten
