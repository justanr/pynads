#pynads

Just playing around with implementing monads in Python.

There's also a little metaclass muckery thrown in for good measure!

Don't take it too seriously, this is just a toy project.

I was good enough to include a test suite though.


Quick Examples
--------------

Currently `Maybe`, `Either`, `List`, `Reader` and `Writer` are all 
implemented in either full or partial fashion. I've also included an 
applicative dictionary instance named `Map`.

`pynads` will also export `Reader` aliased to `Function` and `R`, but 
these resolve to the original Reader class.

###Putting values in Context

```python
Maybe.unit(4) # Returns Just(4)
```

Or use a functional approach:

```python
unit(4, Maybe)
```

Or emulate Haskell poorly:

```python
4 & Maybe
```

Unit on other Monads:

```python
4 & Either # outputs Right(4)
4 & List   # outputs List(4)
4 & Writer # outputs Writer(4, List())
4 & Map    # outputs Map({4: None})
4 & Reader # outputs Reader(const(4))
```

The `List` monad is also smart enough to differ between strings and mappings
and other types of iterables:

```python
"hello" & List  # List("hello")
{'a': 4} & List # List({'a': 4})
[4, 5] & List   # List(4, 5)
```

`Reader`'s unit method puts a value into a closure that ignores any input
and returns the original value.

###Bind, Shove, `>>=`, et. al

Use a bastardized version of Haskell's `>>=`:

```python
Just(4) >> (lambda v: Maybe(v+2))
```

Chain them together with excessive parens:

```python
Maybe.unit(4) >> (lambda v: Maybe(v+2)) >> (lambda v: Nothing)
```

Here's this thing:

```python
(2 & Just) >> (lambda x: Just(x+2))
```

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
           (a+b) & R              ))
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

###Applicatives
We got applicatives as well!

```python
Just(lambda x: x+2).apply(Just(2))
```

But wait, there's an operator!

```python
Just(lambda x: x+2) * Just(2)
```

*Just* like before, take operator overloading abuse to 11!

```python
((lambda x: x+2) & Just) * Just(2)
```

Got a curried function (or just a bunch of nested single argument lambdas)?!

```python
fake_curry = lambda x: lambda y: lambda z: x+y+z

multiapply(Just(fake_curry), Just(1), Just(2), Just(3))
```

##Coming Soon!
Despite this being a toy implementation of Haskell things in Python, I've
taken quite a shine to it. Currently, these are the things in the works:

- State Monad (seems pretty similar to Reader, shouldn't be hard to hammer out)
- do notation (by abusing the coroutine protocol and decorators)
- Monoids (specifically MonoidPlus)
- Expanded notes section so if something seems really odd, you can see my
thought process and the notes I've taken.
- Expanded docstrings on par with Reader's documentation. Despite being a huge
wall of text, I feel it adequately captures my thought process on both
understanding and translating Reader from Haskell to Python.

##Sources
Of course, I didn't come up with this idea on my own. Many implementations
of Haskell-style monads in Python exist. And many sources have informed my
understanding of how each monad operates in Haskell. I doubt I'll list all
of them here as some were found by desperate Google searching and I've
forgotten to record them somewhere.

- `PyMonad <https://bitbucket.org/jason_delaat/pymonad>`_ (original inspiration)
- `Valued Lessons <http://www.valuedlessons.com/2008/01/monads-in-python-with-nice-syntax.html>`_
- `All About Monads <https://wiki.haskell.org/All_About_Monads>`_
- `Learn You A Haskell <http://learnyouahaskell.com/>`_
- `Dustin Getz - Dustin’s awesome monad tutorial for humans, in Python  <http://www.dustingetz.com/2012/04/07/dustins-awesome-monad-tutorial-for-humans-in-python.html>`_
- `Dustin Gets - Writer, Reader, and State monads in Python <http://www.dustingetz.com/2012/10/02/reader-writer-state-monad-in-python.html>`_
- `The State Monad <https://acm.wustl.edu/functional/state-monad.php>`_
- `The Day Python Embarrassed Imperative Programming <http://the-27th-comrade.appspot.com/blog/ahJzfnRoZS0yN3RoLWNvbXJhZGVyDAsSBUVudHJ5GOFdDA>`_
- `You Could Have Invented Monads <http://blog.sigfpe.com/2006/08/you-could-have-invented-monads-and.html>`_
- `Monads, or Programmable Semicolons <http://zacharyvoase.com/2014/04/30/monads/>`_
- `bitemyapp Monad Transformers presentation <https://github.com/bitemyapp/presentations/tree/master/monad_transformers>`_
- `Don't Fear The Monad (video) <http://www.youtube.com/attribution_link?a=o2IwOJe4Tk3p2xPSEti5Fw&u=%2Fwatch%3Fv%3DZhuHCtR3xq8%26feature%3Dshare>`_
- `Stephen Boyer - Monads, Part 1: A Design Pattern <http://www.stephanboyer.com/post/9/monads-part-1-a-design-pattern>`_
- Others which I have forgotten
