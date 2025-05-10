# Fuzzing CPython with fusil

## Introduction

This report presents the issues found by fuzzing [CPython](https://github.com/python/cpython)
with [fusil](https://github.com/devdanzin/fusil), a tool created by
[Victor Stinner](https://github.com/vstinner) and updated and used by
[Daniel Diniz](https://github.com/devdanzin) for this fuzzing campaign.

### Goals

The primary goal of this fuzzing campaign was to uncover defects, improve
stability, and enhance the overall robustness of CPython, particularly
focusing on new features and diverse configurations. A secondary goal was
to explore ways to improve fusil to be more effective in attaining the
primary goal.

This report intends to present the campaign, analyzing its results
quantitatively and qualitatively, issue-finding patterns, and relevance to
the CPython project. Complementarily, an assessment of the format and
procedures of the campaign should allow improvements to future efforts.

### Context on fusil

While fusil is in fact a "multi-agent Python library used to write
fuzzing programs", in this report the name will be used as shorthand to
refer to the Python fuzzer written by Stinner and enhanced by Diniz, based
on the library.

Fusil works by generating source files containing random calls using
random and/or interesting arguments, then monitoring the execution and
output of each source file. It usually finds crashes resulting from the
processing of invalid objects and unexpected call patterns.

This campaign isn't the first time fusil has been used to fuzz CPython:
in the period of XXXX to YYYY, Stinner reported X issues, while Diniz
reported Y issues. Z of these ZZ issues were considered release blockers
at the time. There was then a hiatus in fusil development from 2015
(version 1.5, published by Stinner) to 2024.

Since Stinner's last version, new features have been added to fusil by
Diniz. These features include running the generated code in parallel
threads, testing class instances in addition to classes and functions,
and using new interesting objects and values as inputs, all of which
found new crashes. Other new features, like running the code
asynchronously or mangling objects by replacing some of their attributes,
haven't found any issues.

## Fuzzing environment and procedures

Fuzzing has started in late October 2024 and is still ongoing as of early
May 2025, meaning this report covers a period of approximately 6 months.
It has been conducted on a free AWS EC2 instance, a free AWS LightSail
instance (for 3 months), 3 free Oracle Cloud instances (2 x64, 1 ARM), a
personal desktop computer and a personal laptop.

Each fusil instance corresponds to a long-running fuzzer process that
creates the code, spawns fuzzing processes, manages sessions and collects
hits, and an ephemeral code execution process at a time. Since each
instance consists of two processes running in parallel, most of them were
assigned two CPU cores when possible.

Fusil was installed from git and many different revisions have been used
along the fuzzing period, as no recent releases are available and new
features have been constantly added.

- Concurrent fuzzing instances: 4 to 10
- Fusil versions: many different revisions
- CPython versions: 3.12, 3.13, 3.14, main
- CPython configurations: debug, release, optimized, GILful, free-threaded,
JITted, ASAN-enabled

A hit is defined as a fuzzing session where either the process ends
abnormally (a segmentation fault, an abort etc.) or a keyword indicating
abnormal conditions is matched in the output, e.g. "SystemError",
"Fatal Python error". Many false positives, especially in the beginning
of the fuzzing campaign, were recorded as hits. These became rarer as
keywords were tightened and known problematic modules were skipped.

After running the fuzzer and collecting hits in the form of long Python
source files (>15k lines per file) together with the output of their
execution, each hit is manually classified as new or duplicate. Manual
reduction of new hits and collection of corresponding backtraces is then
usually performed. In a few instances, there was usage of automatic test
case reduction tools like creduce and shrinkray.

Preliminary results were sometimes shared with CPython Core Developers in
the community Python Discord #internals-and-peps channel, where many
developers helped triage the issues, with special mentions of Peter Bierma
and Jelle Zijlstra for continued assistance.

Issues were then filled containing Minimal Reproducible Examples and,
usually, backtraces and error messages. Most issues filed this way did not
contain a diagnostic or pointed to deeper causes, except when those were
provided by Core Developers, as most cases were beyond the capabilities
of the bug reporter (Diniz) to investigate.

## Results

There was no detailed record keeping regarding fuzzing effort and hits, so
the following estimates of resources used, hits and issues found are
presented instead:

- Fuzzing time: > 25.000 hours (sum of all instances)
- Fuzzing sessions: > 1.000.000
- Hits: > 50.000
- Issues filled: 52 (X valid, Y closed, Z open)
- Resulting PRs: XX (Y open, Z closed)

The 52 issues filled correspond roughly to 30% of all the crashes (issues
with "type-crash" label) and 2% of all issues (including features requests,
bugs and invalid issues) reported in the CPython issue tracker during the
period covered by this report.

Hits and new issues don't seem to appear at a steady pace. Apparently,
there are long periods of no or nearly no new findings, followed by rapid
accumulation of new results when new features are added to fusil, or
when new CPython versions and/or configurations are added to the fuzzing
pool. Repeated hits usually stop being found when the underlying issue
is fixed in CPython, hence the high number of hits recorded. In special
cases, suppressions for specific bugs are added, also stopping repeated
hits for them.

_Graph: bugs filled by date (day? week? bar graph? with line of rolling average bugs per... 3 or 4 weeks?) annotated with dates of new features/configurations?_
![issues_by_week.png](issues_by_week.png)

The temporal pattern of issue creation shows that the highest number of
issues were found when CPython was in a "fusil-naive" state, where no
fuzzing with this tool had happened for over a decade. This corresponds
to the XXX issues found from October 30 to December XX 2024.

_Analyze dates of new features/configurations and correlate with number of issues found._

_Table: Issue number x Kind, Configuration, Python version, Status, number of PRs_

Each issue that resulted from the reported fuzzing effort is detailed
in the **Findings** section in the **Appendix**.

_Table: number of issues by kind?_

Even though abort issues only affect debug builds directly, in many cases
they point to causes that would also create problems in release builds.
Segfault issues sound more serious, but some were very shallow crashes in
seldom used corners of CPython's standard librady.

_Table: number of issues by configuration?_

The high number of issues resulting in aborts makes debug builds the most
fruitful configuration, followed by free-threaded builds. ...

_Table or graph?: issues by estimated relevance/severity?_

The relevance/severity of crashes found was estimated with assistance from
CPython Core Developers? The tally displays how diverse fusil findings
are in terms of value to the project: some issues are trivial, others point
to deep bugs that could affect a large number of users. It should be
highlighted that the CPython developers attempt to fix all found issues,
regardless of relevance, which is a marked difference from some other
projects fuzzed with fusil.

_Table: number of PRs (including backports) by author and status_

The developer with the most PRs (XX, YY%) for the issues found with fusil
was Victor Stinner (@vstinner), followed by ... (X, Y%) and ... (Z, ZZ%).
In total, X developers created PRs to fix these issues.

## Impact

In the CPython project, developers don't assign prioritiy or severity
levels to issues. One of the issues found, #131998, was considered
relevant enough to be classified as a release blocker.

```
_Issues that were considered important?_
_Issues that were considered trivial?_
_Duplicate issues (some with better MREs)?_

Here input by core devs would be important, on positive and negative points:
- are the findings valuable?
- Is fusil/this fuzzing effort helping make CPython better?
- Is the constant filling of crashes disruptive of the normal development flow?
- Is the lack of deep analysis and diagnostics when the issues are filed
something that hinders core devs efforts?
- Would you like to see more issues found with fusil being created?
- Would you prefer that issues only be filed when they have been
diagnosed/analyzed?

Maybe run a poll in discuss.python.org to collect number of developers involved
in diagnosing and fixing issues, and another about their opinions as listed above?
```

## Conclusions

The results indicate that running a fuzzing tool with fusil's features
can be fruitful in a project like CPython. Not only a significant number
of crashes were uncovered, but also important issues were revealed by
identifying some of these crashes.

The temporal pattern of bug finding may indicate that short periodic
fuzzing campaings would have a better cost/benefit than a continuous
effort like the one presented here. New features in fusil can justify such
a campaign, while the pace of accumulation of new issues in CPython doesn't
seem to necessitate continuous monitoring.

```
Cultural fit? Depending on Core Devs opinions. If there is a large number of
devs participating in fixing these issues, highligt that. If the general
opinion is that fusil brought value to CPython, hightlight that.

Contrast with low interest in some other projects, like polars and numpy,
and cite that SciPy had a great response to issues found.
```

The original design of fusil's Python fuzzer makes it well-suited for
fuzzing CPython, finding both deep, relevant bugs as well as shallow, low
value crashes. Newly added features also allowed finding both kinds of
issues, achieving the secondary goal of exploring ways to improve fusil
to better excercize CPython's code paths in pursuit of crashes.

Fuzzing CPython with fusil has proved it to be a valuable tool for
identifying and reducing software defects in that project. This means that
the primary goal of the fuzzing campaign was achieved, with relevant
contributions made to CPython's robustness.


-------------
## Apendix

### Findings

Issue titles were collected at the time of writing the report and thus can
in some cases be more descriptive than the original titles.

The "Python versions" field reports the tags used in CPython's issue
tracker, which will under-represent older versions as those tags get
removed or aren't added as versions leave the maintainance window.

The "PRs" field lists all PRs that link to the issue, regardless of
status (open, merged, closed without merging etc.).


#### 1- [126219](https://github.com/python/cpython/issues/126219) - `tkinter.Tk` segfault with invalid `className`

```python
import  _tkinter
_tkinter.create(None, '', '\U0010FFFF', None)

# OR

import tkinter
tkinter.Tk(screenName=None, baseName='', className='\U0010FFFF')
```

- Issue Number: 126219
- Date filled: 30/10/2024
- Kind: Segmentation Fault
- Configuration: release
- Python versions: 3.12, 3.13, 3.14, main
- Status: open
- PRs (author):
  - None yet

<details><summary>Backtrace/error message:</summary>
<p>


```shell
#0  0x00007ffff77bab5b in Tcl_UtfToUniChar () from /lib/x86_64-linux-gnu/libtcl8.6.so
#1  0x00007ffff77bc993 in ?? () from /lib/x86_64-linux-gnu/libtcl8.6.so
#2  0x00007ffff77bb795 in Tcl_UtfToTitle () from /lib/x86_64-linux-gnu/libtcl8.6.so
#3  0x00007ffff78b5083 in ?? () from /lib/x86_64-linux-gnu/libtk8.6.so
#4  0x00007ffff79dcf9d in Tcl_AppInit (interp=0x555555e14860) at ./Modules/tkappinit.c:40
#5  0x00007ffff79d92b4 in Tkapp_New (screenName=screenName@entry=0x0,
    className=className@entry=0x7ffff7c2c1c0 "\364\217\277\277", interactive=interactive@entry=0,
    wantobjects=wantobjects@entry=0, wantTk=wantTk@entry=1, sync=sync@entry=0, use=0x0)
    at ./Modules/_tkinter.c:730
#6  0x00007ffff79d953f in _tkinter_create_impl (module=module@entry=<module at remote 0x7ffff7ab9eb0>,
    screenName=screenName@entry=0x0, baseName=baseName@entry=0x555555c77ef0 <_PyRuntime+51344> "",
    className=className@entry=0x7ffff7c2c1c0 "\364\217\277\277", interactive=interactive@entry=0,
    wantobjects=wantobjects@entry=0, wantTk=1, sync=0, use=0x0) at ./Modules/_tkinter.c:3176
#7  0x00007ffff79d99c6 in _tkinter_create (module=<module at remote 0x7ffff7ab9eb0>, args=0x7ffff7fb0080,
    nargs=<optimized out>) at ./Modules/clinic/_tkinter.c.h:820
#8  0x00005555556f18b0 in cfunction_vectorcall_FASTCALL (
    func=<built-in method create of module object at remote 0x7ffff7ab9eb0>, args=0x7ffff7fb0080,
    nargsf=<optimized out>, kwnames=<optimized out>) at Objects/methodobject.c:436
#9  0x000055555567ba55 in _PyObject_VectorcallTstate (tstate=0x555555cbbc70 <_PyRuntime+329232>,
    callable=<built-in method create of module object at remote 0x7ffff7ab9eb0>, args=0x7ffff7fb0080,
    nargsf=9223372036854775812, kwnames=0x0) at ./Include/internal/pycore_call.h:167
```
</p>
</details>

----------

#### 2- [126220](https://github.com/python/cpython/issues/126220) - `_lsprof.Profiler._creturn_callback()` segfaults

```python
from _lsprof import Profiler
Profiler()._creturn_callback()
# OR
Profiler()._ccall_callback()
```

- Issue Number: 126220
- Date filled: 31/10/2024
- Kind: Segmentation Fault
- Configuration: release
- Python versions: 3.12, 3.13, 3.14, main
- Status: Closed-Completed
- PRs (author):
  - [126233](https://github.com/python/cpython/pull/126233) (@sobolevn)
  - [126271](https://github.com/python/cpython/pull/126271) (@sobolevn)
  - [126310](https://github.com/python/cpython/pull/126310) (@sobolevn, @erlend-aasland)
  - [126311](https://github.com/python/cpython/pull/126311) (@sobolevn, @erlend-aasland)
  - [126402](https://github.com/python/cpython/pull/126402) (@sobolevn, @erlend-aasland)


<details><summary>Backtrace/error message:</summary>
<p>


```shell
Program received signal SIGSEGV, Segmentation fault.
get_cfunc_from_callable (callable=0x0, self_arg=0x7ffff7bff710, missing=0x555555c53b80 <_PyInstrumentation_MISSING>) at ./Modules/_lsprof.c:628
628         if (PyCFunction_Check(callable)) {
(gdb) bt
#0  get_cfunc_from_callable (callable=0x0, self_arg=0x7ffff7bff710,
    missing=0x555555c53b80 <_PyInstrumentation_MISSING>) at ./Modules/_lsprof.c:628
#1  0x00007ffff79dd610 in creturn_callback (self=0x7ffff7a91050, args=<optimized out>,
    size=<optimized out>) at ./Modules/_lsprof.c:676
#2  0x000055555568f4b9 in method_vectorcall_FASTCALL (func=0x7ffff7aba630, args=0x7ffff7fb0078,
    nargsf=<optimized out>, kwnames=<optimized out>) at Objects/descrobject.c:401
#3  0x000055555567ba55 in _PyObject_VectorcallTstate (tstate=0x555555cbbc70 <_PyRuntime+329232>,
    callable=0x7ffff7aba630, args=0x7ffff7fb0078, nargsf=9223372036854775809, kwnames=0x0)
    at ./Include/internal/pycore_call.h:167
#4  0x000055555567bb74 in PyObject_Vectorcall (callable=callable@entry=0x7ffff7aba630,
    args=args@entry=0x7ffff7fb0078, nargsf=<optimized out>, kwnames=kwnames@entry=0x0)
    at Objects/call.c:327
#5  0x0000555555827d24 in _PyEval_EvalFrameDefault (
    tstate=tstate@entry=0x555555cbbc70 <_PyRuntime+329232>, frame=0x7ffff7fb0020,
    throwflag=throwflag@entry=0) at Python/generated_cases.c.h:955
#6  0x0000555555852fb7 in _PyEval_EvalFrame (throwflag=0, frame=<optimized out>,
    tstate=0x555555cbbc70 <_PyRuntime+329232>) at ./Include/internal/pycore_ceval.h:116
#7  _PyEval_Vector (tstate=tstate@entry=0x555555cbbc70 <_PyRuntime+329232>,
    func=func@entry=0x7ffff7a46450, locals=locals@entry=0x7ffff7a55df0, args=args@entry=0x0,
    argcount=argcount@entry=0, kwnames=kwnames@entry=0x0) at Python/ceval.c:1886
#8  0x0000555555853096 in PyEval_EvalCode (co=co@entry=0x7ffff7a58630,
    globals=globals@entry=0x7ffff7a55df0, locals=locals@entry=0x7ffff7a55df0) at Python/ceval.c:662
#9  0x00005555559251f4 in run_eval_code_obj (tstate=tstate@entry=0x555555cbbc70 <_PyRuntime+329232>,
    co=co@entry=0x7ffff7a58630, globals=globals@entry=0x7ffff7a55df0, locals=locals@entry=0x7ffff7a55df0)
    at Python/pythonrun.c:1338
```
</p>
</details>

----------

#### 3- [126221](https://github.com/python/cpython/issues/126221) - `sre_constants._makecodes` segfaults in JIT builds

```python

```

- Issue Number: 126221
- Date filed: 31/10/2024
- Date closed: 31/10/2024
- Kind: Segfault/Crash
- Configuration:
- Python versions: 
- Status: closed
- PRs (author):
  - []() ()

<details><summary>Backtrace/error message:</summary>
<p>


```shell

```
</p>
</details>

----------


#### 4- [126223](https://github.com/python/cpython/issues/126223) - `SystemError` caused by `_interpreters.create()` with invalid unicode argument

```python

```

- Issue Number: 126223
- Date filed: 31/10/2024
- Date closed: 31/10/2024
- Kind: SystemError
- Configuration:
- Python versions: 3.13;3.14
- Status: closed
- PRs (author):
  - []() ()

<details><summary>Backtrace/error message:</summary>
<p>


```shell

```
</p>
</details>

----------


#### 5- [126312](https://github.com/python/cpython/issues/126312) - GC aborts in debug no-gil build

```python

```

- Issue Number: 126312
- Date filed: 01/11/2024
- Date closed: 15/11/2024
- Kind: Abort/AssertionError
- Configuration:
- Python versions: 3.13;3.14
- Status: closed
- PRs (author):
  - []() ()

<details><summary>Backtrace/error message:</summary>
<p>


```shell

```
</p>
</details>

----------


#### 6- [126313](https://github.com/python/cpython/issues/126313) - `curses.napms()` aborts with a `SystemError`

```python

```

- Issue Number: 126313
- Date filed: 01/11/2024
- Date closed: 04/11/2024
- Kind: Abort/AssertionError
- Configuration:
- Python versions: 3.13;3.14
- Status: closed
- PRs (author):
  - []() ()

<details><summary>Backtrace/error message:</summary>
<p>


```shell

```
</p>
</details>

----------


#### 7- [126314](https://github.com/python/cpython/issues/126314) - Running `tracemalloc` in threads segfaults on no-gil

```python

```

- Issue Number: 126314
- Date filed: 01/11/2024
- Date closed: 14/03/2025
- Kind: Segfault/Crash
- Configuration:
- Python versions: 3.13;3.14
- Status: closed
- PRs (author):
  - []() ()

<details><summary>Backtrace/error message:</summary>
<p>


```shell

```
</p>
</details>

----------


#### 8- [126315](https://github.com/python/cpython/issues/126315) - `tracemalloc` aborts when run from threads in no-gil

```python

```

- Issue Number: 126315
- Date filed: 01/11/2024
- Date closed: 
- Kind: Abort/AssertionError
- Configuration:
- Python versions: 3.13;3.14
- Status: open
- PRs (author):
  - []() ()

<details><summary>Backtrace/error message:</summary>
<p>


```shell

```
</p>
</details>

----------


#### 9- [126316](https://github.com/python/cpython/issues/126316) - `grp` is not thread safe

```python

```

- Issue Number: 126316
- Date filed: 01/11/2024
- Date closed: 21/11/2024
- Kind: 
- Configuration:
- Python versions: 3.13;3.14
- Status: closed
- PRs (author):
  - []() ()

<details><summary>Backtrace/error message:</summary>
<p>


```shell

```
</p>
</details>

----------


#### 10- [126341](https://github.com/python/cpython/issues/126341) - `SystemError` from calling `__iter__` on a released `memoryview`

```python

```

- Issue Number: 126341
- Date filed: 03/11/2024
- Date closed: 13/11/2024
- Kind: SystemError
- Configuration:
- Python versions: 3.12;3.13;3.14
- Status: closed
- PRs (author):
  - []() ()

<details><summary>Backtrace/error message:</summary>
<p>


```shell

```
</p>
</details>

----------


#### 11- [126366](https://github.com/python/cpython/issues/126366) - Abort in free-threaded build due to mutation of `ChainMap` of a `Counter` in threads

```python

```

- Issue Number: 126366
- Date filed: 03/11/2024
- Date closed: 18/04/2025
- Kind: Abort/AssertionError
- Configuration:
- Python versions: 3.13;3.14
- Status: closed
- PRs (author):
  - []() ()

<details><summary>Backtrace/error message:</summary>
<p>


```shell

```
</p>
</details>

----------


#### 12- [126455](https://github.com/python/cpython/issues/126455) - Calling many methods on `_ssl._SSLSocket()` segfaults

```python

```

- Issue Number: 126455
- Date filed: 05/11/2024
- Date closed: 06/11/2024
- Kind: Segfault/Crash
- Configuration:
- Python versions: 3.12;3.13;3.14
- Status: closed
- PRs (author):
  - []() ()

<details><summary>Backtrace/error message:</summary>
<p>


```shell

```
</p>
</details>

----------


#### 13- [126456](https://github.com/python/cpython/issues/126456) - `_pyrepl._minimal_curses.tigetstr` segfaults

```python

```

- Issue Number: 126456
- Date filed: 05/11/2024
- Date closed: 13/11/2024
- Kind: Segfault/Crash
- Configuration:
- Python versions: 3.13;3.14
- Status: closed
- PRs (author):
  - []() ()

<details><summary>Backtrace/error message:</summary>
<p>


```shell

```
</p>
</details>

----------


#### 14- [126461](https://github.com/python/cpython/issues/126461) - Calling `_pickle.load` with a `MagicMock` results in `SystemError`/aborts

```python

```

- Issue Number: 126461
- Date filed: 05/11/2024
- Date closed: 06/11/2024
- Kind: Abort/AssertionError
- Configuration:
- Python versions: 3.12;3.13;3.14
- Status: closed
- PRs (author):
  - []() ()

<details><summary>Backtrace/error message:</summary>
<p>


```shell

```
</p>
</details>

----------


#### 15- [126594](https://github.com/python/cpython/issues/126594) - Failed assertion in typeobject.c::wrap_buffer for `b"".__buffer__(-2**31 - 1)`

```python

```

- Issue Number: 126594
- Date filed: 08/11/2024
- Date closed: 24/11/2024
- Kind: Abort/AssertionError
- Configuration:
- Python versions: 3.12;3.13;3.14
- Status: closed
- PRs (author):
  - []() ()

<details><summary>Backtrace/error message:</summary>
<p>


```shell

```
</p>
</details>

----------


#### 16- [126595](https://github.com/python/cpython/issues/126595) - Failed assertion in `itertoolsmodule.c: itertools_count_impl` for `count(sys.maxsize)`

```python

```

- Issue Number: 126595
- Date filed: 08/11/2024
- Date closed: 12/11/2024
- Kind: Abort/AssertionError
- Configuration:
- Python versions: 3.12;3.13;3.14
- Status: closed
- PRs (author):
  - []() ()

<details><summary>Backtrace/error message:</summary>
<p>


```shell

```
</p>
</details>

----------


#### 17- [126644](https://github.com/python/cpython/issues/126644) - `_interpreters` is not thread safe on the free-threaded build

```python

```

- Issue Number: 126644
- Date filed: 10/11/2024
- Date closed: 11/01/2025
- Kind: 
- Configuration:
- Python versions: 3.13;3.14
- Status: closed
- PRs (author):
  - []() ()

<details><summary>Backtrace/error message:</summary>
<p>


```shell

```
</p>
</details>

----------


#### 18- [126654](https://github.com/python/cpython/issues/126654) - `_interpreters.exec` with invalid parameters segfaults

```python

```

- Issue Number: 126654
- Date filed: 10/11/2024
- Date closed: 11/11/2024
- Kind: Segfault/Crash
- Configuration:
- Python versions: 
- Status: closed
- PRs (author):
  - []() ()

<details><summary>Backtrace/error message:</summary>
<p>


```shell

```
</p>
</details>

----------


#### 19- [126876](https://github.com/python/cpython/issues/126876) - Assertion failure for `socket` with too large default timeout (larger than INT_MAX)

```python

```

- Issue Number: 126876
- Date filed: 15/11/2024
- Date closed: 14/12/2024
- Kind: Abort/AssertionError
- Configuration:
- Python versions: 3.12;3.13;3.14
- Status: closed
- PRs (author):
  - []() ()

<details><summary>Backtrace/error message:</summary>
<p>


```shell

```
</p>
</details>

----------


#### 20- [126881](https://github.com/python/cpython/issues/126881) - Segfault with `asyncio.base_events.BaseEventLoop` when passed a small float to `set_debug`.

```python

```

- Issue Number: 126881
- Date filed: 15/11/2024
- Date closed: 29/11/2024
- Kind: Segfault/Crash
- Configuration:
- Python versions: 3.12;3.13;3.14
- Status: closed
- PRs (author):
  - []() ()

<details><summary>Backtrace/error message:</summary>
<p>


```shell

```
</p>
</details>

----------


#### 21- [126884](https://github.com/python/cpython/issues/126884) - Calling `cProfile.runctx` in threads on a free-threading build segfaults

```python

```

- Issue Number: 126884
- Date filed: 15/11/2024
- Date closed: 
- Kind: Segfault/Crash
- Configuration:
- Python versions: 3.13;3.14
- Status: open
- PRs (author):
  - []() ()

<details><summary>Backtrace/error message:</summary>
<p>


```shell

```
</p>
</details>

----------


#### 22- [126895](https://github.com/python/cpython/issues/126895) - Segfault/aborts calling `readline.set_completer_delims` in threads in a free-threaded build

```python

```

- Issue Number: 126895
- Date filed: 16/11/2024
- Date closed: 17/03/2025
- Kind: Segfault/Crash
- Configuration:
- Python versions: 3.13;3.14
- Status: closed
- PRs (author):
  - []() ()

<details><summary>Backtrace/error message:</summary>
<p>


```shell

```
</p>
</details>

----------


#### 23- [126907](https://github.com/python/cpython/issues/126907) - Running `atexit` from threads in free-threading build segfaults

```python

```

- Issue Number: 126907
- Date filed: 16/11/2024
- Date closed: 16/12/2024
- Kind: Segfault/Crash
- Configuration:
- Python versions: 3.13;3.14
- Status: closed
- PRs (author):
  - []() ()

<details><summary>Backtrace/error message:</summary>
<p>


```shell

```
</p>
</details>

----------


#### 24- [127085](https://github.com/python/cpython/issues/127085) - Calling `ShareableList.count` in threads aborts: `Assertion 'self->exports == 0' failed`

```python

```

- Issue Number: 127085
- Date filed: 21/11/2024
- Date closed: 16/12/2024
- Kind: Abort/AssertionError
- Configuration:
- Python versions: 3.13;3.14
- Status: closed
- PRs (author):
  - []() ()

<details><summary>Backtrace/error message:</summary>
<p>


```shell

```
</p>
</details>

----------


#### 25- [127165](https://github.com/python/cpython/issues/127165) - Segfault in invalid `concurrent.futures.interpreter.WorkerContext`

```python

```

- Issue Number: 127165
- Date filed: 22/11/2024
- Date closed: 01/12/2024
- Kind: Segfault/Crash
- Configuration:
- Python versions: 3.13;3.14
- Status: closed
- PRs (author):
  - []() ()

<details><summary>Backtrace/error message:</summary>
<p>


```shell

```
</p>
</details>

----------


#### 26- [127182](https://github.com/python/cpython/issues/127182) - Assertion failure from `StringIO.__setstate__`

```python

```

- Issue Number: 127182
- Date filed: 23/11/2024
- Date closed: 25/11/2024
- Kind: Abort/AssertionError
- Configuration:
- Python versions: 3.13;3.14
- Status: closed
- PRs (author):
  - []() ()

<details><summary>Backtrace/error message:</summary>
<p>


```shell

```
</p>
</details>

----------


#### 27- [127190](https://github.com/python/cpython/issues/127190) - Segfault from `asyncio.events._running_loop.__setattr__` with invalid name

```python

```

- Issue Number: 127190
- Date filed: 23/11/2024
- Date closed: 28/11/2024
- Kind: Segfault/Crash
- Configuration:
- Python versions: 3.13;3.14
- Status: closed
- PRs (author):
  - []() ()

<details><summary>Backtrace/error message:</summary>
<p>


```shell

```
</p>
</details>

----------


#### 28- [127192](https://github.com/python/cpython/issues/127192) - Segfault or abort in free-threaded build calling methods from exception in threads

```python

```

- Issue Number: 127192
- Date filed: 23/11/2024
- Date closed: 23/11/2024
- Kind: Segfault/Crash
- Configuration:
- Python versions: 3.13;3.14
- Status: closed
- PRs (author):
  - []() ()

<details><summary>Backtrace/error message:</summary>
<p>


```shell

```
</p>
</details>

----------


#### 29- [127196](https://github.com/python/cpython/issues/127196) - `_interpreters.exec` with invalid dict as `shared` segfaults

```python

```

- Issue Number: 127196
- Date filed: 23/11/2024
- Date closed: 09/01/2025
- Kind: Segfault/Crash
- Configuration:
- Python versions: 3.13;3.14
- Status: closed
- PRs (author):
  - []() ()

<details><summary>Backtrace/error message:</summary>
<p>


```shell

```
</p>
</details>

----------


#### 30- [127208](https://github.com/python/cpython/issues/127208) - `ExtensionFileLoader.load_module` aborts when initialized with a path containing null-bytes

```python

```

- Issue Number: 127208
- Date filed: 24/11/2024
- Date closed: 29/11/2024
- Kind: Abort/AssertionError
- Configuration:
- Python versions: 3.12;3.13;3.14
- Status: closed
- PRs (author):
  - []() ()

<details><summary>Backtrace/error message:</summary>
<p>


```shell

```
</p>
</details>

----------


#### 31- [127234](https://github.com/python/cpython/issues/127234) - Assertion failures from `_interpchannels._register_end_types` 

```python

```

- Issue Number: 127234
- Date filed: 24/11/2024
- Date closed: 
- Kind: Abort/AssertionError
- Configuration:
- Python versions: 3.13;3.14
- Status: open
- PRs (author):
  - []() ()

<details><summary>Backtrace/error message:</summary>
<p>


```shell

```
</p>
</details>

----------


#### 32- [127235](https://github.com/python/cpython/issues/127235) - Failed assertion in `Python/legacy_tracing.c:431` on a free-threading build

```python

```

- Issue Number: 127235
- Date filed: 24/11/2024
- Date closed: 
- Kind: Abort/AssertionError
- Configuration:
- Python versions: 
- Status: open
- PRs (author):
  - []() ()

<details><summary>Backtrace/error message:</summary>
<p>


```shell

```
</p>
</details>

----------


#### 33- [127316](https://github.com/python/cpython/issues/127316) - [FreeThreading] object_set_class() fails with an assertion error in _PyCriticalSection_AssertHeld()

```python

```

- Issue Number: 127316
- Date filed: 27/11/2024
- Date closed: 29/11/2024
- Kind: Abort/AssertionError
- Configuration:
- Python versions: 
- Status: closed
- PRs (author):
  - []() ()

<details><summary>Backtrace/error message:</summary>
<p>


```shell

```
</p>
</details>

----------


#### 34- [127603](https://github.com/python/cpython/issues/127603) - Abort from `GenericAlias.__sizeof__`: `ob->ob_type != &PyLong_Type`

```python

```

- Issue Number: 127603
- Date filed: 04/12/2024
- Date closed: 11/12/2024
- Kind: Abort/AssertionError
- Configuration:
- Python versions: 3.12
- Status: closed
- PRs (author):
  - []() ()

<details><summary>Backtrace/error message:</summary>
<p>


```shell

```
</p>
</details>

----------


#### 35- [127836](https://github.com/python/cpython/issues/127836) - Assertion failure on finalization with `_lsprof` and `asyncio` in 3.12

```python

```

- Issue Number: 127836
- Date filed: 11/12/2024
- Date closed: 23/02/2025
- Kind: Abort/AssertionError
- Configuration:
- Python versions: 3.12
- Status: closed
- PRs (author):
  - []() ()

<details><summary>Backtrace/error message:</summary>
<p>


```shell

```
</p>
</details>

----------


#### 36- [127870](https://github.com/python/cpython/issues/127870) - Segfaults in ctypes _as_parameter_ handling when called with `MagicMock`

```python

```

- Issue Number: 127870
- Date filed: 12/12/2024
- Date closed: 13/12/2024
- Kind: Segfault/Crash
- Configuration:
- Python versions: 
- Status: closed
- PRs (author):
  - []() ()

<details><summary>Backtrace/error message:</summary>
<p>


```shell

```
</p>
</details>

----------


#### 37- [129573](https://github.com/python/cpython/issues/129573) - Failed assertion in `_PyUnicode_Equal` from `calculate_suggestions` with non-string candidate

```python

```

- Issue Number: 129573
- Date filed: 02/02/2025
- Date closed: 
- Kind: Abort/AssertionError
- Configuration:
- Python versions: 3.12;3.13;3.14
- Status: open
- PRs (author):
  - []() ()

<details><summary>Backtrace/error message:</summary>
<p>


```shell

```
</p>
</details>

----------


#### 38- [129766](https://github.com/python/cpython/issues/129766) - Fatal Python error from `warnings._release_lock()`

```python

```

- Issue Number: 129766
- Date filed: 07/02/2025
- Date closed: 07/02/2025
- Kind: Fatal Python Error
- Configuration:
- Python versions: 
- Status: closed
- PRs (author):
  - []() ()

<details><summary>Backtrace/error message:</summary>
<p>


```shell

```
</p>
</details>

----------


#### 39- [131580](https://github.com/python/cpython/issues/131580) - Faulthandler segfaults when called from threads

```python

```

- Issue Number: 131580
- Date filed: 22/03/2025
- Date closed: 25/03/2025
- Kind: Segfault/Crash
- Configuration:
- Python versions: 
- Status: closed
- PRs (author):
  - []() ()

<details><summary>Backtrace/error message:</summary>
<p>


```shell

```
</p>
</details>

----------


#### 40- [131998](https://github.com/python/cpython/issues/131998) - The interpreter crashes when specializing bound method calls on unbound objects

```python

```

- Issue Number: 131998
- Date filed: 02/04/2025
- Date closed: 08/04/2025
- Kind: Segfault/Crash
- Configuration:
- Python versions: 3.13;3.14
- Status: closed
- PRs (author):
  - []() ()

<details><summary>Backtrace/error message:</summary>
<p>


```shell

```
</p>
</details>

----------


#### 41- [132002](https://github.com/python/cpython/issues/132002) - Segfault deallocating a `ContextVar` built with `str` subclass

```python

```

- Issue Number: 132002
- Date filed: 02/04/2025
- Date closed: 02/04/2025
- Kind: Segfault/Crash
- Configuration:
- Python versions: 3.12;3.13;3.14
- Status: closed
- PRs (author):
  - []() ()

<details><summary>Backtrace/error message:</summary>
<p>


```shell

```
</p>
</details>

----------


#### 42- [132011](https://github.com/python/cpython/issues/132011) - Failed assertion in `_PyEval_EvalFrameDefault`: `self_o != NULL`

```python

```

- Issue Number: 132011
- Date filed: 02/04/2025
- Date closed: 06/04/2025
- Kind: Abort/AssertionError
- Configuration:
- Python versions: 
- Status: closed
- PRs (author):
  - []() ()

<details><summary>Backtrace/error message:</summary>
<p>


```shell

```
</p>
</details>

----------


#### 43- [132171](https://github.com/python/cpython/issues/132171) - Assertion failure calling `_interpreters.run_string` with a string subclass instance

```python

```

- Issue Number: 132171
- Date filed: 06/04/2025
- Date closed: 07/04/2025
- Kind: Abort/AssertionError
- Configuration:
- Python versions: 
- Status: closed
- PRs (author):
  - []() ()

<details><summary>Backtrace/error message:</summary>
<p>


```shell

```
</p>
</details>

----------


#### 44- [132176](https://github.com/python/cpython/issues/132176) - Abort when using a tuple subclass instance as the `bases` parameter for `type`

```python

```

- Issue Number: 132176
- Date filed: 06/04/2025
- Date closed: 15/04/2025
- Kind: Abort/AssertionError
- Configuration:
- Python versions: 
- Status: closed
- PRs (author):
  - []() ()

<details><summary>Backtrace/error message:</summary>
<p>


```shell

```
</p>
</details>

----------


#### 45- [132250](https://github.com/python/cpython/issues/132250) - `_ccall_callback` method of `_lsprof.Profiler` causes Fatal Python error

```python

```

- Issue Number: 132250
- Date filed: 08/04/2025
- Date closed: 08/04/2025
- Kind: Fatal Python Error
- Configuration:
- Python versions: 
- Status: closed
- PRs (author):
  - []() ()

<details><summary>Backtrace/error message:</summary>
<p>


```shell

```
</p>
</details>

----------


#### 46- [132296](https://github.com/python/cpython/issues/132296) - Concurrent deallocation of threads while calling `PyEval_SetTrace`

```python

```

- Issue Number: 132296
- Date filed: 09/04/2025
- Date closed: 
- Kind: 
- Configuration:
- Python versions: 
- Status: open
- PRs (author):
  - []() ()

<details><summary>Backtrace/error message:</summary>
<p>


```shell

```
</p>
</details>

----------


#### 47- [132386](https://github.com/python/cpython/issues/132386) - Segfault or failed assertion (`obj != NULL`) in `PyStackRef_FromPyObjectSteal`

```python

```

- Issue Number: 132386
- Date filed: 11/04/2025
- Date closed: 11/04/2025
- Kind: Segfault/Crash
- Configuration:
- Python versions: 
- Status: closed
- PRs (author):
  - []() ()

<details><summary>Backtrace/error message:</summary>
<p>


```shell

```
</p>
</details>

----------


#### 48- [132461](https://github.com/python/cpython/issues/132461) - Abort from calling `OrderedDict.setdefault` with an invalid value

```python

```

- Issue Number: 132461
- Date filed: 13/04/2025
- Date closed: 
- Kind: Abort/AssertionError
- Configuration:
- Python versions: 
- Status: open
- PRs (author):
  - []() ()

<details><summary>Backtrace/error message:</summary>
<p>


```shell

```
</p>
</details>

----------


#### 49- [132551](https://github.com/python/cpython/issues/132551) - Segfault/abort from calling `BytesIO` `unshare_buffer` in threads on a free-threaded build

```python

```

- Issue Number: 132551
- Date filed: 15/04/2025
- Date closed: 08/05/2025
- Kind: Segfault/Crash
- Configuration:
- Python versions: 3.13;3.14
- Status: closed
- PRs (author):
  - []() ()

<details><summary>Backtrace/error message:</summary>
<p>


```shell

```
</p>
</details>

----------


#### 50- [132707](https://github.com/python/cpython/issues/132707) - Segfault in free-threaded build from interaction of nested list/tuple repr

```python

```

- Issue Number: 132707
- Date filed: 18/04/2025
- Date closed: 18/04/2025
- Kind: Segfault/Crash
- Configuration:
- Python versions: 
- Status: closed
- PRs (author):
  - []() ()

<details><summary>Backtrace/error message:</summary>
<p>


```shell

```
</p>
</details>

----------


#### 51- [132713](https://github.com/python/cpython/issues/132713) - Segfault in `union_repr` from `list_repr_impl` in free-threaded build

```python

```

- Issue Number: 132713
- Date filed: 19/04/2025
- Date closed: 23/04/2025
- Kind: Segfault/Crash
- Configuration:
- Python versions: 3.13;3.14
- Status: closed
- PRs (author):
  - []() ()

<details><summary>Backtrace/error message:</summary>
<p>


```shell

```
</p>
</details>

----------


#### 52- [133441](https://github.com/python/cpython/issues/133441) - 3.13: Abort from failed assertion in `_PyEval_EvalFrameDefault`

```python

```

- Issue Number: 133441
- Date filed: 05/05/2025
- Date closed: 
- Kind: Abort/AssertionError
- Configuration:
- Python versions: 3.13
- Status: open
- PRs (author):
  - []() ()

<details><summary>Backtrace/error message:</summary>
<p>


```shell

```
</p>
</details>

----------

