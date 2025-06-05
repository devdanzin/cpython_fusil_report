# Fuzzing CPython with fusil

## Introduction

This report presents the issues found by fuzzing
[CPython](https://github.com/python/cpython) with
[fusil](https://github.com/devdanzin/fusil), a tool created by
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

In this report, 'fusil' refers to the Python fuzzer based on the fusil
library, originally by Stinner and enhanced for this campaign by Diniz.

Fusil works by generating source files containing random calls using
random and/or interesting arguments, then monitoring the execution and
output of each source file. It usually finds crashes resulting from the
processing of invalid objects and unexpected call patterns.

This campaign isn't the first time fusil has been used to fuzz CPython:
in the period of 2007 to 2013, Stinner reported
[over 40 issues](https://web.archive.org/web/20160828100445/http://fusil.readthedocs.io/python.html),
while Diniz reported
[5 issues](https://github.com/search?q=repo%3Apython%2Fcpython+fusil&type=issues&s=created&o=asc&p=1).
Out of these issues, 4 were considered release blockers at the time. There
was then a hiatus in fusil development from 2015 (version 1.5, published
by Stinner) to 2024.

Since Stinner's last version, new features have been added to fusil by
Diniz. These features include running the generated code in parallel
threads, testing class instances in addition to classes and functions,
and using new interesting objects and values as inputs, all of which
found new crashes. Other new features, such as running the code
asynchronously or mangling objects by replacing some of their attributes,
haven't found any issues.

## Fuzzing environment and procedures

Fuzzing has started in late October 2024 and concluded as of early May
2025, meaning this report covers a period of approximately 6 months. It
has been conducted on a free AWS EC2 instance, a free AWS LightSail
instance (for 3 months), 3 free Oracle Cloud instances (2 x64, 1 ARM), a
personal desktop computer and a personal laptop, all running Linux.

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
- CPython configurations: debug, release, optimized, default (GIL-enabled),
free-threaded, JITted, ASAN-enabled

A hit is defined as a fuzzing session where either the process ends
abnormally (a segmentation fault, an abort etc.) or a keyword indicating
abnormal conditions is matched in the output, e.g. "SystemError",
"Fatal Python error". Many false positives, especially in the beginning
of the fuzzing campaign, were recorded as hits. These became rarer as
keywords were tightened and known problematic modules were skipped by
adding them to filter lists.

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
- Issues filled: 52 (X valid, 43 closed, 9 open)
- Resulting PRs: 98 (Y open, Z closed)

The 52 issues filled correspond roughly to 30% of all the crashes (issues
with "type-crash" label) and 2% of all issues (including features requests,
bugs and invalid issues) reported in the CPython issue tracker during the
period covered by this report. The 52 reported issues led to a significant
amount of corrective activity, with a total of 98 pull requests (PRs) being
created to address them.

Analysis of the 43 closed issues for which data was available indicates
that the median time to close an issue was 5 days, with an average of
approximately 20 days. This relatively quick turnaround for many issues
highlights the CPython development community's responsiveness to reported
defects

Hits and new issues don't seem to appear at a steady pace. Apparently,
there are long periods of no or nearly no new findinxgs, followed by rapid
accumulation of new results when new features are added to fusil, or
when new CPython versions and/or configurations are added to the fuzzing
pool. Repeated hits usually stop being found when the underlying issue
is fixed in CPython, hence the high number of hits recorded. In special
cases, suppressions for specific bugs are added, also stopping repeated
hits for them.

The temporal pattern of issue discovery and resolution throughout the fuzzing campaign is visualized in Figure X (see `issues_created_closed_per_week_plot.png`). This bar chart displays the number of issues created (blue bars) and closed (red bars) on a weekly basis, spanning from week 44 of 2024 through week 19 of 2025. The X-axis represents the week number, transitioning from 2024 into 2025 (e.g., W52 '24, W01 '25), while the Y-axis quantifies the number of issues, ranging from 0 to 10.

Several distinct phases of activity are observable:

* **Initial Burst (Weeks 44-50, 2024):** The campaign commenced with a significant number of new issues being opened, peaking at 9 issues in the first week (W44 '24). This initial surge gradually declined over the subsequent weeks. Issue closures began more modestly, with 2 issues closed in week 44, ramping up to a peak of 6 issues closed in week 48.
* **Mid-Campaign Lull (Week 51, 2024 - Week 13, 2025):** Following the initial phase, there was a marked decrease in the reporting of new issues. Specifically, no new issues were opened between week 51 of 2024 and week 5 of 2025. A small number of existing issues were closed during this period (e.g., in W51 '24 and W03 '25). A brief resurgence occurred in week 6 of 2025 with two new issues opened. This was followed by another quiet period for new discoveries until week 14.
* **Second Wave of Discoveries (Weeks 14-16, 2025):** A renewed period of activity was observed starting week 14 of 2025, with a total of 12 new issues opened over these three weeks. Issue closures also saw an uptick during this timeframe.
* **Later Period (Weeks 17-19, 2025):** The final weeks covered by the graph show minimal to no new issue creation, with some ongoing closure activity.

The temporal pattern of issue creation shows that the highest number of
issues were found when CPython was in a "fusil-naive" state, where no
fuzzing with this tool had happened for a decade. This corresponds to the
35 issues found from October 31 to December 12 2024.

Attempting to correlate these observed patterns in issue discovery with specific developments in the fusil fuzzer or the fuzzing campaign's setup offers some plausible insights, although a detailed history of fusil's feature enhancements prior to November 2024 is not fully captured in the available commit logs. Nevertheless, two periods of increased issue yield appear to align with notable changes:

1.  The **initial high rate of issue discovery** (peaking between week 44 and week 48 of 2024) corresponds with the commencement of the fuzzing campaign against a relatively "fusil-naive" CPython. Additionally, work on enabling and stabilizing threaded execution within fusil occurred around late November 2024 (e.g., commits `fd6fddea` and `146a1654`), a feature noted in prior context as effective in finding new crashes. This confluence of factors likely contributed to the significant number of defects uncovered early in the campaign.
2.  A **subsequent resurgence in issue reporting during weeks 14-16 of 2025** (early to mid-April) aligns closely with a series of enhancements to fusil's input generation capabilities. Specifically, commits from early April 2025 introduced support for "weird_classes" (subclasses of core types with unusual behavior, `commit 80696090`), "tricky typing values" (`commit 64451923`), "new weird instances" (`commit 01e7fccc`), and basic support for Numpy arrays as inputs (`commit aefb7644`). The timing suggests these new input types and object generation strategies were effective in exercising different code paths and uncovering a fresh set of defects.

While other fusil modifications, such as experimental JIT fuzzing (December 2024) or the introduction of various CPython configurations to the fuzzing pool (which, according to issue data, largely occurred at the campaign's outset), did not show such distinct correlations with new issue spikes, the enhancements to input diversity and execution models appear to have had a more pronounced impact on discovery rates.




| Issue Number |       Status       | Date filed | Date closed | Days open |        Kind        |   Configuration  | Python versions          | Component | Affected files |                   PRs                          | Number of PRs |                       PR authors                       |
|--------------|--------------------|------------|-------------|-----------|--------------------|------------------|--------------------------|-----------|----------------|------------------------------------------------|---------------|--------------------------------------------------------|
|    126219    | Open               | 30/10/2024 |             |           | Segmentation Fault | Release          | 3.12, 3.13, 3.14         |           |                |                                                |       0       |                                                        |
|    126220    | Closed-Completed   | 31/10/2024 | 06/11/2024  |           | Segmentation Fault | Release          | 3.12, 3.13, 3.14         |           |                | 126233, 126271, 126310, 126311, 126402         |       5       | @sobolevn, @erlend-aasland                             |
|    126221    | Closed-Not-Planned | 31/10/2024 | 31/10/2024  |           | Segmentation Fault | JIT              | 3.13, 3.14               |           |                | 126507                                         |       1       | @markshannon                                           |
|    126223    | Closed-Completed   | 31/10/2024 | 31/10/2024  |           | Abort              | Debug            | 3.13, 3.14               |           |                | 126224, 126242                                 |       2       | @ZeroIntensity, @sobolevn, @picnixz                    |
|    126312    | Closed-Completed   | 01/11/2024 | 15/11/2024  |           | Abort              | Free-Threaded    | 3.13, 3.14               |           |                | 126338, 126866                                 |       2       | @ZeroIntensity, @skirpichev                            |
|    126313    | Closed-Completed   | 01/11/2024 | 04/11/2024  |           | Abort              | Debug            | 3.13, 3.14               |           |                | 126351, 126493                                 |       2       | @picnixz                                               |
|    126314    | Closed-Completed   | 01/11/2024 | 14/03/2025  |           | Segmentation Fault | Free-Threaded    | 3.13, 3.14               |           |                |                                                |       0       |                                                        |
|    126315    | Open               | 01/11/2024 |             |           | Abort              | Free-Threaded    | 3.13, 3.14               |           |                |                                                |       0       |                                                        |
|    126316    | Closed-Completed   | 01/11/2024 | 21/11/2024  |           | Segmentation Fault | Free-Threaded    | 3.13, 3.14               |           |                | 126488, 126504, 126506, 127055, 127104         |       5       | @vstinner                                              |
|    126341    | Closed-Completed   | 03/11/2024 | 13/11/2024  |           | Abort              | Release          | 3.12, 3.13, 3.14         |           |                | 126759, 126778, 126779                         |       3       | @ritvikpasham, @ZeroIntensity, @vstinner, @sobolevn    |
|    126366    | Closed-Completed   | 03/11/2024 | 18/04/2025  |           | Abort              | Free-Threaded    | 3.13, 3.14               |           |                | 126369, 126371, 132693                         |       3       | @ZeroIntensity, @Fidget-Spinner, @kumaraditya303       |
|    126455    | Closed-Completed   | 05/11/2024 | 06/11/2024  |           | Segmentation Fault | Release          | 3.12, 3.13, 3.14         |           |                | 126481, 126486, 126487                         |       3       | @vstinner                                              |
|    126456    | Closed-Completed   | 05/11/2024 | 13/11/2024  |           | Segmentation Fault | Release          | 3.13, 3.14               |           |                | 126472, 126790                                 |       2       | @vstinner                                              |
|    126461    | Closed-Completed   | 05/11/2024 | 06/11/2024  |           | Abort              | Debug            | 3.12, 3.13, 3.14         |           |                | 126485, 126495, 126496                         |       3       | @vstinner                                              |
|    126594    | Closed-Completed   | 08/11/2024 | 24/11/2024  |           | Abort              | Debug            | 3.12, 3.13, 3.14         |           |                | 126754, 127004, 127005                         |       3       | @vstinner, @JelleZijlstra                              |
|    126595    | Closed-Completed   | 08/11/2024 | 12/11/2024  |           | Abort              | Debug            | 3.12, 3.13, 3.14         |           |                | 126617, 126739, 126740                         |       3       | @picnixz                                               |
|    126644    | Closed-Not-Planned | 10/11/2024 | 11/01/2025  |           | Abort              | Free-Threaded    | 3.13, 3.14               |           |                | 126696                                         |       1       | @ZeroIntensity                                         |
|    126654    | Closed-Completed   | 10/11/2024 | 11/11/2024  |           | Segmentation Fault | Release          | 3.13, 3.14               |           |                | 126678, 126681                                 |       2       | @sobolevn                                              |
|    126876    | Closed-Completed   | 15/11/2024 | 14/12/2024  |           | Abort              | Debug            | 3.12, 3.13, 3.14         |           |                | 126968, 127002, 127003, 127517                 |       4       | @vstinner                                              |
|    126881    | Closed-Completed   | 15/11/2024 | 29/11/2024  |           | Segmentation Fault | Release          | 3.12, 3.13, 3.14         |           |                | 126901, 126904, 127395                         |       3       | @picnixz, @kumaraditya303                              |
|    126884    | Open               | 15/11/2024 |             |           | Segmentation Fault | Free-Threaded    | 3.13, 3.14               |           |                |                                                |       0       |                                                        |
|    126895    | Closed-Completed   | 16/11/2024 | 17/03/2025  |           | Segmentation Fault | Free-Threaded    | 3.13, 3.14               |           |                | 131208                                         |       1       | @tom-pytel                                             |
|    126907    | Closed-Completed   | 16/11/2024 | 16/12/2024  |           | Segmentation Fault | Free-Threaded    | 3.13, 3.14               |           |                | 126908, 127935                                 |       2       | @ZeroIntensity                                         |
|    127085    | Closed-Completed   | 21/11/2024 | 16/12/2024  |           | Abort              | Free-Threaded    | 3.13, 3.14               |           |                | 127412, 128019                                 |       2       | @LindaSummer, @freakboy3742                            |
|    127165    | Closed-Completed   | 22/11/2024 | 01/12/2024  |           | Segmentation Fault | Release          | 3.13, 3.14               |           |                | 127199, 127463                                 |       2       | @ZeroIntensity                                         |
|    127182    | Closed-Completed   | 23/11/2024 | 25/11/2024  |           | Abort              | Debug            | 3.13, 3.14               |           |                | 127219, 127262, 127263                         |       3       | @sobolevn, @vstinner                                   |
|    127190    | Closed-Completed   | 23/11/2024 | 28/11/2024  |           | Segmentation Fault | Release          | 3.13, 3.14               |           |                | 127366, 127367, 127368                         |       3       | @vstinner                                              |
|    127192    | Closed-Not-Planned | 23/11/2024 | 23/11/2024  |           | Segmentation Fault | Free-Threaded    | 3.13, 3.14               |           |                |                                                |       0       |                                                        |
|    127196    | Closed-Completed   | 23/11/2024 | 09/01/2025  |           | Segmentation Fault | Release          | 3.13, 3.14               |           |                | 127220, 128689                                 |       2       | @sobolevn                                              |
|    127208    | Closed-Completed   | 24/11/2024 | 29/11/2024  |           | Abort              | Debug            | 3.12, 3.13, 3.14         |           |                | 127400, 127418, 127419                         |       3       | @vstinner                                              |
|    127234    | Open               | 24/11/2024 |             |           | Abort              | Debug            | 3.13, 3.14               |           |                |                                                |       0       |                                                        |
|    127235    | Open               | 24/11/2024 |             |           | Abort              | Free-Threaded    | 3.14                     |           |                |                                                |       0       |                                                        |
|    127316    | Closed-Completed   | 27/11/2024 | 29/11/2024  |           | Abort              | Free-Threaded    | 3.13, 3.14               |           |                | 127399, 127422                                 |       2       | @kumaraditya303                                        |
|    127603    | Closed-Completed   | 04/12/2024 | 11/12/2024  |           | Abort              | Debug            | 3.12                     |           |                | 127605                                         |       1       | @markshannon                                           |
|    127836    | Closed-Not-Planned | 11/12/2024 | 23/02/2025  |           | Abort              | Debug            | 3.12                     |           |                |                                                |       0       |                                                        |
|    127870    | Closed-Completed   | 12/12/2024 | 13/12/2024  |           | Segmentation Fault | Release          | 3.12, 3.13, 3.14         |           |                | 127872, 127917, 127918                         |       3       | @vstinner                                              |
|    129573    | Open               | 02/02/2025 |             |           | Abort              | Debug            | 3.12, 3.13, 3.14         |           |                | 129574, 130997                                 |       2       | @devdanzin                                             |
|    129766    | Closed-Completed   | 07/02/2025 | 07/02/2025  |           | Abort              | Debug            | 3.14                     |           |                | 129771                                         |       1       | @sobolevn                                              |
|    131580    | Closed-Completed   | 22/03/2025 | 25/03/2025  |           | Segmentation Fault | Free-Threaded    | 3.14                     |           |                |                                                |       0       |                                                        |
|    131998    | Closed-Completed   | 02/04/2025 | 08/04/2025  |           | Segmentation Fault | Release          | 3.13, 3.14               |           |                | 132000, 132262                                 |       2       | @ZeroIntensity, @sobolevn, @vstinner, @markshannon     |
|    132002    | Closed-Completed   | 02/04/2025 | 02/04/2025  |           | Segmentation Fault | Release          | 3.12, 3.13, 3.14         |           |                | 132003, 132007, 132008                         |       3       | @sobolevn                                              |
|    132011    | Closed-Completed   | 02/04/2025 | 06/04/2025  |           | Abort              | Debug            | 3.13, 3.14               |           |                | 132018, 132161                                 |       2       | @sobolevn                                              |
|    132171    | Closed-Completed   | 06/04/2025 | 07/04/2025  |           | Abort              | Debug            | 3.13, 3.14               |           |                | 132173, 132219                                 |       2       | @sobolevn                                              |
|    132176    | Closed-Completed   | 06/04/2025 | 15/04/2025  |           | Abort              | Debug            | 3.13, 3.14               |           |                | 132212, 132548                                 |       2       | @sobolevn                                              |
|    132250    | Closed-Completed   | 08/04/2025 | 08/04/2025  |           | Abort              | Debug            | 3.13, 3.14               |           |                | 132251, 132281                                 |       2       | @gaogaotiantian                                        |
|    132296    | Open               | 09/04/2025 |             |           | Segmentation Fault | Free-Threaded    | 3.14                     |           |                | 132298                                         |       1       | @ZeroIntensity                                         |
|    132386    | Closed-Completed   | 11/04/2025 | 11/04/2025  |           | Segmentation Fault | Release          | 3.14                     |           |                | 132412                                         |       1       | @tomasr8                                               |
|    132461    | Open               | 13/04/2025 |             |           | Abort              | Debug            | 3.14                     |           |                | 132462                                         |       1       | @dura0ok                                               |
|    132551    | Closed-Completed   | 15/04/2025 | 08/05/2025  |           | Segmentation Fault | Free-Threaded    | 3.13, 3.14               |           |                | 132616                                         |       1       | @tom-pytel                                             |
|    132707    | Closed-Not-Planned | 18/04/2025 | 18/04/2025  |           | Segmentation Fault | Free-Threaded    | 3.14                     |           |                |                                                |       0       |                                                        |
|    132713    | Closed-Completed   | 19/04/2025 | 23/04/2025  |           | Segmentation Fault | Free-Threaded    | 3.13, 3.14               |           |                | 132801, 132802, 132809, 132811, 132839, 132899 |       6       | @vstinner                                              |
|    133441    | Open               | 05/05/2025 |             |           | Abort              | Debug            | 3.13                     |           |                | 133446                                         |       1       | @vstinner                                              |
_Table: Issue number x Kind, Configuration, Python version, Status, number of PRs_

Each issue that resulted from the reported fuzzing effort is detailed
in the **Findings** section in the **Appendix**.

| Kind                 | Number of Issues |
|----------------------|------------------|
| Segfault/Crash       | 23               |
| Abort/AssertionError | 22               |
| SystemError          | 2                |
| Fatal Python Error   | 2                |
| Unknown              | 3                |
| **Total**            | **52**           |

Even though abort issues only affect debug builds directly, in many cases
they point to causes that would also create problems in release builds.
Segfault issues sound more serious, but some were very shallow crashes in
seldom used corners of CPython's standard librady.

| Configuration   | Number of Issues |
|-----------------|------------------|
| Debug           | 19               |
| Free-Threaded   | 18               |
| Release         | 14               |
| JIT             | 1                |
| **Total**       | **52**           |

The high number of issues resulting in aborts and the fact that most
segfaults also work on them make debug builds the most fruitful
configuration, followed by free-threaded builds.

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
removed or aren't added as versions leave the maintainance window. To
complement this field, versions are also collected from the PRs for an
issue.

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
- Status: Open
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
- Date closed: 06/11/2024
- Kind: Segmentation Fault
- Configuration: Release
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

This issue was closed in favor of https://github.com/python/cpython/issues/126222,
even though it was filed first, because the other issue had much better
information about the bug. The PR for that other issue is referenced here.

```python
import sre_constants
sre_constants._makecodes("", {}, 10)
```

- Issue Number: 126221
- Date filed: 31/10/2024
- Date closed: 31/10/2024
- Kind: Segmentation Fault
- Configuration: JIT
- Python versions: 3.13, 3.14
- Status: Closed-Not-Planned
- PRs (author):
  - [126507](https://github.com/python/cpython/pull/126507) (@markshannon)

<details><summary>Backtrace/error message:</summary>
<p>


```shell
Program received signal SIGSEGV, Segmentation fault.
_PyEval_EvalFrameDefault (tstate=0x555555b3f440 <_PyRuntime+313216>, frame=0x7ffff7fb0098, throwflag=<optimized out>) at Python/generated_cases.c.h:6753
6753                PyStackRef_CLOSE(value);
(gdb) bt
#0  _PyEval_EvalFrameDefault (tstate=0x555555b3f440 <_PyRuntime+313216>, frame=0x7ffff7fb0098,
    throwflag=<optimized out>) at Python/generated_cases.c.h:6753
#1  0x00005555557a9bac in _PyEval_EvalFrame (throwflag=0, frame=0x7ffff7fb0020,
    tstate=0x555555b3f440 <_PyRuntime+313216>) at ./Include/internal/pycore_ceval.h:116
#2  _PyEval_Vector (args=0x0, argcount=0, kwnames=0x0, locals=0x7ffff7a18c00, func=0x7ffff7a035e0,
    tstate=0x555555b3f440 <_PyRuntime+313216>) at Python/ceval.c:1886
#3  PyEval_EvalCode (co=co@entry=0x7ffff7a3a010, globals=globals@entry=0x7ffff7a18c00,
    locals=locals@entry=0x7ffff7a18c00) at Python/ceval.c:662
#4  0x000055555583aca8 in run_eval_code_obj (locals=0x7ffff7a18c00, globals=0x7ffff7a18c00,
    co=0x7ffff7a3a010, tstate=0x555555b3f440 <_PyRuntime+313216>) at Python/pythonrun.c:1338
#5  run_eval_code_obj (tstate=0x555555b3f440 <_PyRuntime+313216>, co=0x7ffff7a3a010,
    globals=0x7ffff7a18c00, locals=0x7ffff7a18c00) at Python/pythonrun.c:1305
#6  0x000055555583af28 in run_mod (mod=mod@entry=0x555555c61fb0, filename=filename@entry=0x7ffff7a72130,
    globals=globals@entry=0x7ffff7a18c00, locals=locals@entry=0x7ffff7a18c00,
    flags=flags@entry=0x7fffffffdf28, arena=arena@entry=0x7ffff7b5e250, interactive_src=0x7ffff7b8dbc0,
    generate_new_source=0) at Python/pythonrun.c:1423
#7  0x000055555583d5a4 in _PyRun_StringFlagsWithName (generate_new_source=0, flags=0x7fffffffdf28,
    locals=0x7ffff7a18c00, globals=0x7ffff7a18c00, start=257, name=0x7ffff7a72130,
    str=0x7ffff7a49c10 "import sre_constants; sre_constants._makecodes('', {}, 10)\n")
    at Python/pythonrun.c:1222
#8  _PyRun_SimpleStringFlagsWithName (
    command=0x7ffff7a49c10 "import sre_constants; sre_constants._makecodes('', {}, 10)\n",
    name=name@entry=0x5555558e3520 "<string>", flags=flags@entry=0x7fffffffdf28) at Python/pythonrun.c:548
```
</p>
</details>

----------


#### 4- [126223](https://github.com/python/cpython/issues/126223) - `SystemError` caused by `_interpreters.create()` with invalid unicode argument

```python
$ ./python -c "import _interpreters; _interpreters.create('\udc80')"
```

- Issue Number: 126223
- Date filed: 31/10/2024
- Date closed: 31/10/2024
- Kind: Abort
- Configuration: Debug
- Python versions: 3.13, 3.14
- Status: Closed-Completed
- PRs (author):
  - [126224](https://github.com/python/cpython/pull/126224) (@ZeroIntensity)
  - [126242](https://github.com/python/cpython/pull/126242) (@ZeroIntensity, @sobolevn, @picnixz)

<details><summary>Backtrace/error message:</summary>
<p>


```shell
Fatal Python error: _Py_CheckFunctionResult: a function returned a result with an exception set
Python runtime state: initialized
UnicodeEncodeError: 'utf-8' codec can't encode character '\udc80' in position 0: surrogates not allowed

The above exception was the direct cause of the following exception:

SystemError: <built-in function create> returned a result with an exception set

Current thread 0x00007f0234dca740 (most recent call first):
  File "<string>", line 1 in <module>
Aborted
```
</p>
</details>

----------


#### 5- [126312](https://github.com/python/cpython/issues/126312) - GC aborts in debug no-gil build

```python
import gc
gc.freeze()
gc.is_finalized(lambda: None)
gc.collect()
gc.unfreeze()
gc.collect()
```

- Issue Number: 126312
- Date filed: 01/11/2024
- Date closed: 15/11/2024
- Kind: Abort
- Configuration: Free-Threaded
- Python versions: 3.13, 3.14
- Status: Closed-Completed
- PRs (author):
  - [126338](https://github.com/python/cpython/pull/126338) (@ZeroIntensity)
  - [126866](https://github.com/python/cpython/pull/126866) (@ZeroIntensity, @skirpichev)

<details><summary>Backtrace/error message:</summary>
<p>


```shell
Python/gc_free_threading.c:550: validate_refcounts: Assertion "!gc_is_unreachable(op)" failed: object should not be marked as unreachable yet
Enable tracemalloc to get the memory block allocation traceback

object address  : 0x200007373f0
object refcount : 1152921504606846977
object type     : 0x55adadc26660
object type name: dict
object repr     : {'__name__': '__main__', '__doc__': None, '__package__': None, '__loader__': <_frozen_importlib_external.SourceFileLoader object at 0x20000330a20>, '__spec__': None, '__builtins__': <module 'builtins' (built-in)>, '__file__': '/home/fusil/python-61/gc-assertion-abort-2/source.py', '__cached__': None, 'gc': <module 'gc' (built-in)>}

Fatal Python error: _PyObject_AssertFailed: _PyObject_AssertFailed
Python runtime state: initialized

Current thread 0x00007f1b47a64740 (most recent call first):
  Garbage-collecting
  File "/home/fusil/python-61/gc-assertion-abort-2/source.py", line 6 in <module>
Aborted
```
</p>
</details>

----------


#### 6- [126313](https://github.com/python/cpython/issues/126313) - `curses.napms()` aborts with a `SystemError`

```python
import curses
curses.napms(37)
```

- Issue Number: 126313
- Date filed: 01/11/2024
- Date closed: 04/11/2024
- Kind: Abort
- Configuration: Debug
- Python versions: 3.13, 3.14
- Status: Closed-Completed
- PRs (author):
  - [126351](https://github.com/python/cpython/pull/126351) (@picnixz)
  - [126493](https://github.com/python/cpython/pull/126493) (@picnixz)

<details><summary>Backtrace/error message:</summary>
<p>


```shell
Fatal Python error: _Py_CheckFunctionResult: a function returned a result with an exception set
Python runtime state: initialized
_curses.error: must call initscr() first

The above exception was the direct cause of the following exception:

SystemError: <built-in function napms> returned a result with an exception set

Current thread 0x00007fe41a8c3740 (most recent call first):
  File "/home/fusil/python-73/curses-fatal/source.py", line 3 in <module>
Aborted
```
</p>
</details>

----------


#### 7- [126314](https://github.com/python/cpython/issues/126314) - Running `tracemalloc` in threads segfaults on no-gil
Fixed by addressing another issue (#128679).

```python
# This segfaults with PYTHON_GIL=0, works with PYTHON_GIL=1
from threading import Thread
import tracemalloc

alive = [
    Thread(target=tracemalloc.take_snapshot, args=()),
    Thread(target=tracemalloc.clear_traces, args=()),
]

tracemalloc.start()
import inspect # This seems to be important, has to happen after .start()

for obj in alive:
    print('START', obj)
    obj.start()
```

- Issue Number: 126314
- Date filed: 01/11/2024
- Date closed: 14/03/2025
- Kind: Segmentation Fault
- Configuration: Free-Threaded
- Python versions: 3.13, 3.14
- Status: Closed-Completed
- PRs (author):
  - None

<details><summary>Backtrace/error message:</summary>
<p>


```shell
frame_to_pyobject (frame=frame@entry=0x555555e78eac) at Python/tracemalloc.c:994
994         PyTuple_SET_ITEM(frame_obj, 0, Py_NewRef(frame->filename));
(gdb) bt
#0  frame_to_pyobject (
    frame=frame@entry=0x555555e78eac)
    at Python/tracemalloc.c:994
#1  0x000055555591edbd in traceback_to_pyobject (
    traceback=0x555555e78ea0,
    intern_table=intern_table@entry=0x7ffff00019c0)
    at Python/tracemalloc.c:1024
#2  0x000055555591efee in trace_to_pyobject (
    domain=<optimized out>, trace=0x7ffff000ee70,
    intern_tracebacks=0x7ffff00019c0)
    at Python/tracemalloc.c:1070
#3  0x000055555591f46d in tracemalloc_get_traces_fill (traces=<optimized out>, key=<optimized out>,
    value=<optimized out>,
    user_data=0x7ffff7ba7880)
    at Python/tracemalloc.c:1188
#4  0x00005555558b7f49 in _Py_hashtable_foreach (
    ht=0x7ffff0001ab0,
    func=func@entry=0x55555591f44a <tracemalloc_get_traces_fill>,
    user_data=user_data@entry=0x7ffff7ba7880)
    at Python/hashtable.c:275
#5  0x0000555555920889 in _PyTraceMalloc_GetTraces
    () at Python/tracemalloc.c:1470
#6  0x0000555555957b44 in _tracemalloc__get_traces_impl (module=<optimized out>)
    at ./Modules/_tracemalloc.c:57
```
</p>
</details>

----------


#### 8- [126315](https://github.com/python/cpython/issues/126315) - `tracemalloc` aborts when run from threads in no-gil

```python
from threading import Thread
import _tracemalloc

alive = [
    Thread(target=_tracemalloc.start, args=(
        (memoryview(bytearray(b"abc\xe9\xff")),))),
    Thread(target=_tracemalloc.start, args=()),
    Thread(target=_tracemalloc.get_traceback_limit, args=()),
    Thread(target=_tracemalloc.start, args=()),
    Thread(target=_tracemalloc.stop, args=()),
    Thread(target=_tracemalloc.reset_peak, args=()),
    Thread(target=_tracemalloc.get_tracemalloc_memory, args=())
]

for obj in alive:
    print('START', obj)
    try:
        obj.start()
    except Exception:
        pass
```

- Issue Number: 126315
- Date filed: 01/11/2024
- Date closed:
- Kind: Abort
- Configuration: Free-Threaded
- Python versions: 3.13, 3.14
- Status: Open
- PRs (author):
  - None yet

<details><summary>Backtrace/error message:</summary>
<p>


```shell
python: Python/tracemalloc.c:445: tracemalloc_remove_trace: Assertion `tracemalloc_config.tracing' failed.
Aborted

# Or

python: Python/tracemalloc.c:469: tracemalloc_add_trace: Assertion `tracemalloc_config.tracing' failed.
Aborted
```
</p>
</details>

----------


#### 9- [126316](https://github.com/python/cpython/issues/126316) - `grp` is not thread safe

```python
from threading import Thread
import grp

for x in range(5000):
    alive = [
        Thread(target=grp.getgrgid, args=(1,)),
        Thread(target=grp.getgrall),
        Thread(target=grp.getgrnam, args=('root',)),
    ]

    for obj in alive:
        print('START', obj)
        obj.start()
```

- Issue Number: 126316
- Date filed: 01/11/2024
- Date closed: 21/11/2024
- Kind: Segmentation Fault
- Configuration: Free-Threaded
- Python versions: 3.13, 3.14
- Status: Closed-Completed
- PRs (author):
  - [126488](https://github.com/python/cpython/pull/126488) (@vstinner)
  - [126504](https://github.com/python/cpython/pull/126504) (@vstinner)
  - [126506](https://github.com/python/cpython/pull/126506) (@vstinner)
  - [127055](https://github.com/python/cpython/pull/127055) (@vstinner)
  - [127104](https://github.com/python/cpython/pull/127104) (@vstinner)

<details><summary>Backtrace/error message:</summary>
<p>


```shell
(gdb) bt
#0  __strlen_avx2 ()
    at ../sysdeps/x86_64/multiarch/strlen-avx2.S:74
#1  0x00005555557ad3cb in PyUnicode_DecodeFSDefault (
    s=s@entry=0x3838323432353a78 <error: Cannot access memory at address 0x3838323432353a78>) at Objects/unicodeobject.c:4058
#2  0x00007ffff7c3f952 in mkgrent (
    module=module@entry=0x20000795b80, p=<optimized out>)
    at ./Modules/grpmodule.c:83
#3  0x00007ffff7c3fc41 in grp_getgrall_impl (
    module=0x20000795b80) at ./Modules/grpmodule.c:291
#4  0x00007ffff7c3fcad in grp_getgrall (
    module=<optimized out>, _unused_ignored=<optimized out>)
    at ./Modules/clinic/grpmodule.c.h:83
#5  0x00005555556fca83 in cfunction_vectorcall_NOARGS (
    func=0x2000079f820, args=<optimized out>,
    nargsf=<optimized out>, kwnames=<optimized out>)
    at Objects/methodobject.c:495
#6  0x000055555567b4bc in _PyVectorcall_Call (
    tstate=tstate@entry=0x555555d2ac70,
    func=0x5555556fc8b5 <cfunction_vectorcall_NOARGS>,
    callable=callable@entry=0x2000079f820,
    tuple=tuple@entry=0x555555c5d1d8 <_PyRuntime+128984>,
    kwargs=kwargs@entry=0x2001a0400d0) at Objects/call.c:273
#7  0x000055555567b894 in _PyObject_Call (
    tstate=0x555555d2ac70,
    callable=callable@entry=0x2000079f820,
    args=args@entry=0x555555c5d1d8 <_PyRuntime+128984>,
    kwargs=kwargs@entry=0x2001a0400d0) at Objects/call.c:348
#8  0x000055555567b8f1 in PyObject_Call (
    callable=callable@entry=0x2000079f820,
    args=args@entry=0x555555c5d1d8 <_PyRuntime+128984>,
    kwargs=kwargs@entry=0x2001a0400d0) at Objects/call.c:373
```
</p>
</details>

----------


#### 10- [126341](https://github.com/python/cpython/issues/126341) - `SystemError` from calling `__iter__` on a released `memoryview`

```python
av = memoryview(b"something")
av.release()
av.__iter__()
```

- Issue Number: 126341
- Date filed: 03/11/2024
- Date closed: 13/11/2024
- Kind: Abort
- Configuration: Release
- Python versions: 3.12, 3.13, 3.14
- Status: Closed-Completed
- PRs (author):
  - [126759](https://github.com/python/cpython/pull/126759) (@ritvikpasham)
  - [126778](https://github.com/python/cpython/pull/126778) (@ritvikpasham, @ZeroIntensity, @vstinner, @sobolevn)
  - [126779](https://github.com/python/cpython/pull/126779) (@ritvikpasham, @ZeroIntensity, @vstinner, @sobolevn)

<details><summary>Backtrace/error message:</summary>
<p>


```shell
Fatal Python error: _Py_CheckFunctionResult: a function returned a result with an exception set
Python runtime state: initialized
ValueError: operation forbidden on released memoryview object

The above exception was the direct cause of the following exception:

SystemError: <method-wrapper '__iter__' of memoryview object at 0x200006a6050> returned a result with an exception set
Aborted
```
</p>
</details>

----------


#### 11- [126366](https://github.com/python/cpython/issues/126366) - Abort in free-threaded build due to mutation of `ChainMap` of a `Counter` in threads

```python
from threading import Thread
from collections import ChainMap, Counter

counter = Counter(range(100))
chainmap = ChainMap(counter)
chainmap2 = ChainMap(counter)

def mutate_removing():
    for x in range(10):
        chainmap.pop(list(chainmap.keys()).pop())
        chainmap2.pop(list(chainmap2.keys()).pop())

def mutate_adding():
    for x in range(50):
        chainmap[max(chainmap) + x + 1] = x
        chainmap2[max(chainmap2) + x + 1] = x

alive = []

for x in range(55):
    alive.append(Thread(target=mutate_removing, args=()))
    alive.append(Thread(target=mutate_adding, args=()))

for obj in alive:
    try:
        print('START', obj)
        obj.start()
    except Exception:
        pass
```

- Issue Number: 126366
- Date filed: 03/11/2024
- Date closed: 18/04/2025
- Kind: Abort
- Configuration: Free-Threaded
- Python versions: 3.13, 3.14
- Status: Closed-Completed
- PRs (author):
  - [126369](https://github.com/python/cpython/pull/126369) (@ZeroIntensity)
  - [126371](https://github.com/python/cpython/pull/126371) (@ZeroIntensity, @Fidget-Spinner)
  - [132693](https://github.com/python/cpython/pull/132693) (@kumaraditya303)

<details><summary>Backtrace/error message:</summary>
<p>


```shell
python: ./Include/internal/pycore_stackref.h:99: _PyStackRef_FromPyObjectSteal: Assertion `obj != NULL' failed.
Aborted
```
</p>
</details>

----------


#### 12- [126455](https://github.com/python/cpython/issues/126455) - Calling many methods on `_ssl._SSLSocket()` segfaults

```python
import _ssl
s = _ssl._SSLSocket()
s.shutdown()
```

- Issue Number: 126455
- Date filed: 05/11/2024
- Date closed: 06/11/2024
- Kind: Segmentation Fault
- Configuration: Release
- Python versions: 3.12, 3.13, 3.14
- Status: Closed-Completed
- PRs (author):
  - [126481](https://github.com/python/cpython/pull/126481) (@vstinner)
  - [126486](https://github.com/python/cpython/pull/126486) (@vstinner)
  - [126487](https://github.com/python/cpython/pull/126487) (@vstinner)

<details><summary>Backtrace/error message:</summary>
<p>


```shell
#0  0x00007ffff7b89129 in SSL_shutdown () from /lib/x86_64-linux-gnu/libssl.so.3
#1  0x00007ffff7c287bc in _ssl__SSLSocket_shutdown_impl (self=self@entry=0x20000572510) at ./Modules/_ssl.c:2710
#2  0x00007ffff7c28977 in _ssl__SSLSocket_shutdown (self=0x20000572510, _unused_ignored=<optimized out>)
    at ./Modules/clinic/_ssl.c.h:557
#3  0x0000555555694039 in method_vectorcall_NOARGS (func=<method_descriptor at remote 0x20000779380>, args=0x7fffffffd298,
    nargsf=<optimized out>, kwnames=<optimized out>) at Objects/descrobject.c:447
#4  0x000055555567ccec in _PyObject_VectorcallTstate (tstate=0x555555d2c2a0 <_PyRuntime+359904>,
    callable=<method_descriptor at remote 0x20000779380>, args=0x7fffffffd298, nargsf=9223372036854775809, kwnames=0x0)
    at ./Include/internal/pycore_call.h:167
#5  0x000055555567ce0b in PyObject_Vectorcall (callable=callable@entry=<method_descriptor at remote 0x20000779380>,
    args=args@entry=0x7fffffffd298, nargsf=<optimized out>, kwnames=kwnames@entry=0x0) at Objects/call.c:327
#6  0x0000555555841c09 in _PyEval_EvalFrameDefault (tstate=tstate@entry=0x555555d2c2a0 <_PyRuntime+359904>, frame=<optimized out>,
    throwflag=throwflag@entry=0) at Python/generated_cases.c.h:955
#7  0x000055555586fb1f in _PyEval_EvalFrame (throwflag=0, frame=<optimized out>, tstate=0x555555d2c2a0 <_PyRuntime+359904>)
    at ./Include/internal/pycore_ceval.h:116
#8  _PyEval_Vector (tstate=tstate@entry=0x555555d2c2a0 <_PyRuntime+359904>, func=func@entry=0x20000ad32d0,
    locals=locals@entry={'__name__': '__main__', '__doc__': None, '__package__': None, '__loader__': <type at remote 0x20000276e10>, '__spec__': None, '__builtins__': <module at remote 0x2000025c640>, '_ssl': <module at remote 0x20000778d60>, 's': <_ssl._SSLSocket at remote 0x20000572510>}, args=args@entry=0x0, argcount=argcount@entry=0, kwnames=kwnames@entry=0x0) at Python/ceval.c:1886
#9  0x000055555586fd6c in PyEval_EvalCode (co=co@entry=<code at remote 0x2000033f190>,
    globals=globals@entry={'__name__': '__main__', '__doc__': None, '__package__': None, '__loader__': <type at remote 0x20000276e10>, '__spec__': None, '__builtins__': <module at remote 0x2000025c640>, '_ssl': <module at remote 0x20000778d60>, 's': <_ssl._SSLSocket at remote 0x20000572510>},
    locals=locals@entry={'__name__': '__main__', '__doc__': None, '__package__': None, '__loader__': <type at remote 0x20000276e10>, '__spec__': None, '__builtins__': <module at remote 0x2000025c640>, '_ssl': <module at remote 0x20000778d60>, 's': <_ssl._SSLSocket at remote 0x20000572510>}) at Python/ceval.c:662
```
</p>
</details>

----------


#### 13- [126456](https://github.com/python/cpython/issues/126456) - `_pyrepl._minimal_curses.tigetstr` segfaults

```python
python -c "from _pyrepl._minimal_curses import tigetstr; tigetstr('')"
```

- Issue Number: 126456
- Date filed: 05/11/2024
- Date closed: 13/11/2024
- Kind: Segmentation Fault
- Configuration: Release
- Python versions: 3.13, 3.14
- Status: Closed-Completed
- PRs (author):
  - [126472](https://github.com/python/cpython/pull/126472) (@vstinner)
  - [126790](https://github.com/python/cpython/pull/126790) (@vstinner)

<details><summary>Backtrace/error message:</summary>
<p>


```shell
#0  __strlen_avx2 () at ../sysdeps/x86_64/multiarch/strlen-avx2.S:510
#1  0x00007ffff7c335ff in z_get (ptr=<optimized out>, size=<optimized out>) at ./Modules/_ctypes/cfield.c:1382
#2  0x00007ffff7c20f0a in Simple_get_value (self=0x200009b0fe0, _unused_ignored=<optimized out>) at ./Modules/_ctypes/_ctypes.c:5062
#3  0x0000555555691b7a in getset_get (self=self@entry=<getset_descriptor at remote 0x20000ac5410>,
    obj=obj@entry=<c_char_p() at remote 0x200009b0fe0>, type=<optimized out>) at Objects/descrobject.c:193
#4  0x000055555570a99d in _PyObject_GenericGetAttrWithDict (obj=<c_char_p() at remote 0x200009b0fe0>, name='value',
    dict=dict@entry=0x0, suppress=suppress@entry=0) at Objects/object.c:1659
#5  0x000055555570b538 in PyObject_GenericGetAttr (obj=<optimized out>, name=<optimized out>) at Objects/object.c:1741
#6  0x000055555570a740 in PyObject_GetAttr (v=v@entry=<c_char_p() at remote 0x200009b0fe0>, name='value') at Objects/object.c:1255
#7  0x000055555585be7e in _PyEval_EvalFrameDefault (tstate=tstate@entry=0x555555d2c2a0 <_PyRuntime+359904>, frame=0x7ffff7fb0088,
    throwflag=throwflag@entry=0) at ./Include/internal/pycore_stackref.h:74
#8  0x000055555586fb1f in _PyEval_EvalFrame (throwflag=0, frame=<optimized out>, tstate=0x555555d2c2a0 <_PyRuntime+359904>)
    at ./Include/internal/pycore_ceval.h:116
#9  _PyEval_Vector (tstate=tstate@entry=0x555555d2c2a0 <_PyRuntime+359904>, func=func@entry=0x20000ad32d0,
    locals=locals@entry={'__name__': '__main__', '__doc__': None, '__package__': None, '__loader__': <type at remote 0x20000276e10>, '__spec__': None, '__builtins__': <module at remote 0x2000025c640>, 'tigetstr': <function at remote 0x200008b24d0>},
    args=args@entry=0x0, argcount=argcount@entry=0, kwnames=kwnames@entry=0x0) at Python/ceval.c:1886
#10 0x000055555586fd6c in PyEval_EvalCode (co=co@entry=<code at remote 0x20000a87450>,
    globals=globals@entry={'__name__': '__main__', '__doc__': None, '__package__': None, '__loader__': <type at remote 0x20000276e10>, '__spec__': None, '__builtins__': <module at remote 0x2000025c640>, 'tigetstr': <function at remote 0x200008b24d0>},
    locals=locals@entry={'__name__': '__main__', '__doc__': None, '__package__': None, '__loader__': <type at remote 0x20000276e10>, '__spec__': None, '__builtins__': <module at remote 0x2000025c640>, 'tigetstr': <function at remote 0x200008b24d0>})
    at Python/ceval.c:662
#11 0x000055555595452a in run_eval_code_obj (tstate=tstate@entry=0x555555d2c2a0 <_PyRuntime+359904>, co=co@entry=0x20000a87450,
    globals=globals@entry={'__name__': '__main__', '__doc__': None, '__package__': None, '__loader__': <type at remote 0x20000276e10>, '__spec__': None, '__builtins__': <module at remote 0x2000025c640>, 'tigetstr': <function at remote 0x200008b24d0>},
    locals=locals@entry={'__name__': '__main__', '__doc__': None, '__package__': None, '__loader__': <type at remote 0x20000276e10>, '__spec__': None, '__builtins__': <module at remote 0x2000025c640>, 'tigetstr': <function at remote 0x200008b24d0>})
    at Python/pythonrun.c:1338
```
</p>
</details>

----------


#### 14- [126461](https://github.com/python/cpython/issues/126461) - Calling `_pickle.load` with a `MagicMock` results in `SystemError`/aborts

```python
python -c "from unittest.mock import MagicMock as MM; from _pickle import load; load(MM())"
```

- Issue Number: 126461
- Date filed: 05/11/2024
- Date closed: 06/11/2024
- Kind: Abort
- Configuration: Debug
- Python versions: 3.12, 3.13, 3.14
- Status: Closed-Completed
- PRs (author):
  - [126485](https://github.com/python/cpython/pull/126485) (@vstinner)
  - [126495](https://github.com/python/cpython/pull/126495) (@vstinner)
  - [126496](https://github.com/python/cpython/pull/126496) (@vstinner)

<details><summary>Backtrace/error message:</summary>
<p>


```shell
python: Objects/typeobject.c:5583: _PyType_LookupRef: Assertion `!PyErr_Occurred()' failed.
Aborted
```
</p>
</details>

----------


#### 15- [126594](https://github.com/python/cpython/issues/126594) - Failed assertion in typeobject.c::wrap_buffer for `b"".__buffer__(-2**31 - 1)`

```python
b"".__buffer__(-2**31 - 1)
```

- Issue Number: 126594
- Date filed: 08/11/2024
- Date closed: 24/11/2024
- Kind: Abort
- Configuration: Debug
- Python versions: 3.12, 3.13, 3.14
- Status: Closed-Completed
- PRs (author):
  - [126754](https://github.com/python/cpython/pull/126754) (@vstinner)
  - [127004](https://github.com/python/cpython/pull/127004) (@vstinner, @JelleZijlstra)
  - [127005](https://github.com/python/cpython/pull/127005) (@vstinner, @JelleZijlstra)

<details><summary>Backtrace/error message:</summary>
<p>


```shell
python: Objects/typeobject.c:9321: wrap_buffer: Assertion `_Py_STATIC_CAST(Py_ssize_t, _Py_STATIC_CAST(int, (flags))) == (flags)' failed.
Aborted
```
</p>
</details>

----------


#### 16- [126595](https://github.com/python/cpython/issues/126595) - Failed assertion in `itertoolsmodule.c: itertools_count_impl` for `count(sys.maxsize)`

```python
python -c "from sys import maxsize; from itertools import count; count(maxsize)"
```

- Issue Number: 126595
- Date filed: 08/11/2024
- Date closed: 12/11/2024
- Kind: Abort
- Configuration: Debug
- Python versions: 3.12, 3.13, 3.14
- Status: Closed-Completed
- PRs (author):
  - [126617](https://github.com/python/cpython/pull/126617) (@picnixz)
  - [126739](https://github.com/python/cpython/pull/126739) (@picnixz)
  - [126740](https://github.com/python/cpython/pull/126740) (@picnixz)

<details><summary>Backtrace/error message:</summary>
<p>


```shell
python: ./Modules/itertoolsmodule.c:3325: itertools_count_impl: Assertion `(cnt != PY_SSIZE_T_MAX && long_cnt == NULL && fast_mode) || (cnt == PY_SSIZE_T_MAX && long_cnt != NULL && !fast_mode)' failed.
Aborted (core dumped)
```
</p>
</details>

----------


#### 17- [126644](https://github.com/python/cpython/issues/126644) - `_interpreters` is not thread safe on the free-threaded build

```python
import _interpreters
from threading import Thread

def f(): pass

ints = []
for x in range(300):
    ints.append(_interpreters.create())

threads = []
for interpr in ints:
    threads.append(Thread(target=_interpreters.run_string, args=(interpr, "f()",)))
    threads.append(Thread(target=_interpreters.get_current, args=()))
    threads.append(Thread(target=_interpreters.destroy, args=(interpr,)))
    threads.append(Thread(target=_interpreters.list_all, args=()))
    threads.append(Thread(target=_interpreters.destroy, args=(interpr,)))
    threads.append(Thread(target=_interpreters.get_current, args=()))
    threads.append(Thread(target=_interpreters.get_main, args=()))
    threads.append(Thread(target=_interpreters.destroy, args=(interpr,)))
    threads.append(Thread(target=_interpreters.run_string, args=(interpr, "f()",)))

for thread in threads:
    try:
        print("START", thread)
        thread.start()
    except Exception:
        pass

for thread in threads:
    try:
        print("JOIN", thread)
        thread.join()
    except Exception:
        pass
```

- Issue Number: 126644
- Date filed: 10/11/2024
- Date closed: 11/01/2025
- Kind: Abort
- Configuration: Free-Threaded
- Python versions: 3.13, 3.14
- Status: Closed-Not-Planned
- PRs (author):
  - [126696](https://github.com/python/cpython/pull/126696) (@ZeroIntensity)

<details><summary>Backtrace/error message:</summary>
<p>


```shell
#0  __pthread_kill_implementation (no_tid=0, signo=6, threadid=140729519150656) at ./nptl/pthread_kill.c:44
#1  __pthread_kill_internal (signo=6, threadid=140729519150656) at ./nptl/pthread_kill.c:78
#2  __GI___pthread_kill (threadid=140729519150656, signo=signo@entry=6) at ./nptl/pthread_kill.c:89
#3  0x00007ffff7ce0476 in __GI_raise (sig=sig@entry=6) at ../sysdeps/posix/raise.c:26
#4  0x00007ffff7cc67f3 in __GI_abort () at ./stdlib/abort.c:79
#5  0x00007ffff7cc671b in __assert_fail_base (fmt=0x7ffff7e7b130 "%s%s%s:%u: %s%sAssertion `%s' failed.\n%n",
    assertion=0x555555aceaf4 "heap->size > 0", file=0x555555aceae0 "Python/index_pool.c", line=92, function=<optimized out>)
    at ./assert/assert.c:92
#6  0x00007ffff7cd7e96 in __GI___assert_fail (assertion=assertion@entry=0x555555aceaf4 "heap->size > 0",
    file=file@entry=0x555555aceae0 "Python/index_pool.c", line=line@entry=92,
    function=function@entry=0x555555aceb40 <__PRETTY_FUNCTION__.1> "heap_pop") at ./assert/assert.c:101
#7  0x00005555558caa1c in heap_pop (heap=<optimized out>) at Python/index_pool.c:92
#8  0x00005555558cac33 in _PyIndexPool_AllocIndex (pool=pool@entry=0x7ffff780f498) at Python/index_pool.c:173
#9  0x000055555568d9f0 in _Py_ReserveTLBCIndex (interp=interp@entry=0x7ffff780b020) at Objects/codeobject.c:2752
#10 0x0000555555951c33 in new_threadstate (interp=interp@entry=0x7ffff780b020, whence=whence@entry=5) at Python/pystate.c:1516
#11 0x0000555555953994 in _PyThreadState_NewBound (interp=interp@entry=0x7ffff780b020, whence=whence@entry=5)
    at Python/pystate.c:1578
#12 0x0000555555896ee9 in _enter_session (session=session@entry=0x7ffe24ff8740, interp=interp@entry=0x7ffff780b020)
    at Python/crossinterp.c:1548
#13 0x000055555589b9fb in _PyXI_Enter (session=session@entry=0x7ffe24ff8740, interp=interp@entry=0x7ffff780b020,
    nsupdates=nsupdates@entry=0x0) at Python/crossinterp.c:1711
#14 0x00007ffff7c3d217 in _run_in_interpreter (interp=interp@entry=0x7ffff780b020, codestr=0x200006182c8 "f()", codestrlen=3,
    shareables=shareables@entry=0x0, flags=1, p_excinfo=p_excinfo@entry=0x7ffe24ff8870) at ./Modules/_interpretersmodule.c:461
#15 0x00007ffff7c3d3ef in _interp_exec (self=self@entry=<module at remote 0x20000778b30>, interp=interp@entry=0x7ffff780b020,
    code_arg=<optimized out>, shared_arg=0x0, p_excinfo=p_excinfo@entry=0x7ffe24ff8870) at ./Modules/_interpretersmodule.c:950
#16 0x00007ffff7c3dc6b in interp_run_string (self=<module at remote 0x20000778b30>, args=args@entry=(9, 'f()'), kwds=kwds@entry={})
    at ./Modules/_interpretersmodule.c:1110
#17 0x000055555570145a in cfunction_call (func=func@entry=<built-in method run_string of module object at remote 0x20000778b30>,
    args=args@entry=(9, 'f()'), kwargs=kwargs@entry={}) at Objects/methodobject.c:551
#18 0x000055555567f69a in _PyObject_Call (tstate=0x5555560c09d0,
    callable=callable@entry=<built-in method run_string of module object at remote 0x20000778b30>, args=args@entry=(9, 'f()'),
    kwargs=kwargs@entry={}) at Objects/call.c:361
```
</p>
</details>

----------


#### 18- [126654](https://github.com/python/cpython/issues/126654) - `_interpreters.exec` with invalid parameters segfaults

```python
import _interpreters

_interpreters.exec(False, "aaaa", 1)
```

- Issue Number: 126654
- Date filed: 10/11/2024
- Date closed: 11/11/2024
- Kind: Segmentation Fault
- Configuration: Release
- Python versions: 3.13, 3.14
- Status: Closed-Completed
- PRs (author):
  - [126678](https://github.com/python/cpython/pull/126678) (@sobolevn)
  - [126681](https://github.com/python/cpython/pull/126681) (@sobolevn)

<details><summary>Backtrace/error message:</summary>
<p>


```shell
Program received signal SIGSEGV, Segmentation fault.
0x00005555557c4e1c in _PyXI_ApplyError (error=0x0) at Python/crossinterp.c:1057
1057        if (error->code == _PyXI_ERR_UNCAUGHT_EXCEPTION) {
(gdb) bt
#0  0x00005555557c4e1c in _PyXI_ApplyError (error=0x0) at Python/crossinterp.c:1057
#1  0x00007ffff79db912 in _run_in_interpreter (p_excinfo=0x7fffffffd0a0, flags=1, shareables=0x555555abe9d0 <_PyRuntime+14032>,
    codestrlen=<optimized out>, codestr=0x7ffff7a53358 "aaaa", interp=0x555555ad0e48 <_PyRuntime+88904>)
    at ./Modules/_interpretersmodule.c:463
#2  _interp_exec (interp=interp@entry=0x555555ad0e48 <_PyRuntime+88904>, code_arg=<optimized out>,
    shared_arg=0x555555abe9d0 <_PyRuntime+14032>, p_excinfo=p_excinfo@entry=0x7fffffffd0a0, self=<optimized out>)
    at ./Modules/_interpretersmodule.c:950
#3  0x00007ffff79dbaa0 in interp_exec (self=<optimized out>, args=<optimized out>, kwds=<optimized out>)
    at ./Modules/_interpretersmodule.c:995
#4  0x00005555556ac233 in cfunction_call (func=0x7ffff7a6d4e0, args=<optimized out>, kwargs=<optimized out>)
    at Objects/methodobject.c:551
#5  0x00005555556433f0 in _PyObject_MakeTpCall (tstate=0x555555b07b20 <_PyRuntime+313376>, callable=callable@entry=0x7ffff7a6d4e0,
    args=args@entry=0x7ffff7fb0080, nargs=<optimized out>, keywords=keywords@entry=0x0) at Objects/call.c:242
#6  0x0000555555643d16 in _PyObject_VectorcallTstate (kwnames=0x0, nargsf=<optimized out>, args=0x7ffff7fb0080,
    callable=0x7ffff7a6d4e0, tstate=<optimized out>) at ./Include/internal/pycore_call.h:165
#7  0x00005555555d8e85 in _PyEval_EvalFrameDefault (tstate=0x555555b07b20 <_PyRuntime+313376>, frame=0x7ffff7fb0020,
    throwflag=<optimized out>) at Python/generated_cases.c.h:955
#8  0x00005555557a5abc in _PyEval_EvalFrame (throwflag=0, frame=0x7ffff7fb0020, tstate=0x555555b07b20 <_PyRuntime+313376>)
    at ./Include/internal/pycore_ceval.h:116
#9  _PyEval_Vector (args=0x0, argcount=0, kwnames=0x0, locals=0x7ffff7a187c0, func=0x7ffff7a033d0,
    tstate=0x555555b07b20 <_PyRuntime+313376>) at Python/ceval.c:1901
#10 PyEval_EvalCode (co=co@entry=0x7ffff7a3a120, globals=globals@entry=0x7ffff7a187c0, locals=locals@entry=0x7ffff7a187c0)
    at Python/ceval.c:662
#11 0x0000555555811018 in run_eval_code_obj (locals=0x7ffff7a187c0, globals=0x7ffff7a187c0, co=0x7ffff7a3a120,
    tstate=0x555555b07b20 <_PyRuntime+313376>) at Python/pythonrun.c:1338
```
</p>
</details>

----------


#### 19- [126876](https://github.com/python/cpython/issues/126876) - Assertion failure for `socket` with too large default timeout (larger than INT_MAX)

```python
python -c "import socket; socket.setdefaulttimeout(2**31) ; socket._fallback_socketpair()"
```

- Issue Number: 126876
- Date filed: 15/11/2024
- Date closed: 14/12/2024
- Kind: Abort
- Configuration: Debug
- Python versions: 3.12, 3.13, 3.14
- Status: Closed-Completed
- PRs (author):
  - [126968](https://github.com/python/cpython/pull/126968) (@vstinner)
  - [127002](https://github.com/python/cpython/pull/127002) (@vstinner)
  - [127003](https://github.com/python/cpython/pull/127003) (@vstinner)
  - [127517](https://github.com/python/cpython/pull/127517) (@vstinner)

<details><summary>Backtrace/error message:</summary>
<p>


```shell
python: ./Modules/socketmodule.c:819: internal_select: Assertion `ms <= INT_MAX' failed.
Aborted (core dumped)
```
</p>
</details>

----------


#### 20- [126881](https://github.com/python/cpython/issues/126881) - Segfault with `asyncio.base_events.BaseEventLoop` when passed a small float to `set_debug`.

```python
import asyncio.base_events

obj = asyncio.base_events.BaseEventLoop()
obj.set_debug(0.0005)
obj._run_forever_setup()
```

- Issue Number: 126881
- Date filed: 15/11/2024
- Date closed: 29/11/2024
- Kind: Segmentation Fault
- Configuration: Release
- Python versions: 3.12, 3.13, 3.14
- Status: Closed-Completed
- PRs (author):
  - [126901](https://github.com/python/cpython/pull/126901) (@picnixz)
  - [126904](https://github.com/python/cpython/pull/126904) (@kumaraditya303)
  - [127395](https://github.com/python/cpython/pull/127395) (@kumaraditya303)

<details><summary>Backtrace/error message:</summary>
<p>


```shell
#0  0x00007ffff7bc9f51 in mult (a=0x7ffff7f19338 <_PyRuntime+118936>, b=0x0) at Python/dtoa.c:618
#1  0x00007ffff7bca2dc in pow5mult (b=0x7ffff7f19338 <_PyRuntime+118936>, k=1) at Python/dtoa.c:702
#2  0x00007ffff7bcdede in _Py_dg_dtoa (dd=0.00050000000000000001, mode=0, ndigits=0, decpt=0x7fffffff956c,
    sign=0x7fffffff9570, rve=0x7fffffff9580) at Python/dtoa.c:2550
#3  0x00007ffff7bc82e0 in format_float_short (d=0.00050000000000000001, format_code=114 'r', mode=0,
    precision=0, always_add_sign=0, add_dot_0_if_integer=2, use_alt_formatting=0, no_negative_zero=0,
    float_strings=0x7ffff7e6fab0 <lc_float_strings>, type=0x0) at Python/pystrtod.c:986
#4  0x00007ffff7bc8b3d in PyOS_double_to_string (val=0.00050000000000000001, format_code=114 'r',
    precision=0, flags=2, type=0x0) at Python/pystrtod.c:1279
#5  0x00007ffff794ca67 in float_repr (v=0x7ffff73ac970) at Objects/floatobject.c:380
#6  0x00007ffff79ecc50 in object_str (self=0x7ffff73ac970) at Objects/typeobject.c:6215
#7  0x00007ffff799fa89 in PyObject_Str (v=0x7ffff73ac970) at Objects/object.c:742
```
</p>
</details>

----------


#### 21- [126884](https://github.com/python/cpython/issues/126884) - Calling `cProfile.runctx` in threads on a free-threading build segfaults

```python
from threading import Thread
import cProfile

for x in range(100):
    Thread(target=cProfile.runctx, args=("", {}, {}, "",)).start()
```

- Issue Number: 126884
- Date filed: 15/11/2024
- Date closed:
- Kind: Segmentation Fault
- Configuration: Free-Threaded
- Python versions: 3.13, 3.14
- Status: Open
- PRs (author):
  - None yet

<details><summary>Backtrace/error message:</summary>
<p>


```shell
#0  RotatingTree_Get (root=0xddddddddddddde25, key=key@entry=0x20002080780) at ./Modules/rotatingtree.c:56
#1  0x00007ffff7c3c940 in getSubEntry (pObj=pObj@entry=0x200041901e0, caller=<optimized out>,
    entry=entry@entry=0x20002080780) at ./Modules/_lsprof.c:245
#2  0x00007ffff7c3cf25 in Stop (pObj=pObj@entry=0x200041901e0, self=self@entry=0x200020e0310,
    entry=0x20002080780) at ./Modules/_lsprof.c:338
#3  0x00007ffff7c3cfdb in flush_unmatched (pObj=pObj@entry=0x200041901e0) at ./Modules/_lsprof.c:833
#4  0x00007ffff7c3e991 in _lsprof_Profiler_disable_impl (self=0x200041901e0) at ./Modules/_lsprof.c:893
#5  0x00007ffff7c3e9ca in _lsprof_Profiler_disable (self=<optimized out>, _unused_ignored=<optimized out>)
    at ./Modules/clinic/_lsprof.c.h:288
#6  0x0000555555694b24 in method_vectorcall_NOARGS (func=<method_descriptor at remote 0x20000aa01d0>,
    args=0x7ffff7433b48, nargsf=<optimized out>, kwnames=<optimized out>) at Objects/descrobject.c:447
#7  0x000055555567cc55 in _PyObject_VectorcallTstate (tstate=0x555555dcc3f0,
    callable=<method_descriptor at remote 0x20000aa01d0>, args=0x7ffff7433b48, nargsf=9223372036854775809,
    kwnames=0x0) at ./Include/internal/pycore_call.h:167
#8  0x000055555567cd74 in PyObject_Vectorcall (
    callable=callable@entry=<method_descriptor at remote 0x20000aa01d0>, args=args@entry=0x7ffff7433b48,
    nargsf=<optimized out>, kwnames=kwnames@entry=0x0) at Objects/call.c:327
#9  0x00005555558592c0 in _PyEval_EvalFrameDefault (tstate=tstate@entry=0x555555dcc3f0,
    frame=0x7ffff6c30340, throwflag=throwflag@entry=0) at Python/generated_cases.c.h:4469
#10 0x00005555558726ea in _PyEval_EvalFrame (throwflag=0, frame=<optimized out>, tstate=0x555555dcc3f0)
    at ./Include/internal/pycore_ceval.h:116
#11 _PyEval_Vector (tstate=<optimized out>, func=0x20000a8b450, locals=locals@entry=0x0,
    args=0x7ffff7433cd8, argcount=1, kwnames=<optimized out>) at Python/ceval.c:1901
```
</p>
</details>

----------


#### 22- [126895](https://github.com/python/cpython/issues/126895) - Segfault/aborts calling `readline.set_completer_delims` in threads in a free-threaded build

```python
from threading import Thread
import readline

def f():
    for x in range(100):
        readline.get_completer_delims()
        readline.set_completer_delims(' \t\n`@#%^&*()=+[{]}\\|;:\'",<>?')
        readline.set_completer_delims(' \t\n`@#%^&*()=+[{]}\\|;:\'",<>?')
        readline.get_completer_delims()

for x in range(100):
    Thread(target=f, args=()).start()
```

- Issue Number: 126895
- Date filed: 16/11/2024
- Date closed: 17/03/2025
- Kind: Segmentation Fault
- Configuration: Free-Threaded
- Python versions: 3.13, 3.14
- Status: Closed-Completed
- PRs (author):
  - [131208](https://github.com/python/cpython/pull/131208) (@tom-pytel)

<details><summary>Backtrace/error message:</summary>
<p>


```shell
Thread 92 "python" received signal SIGSEGV, Segmentation fault.
[Switching to Thread 0x7ffeca7e4640 (LWP 631239)]
0x00007ffff7d3f743 in unlink_chunk (p=p@entry=0x555555f56c00, av=0x7ffff7eb8c80 <main_arena>) at ./malloc/malloc.c:1634
1634    ./malloc/malloc.c: No such file or directory.
(gdb) bt
#0  0x00007ffff7d3f743 in unlink_chunk (p=p@entry=0x555555f56c00, av=0x7ffff7eb8c80 <main_arena>)
    at ./malloc/malloc.c:1634
#1  0x00007ffff7d40d2b in _int_free (av=0x7ffff7eb8c80 <main_arena>, p=0x555555f528a0,
    have_lock=<optimized out>) at ./malloc/malloc.c:4616
#2  0x00007ffff7d43453 in __GI___libc_free (mem=<optimized out>) at ./malloc/malloc.c:3391
#3  0x000055555570ed2c in _PyMem_RawFree (_unused_ctx=<optimized out>, ptr=<optimized out>)
    at Objects/obmalloc.c:90
#4  0x0000555555713955 in _PyMem_DebugRawFree (ctx=0x555555cdb8f8 <_PyRuntime+824>, p=0x555555f528c0)
    at Objects/obmalloc.c:2767
#5  0x000055555572c462 in PyMem_RawFree (ptr=ptr@entry=0x555555f528c0) at Objects/obmalloc.c:971
#6  0x00005555559527fc in free_threadstate (tstate=tstate@entry=0x555555f528c0) at Python/pystate.c:1411
#7  0x00005555559549c0 in _PyThreadState_DeleteCurrent (tstate=tstate@entry=0x555555f528c0)
    at Python/pystate.c:1834
#8  0x0000555555a11b74 in thread_run (boot_raw=boot_raw@entry=0x555555f52870)
    at ./Modules/_threadmodule.c:355
#9  0x0000555555974fdb in pythread_wrapper (arg=<optimized out>) at Python/thread_pthread.h:242
#10 0x00007ffff7d32ac3 in start_thread (arg=<optimized out>) at ./nptl/pthread_create.c:442
#11 0x00007ffff7dc4850 in clone3 () at ../sysdeps/unix/sysv/linux/x86_64/clone3.S:81
```
</p>
</details>

----------


#### 23- [126907](https://github.com/python/cpython/issues/126907) - Running `atexit` from threads in free-threading build segfaults

```python
from threading import Thread
import atexit

def g():
    pass

def f():
    for x in range(100):
        atexit.register(g)
        atexit._clear()
        atexit.register(g)
        atexit.unregister(g)
        atexit._run_exitfuncs()

for x in range(100):
    Thread(target=f, args=()).start()
```

- Issue Number: 126907
- Date filed: 16/11/2024
- Date closed: 16/12/2024
- Kind: Segmentation Fault
- Configuration: Free-Threaded
- Python versions: 3.13, 3.14
- Status: Closed-Completed
- PRs (author):
  - [126908](https://github.com/python/cpython/pull/126908) (@ZeroIntensity)
  - [127935](https://github.com/python/cpython/pull/127935) (@ZeroIntensity)

<details><summary>Backtrace/error message:</summary>
<p>


```shell
#0  atexit_delete_cb (state=state@entry=0x555555cfd8f8 <_PyRuntime+140088>, i=i@entry=0)
    at ./Modules/atexitmodule.c:58
#1  0x000055555598d962 in atexit_cleanup (state=0x555555cfd8f8 <_PyRuntime+140088>)
    at ./Modules/atexitmodule.c:75
#2  0x000055555598d9b6 in atexit_clear (module=<optimized out>, unused=<optimized out>)
    at ./Modules/atexitmodule.c:249
#3  0x0000555555702405 in cfunction_vectorcall_NOARGS (
    func=<built-in method _clear of module object at remote 0x200007752c0>, args=<optimized out>,
    nargsf=<optimized out>, kwnames=<optimized out>) at Objects/methodobject.c:495
#4  0x000055555567cc55 in _PyObject_VectorcallTstate (tstate=0x555555dc8fe0,
    callable=<built-in method _clear of module object at remote 0x200007752c0>, args=0x7ffff7c42b48,
    nargsf=9223372036854775808, kwnames=0x0) at ./Include/internal/pycore_call.h:167
#5  0x000055555567cd74 in PyObject_Vectorcall (
    callable=callable@entry=<built-in method _clear of module object at remote 0x200007752c0>,
    args=args@entry=0x7ffff7c42b48, nargsf=<optimized out>, kwnames=kwnames@entry=0x0)
    at Objects/call.c:327
#6  0x00005555558441f7 in _PyEval_EvalFrameDefault (tstate=tstate@entry=0x555555dc8fe0,
    frame=<optimized out>, throwflag=throwflag@entry=0) at Python/generated_cases.c.h:955
#7  0x0000555555872978 in _PyEval_EvalFrame (throwflag=0, frame=<optimized out>, tstate=0x555555dc8fe0)
    at ./Include/internal/pycore_ceval.h:116
#8  _PyEval_Vector (tstate=<optimized out>, func=0x20000a8b530, locals=locals@entry=0x0,
    args=0x7ffff7c42cd8, argcount=1, kwnames=<optimized out>) at Python/ceval.c:1901
#9  0x000055555567c622 in _PyFunction_Vectorcall (func=<optimized out>, stack=<optimized out>,
    nargsf=<optimized out>, kwnames=<optimized out>) at Objects/call.c:413
#10 0x00005555556816b4 in _PyObject_VectorcallTstate (kwnames=0x0, nargsf=1, args=0x7ffff7c42cd8,
    callable=<function at remote 0x20000a8b530>, tstate=0x555555dc8fe0)
    at ./Include/internal/pycore_call.h:167
```
</p>
</details>

----------


#### 24- [127085](https://github.com/python/cpython/issues/127085) - Calling `ShareableList.count` in threads aborts: `Assertion 'self->exports == 0' failed`

```python
import gc
import multiprocessing.shared_memory
from threading import Thread

obj = multiprocessing.shared_memory.ShareableList("Uq..SeDAmB+EBrkLl.SG.Z+Z.ZdsV..wT+zLxKwdN\b")

for x in range(10):
    Thread(target=obj.count, args=(1,)).start()

del obj
gc.collect()
```

- Issue Number: 127085
- Date filed: 21/11/2024
- Date closed: 16/12/2024
- Kind: Abort
- Configuration: Free-Threaded
- Python versions: 3.13, 3.14
- Status: Closed-Completed
- PRs (author):
  - [127412](https://github.com/python/cpython/pull/127412) (@LindaSummer)
  - [128019](https://github.com/python/cpython/pull/128019) (@freakboy3742)

<details><summary>Backtrace/error message:</summary>
<p>


```shell
Exception ignored in: <function SharedMemory.__del__ at 0x200006bbfb0>
Traceback (most recent call last):
  File "/home/danzin/projects/mycpython/Lib/multiprocessing/shared_memory.py", line 189, in __del__
    self.close()
  File "/home/danzin/projects/mycpython/Lib/multiprocessing/shared_memory.py", line 229, in close
    self._buf.release()
BufferError: memoryview has 2 exported buffers
python: Objects/memoryobject.c:1143: memory_dealloc: Assertion `self->exports == 0' failed.
Aborted
```
</p>
</details>

----------


#### 25- [127165](https://github.com/python/cpython/issues/127165) - Segfault in invalid `concurrent.futures.interpreter.WorkerContext`

```python
python -c "import concurrent.futures.interpreter; w = concurrent.futures.interpreter.WorkerContext(0, {'\x00': ''}).initialize()"

# Or

import _interpreters
_interpreters.create()
_interpreters.set___main___attrs(1, {"\x00": 1}, restrict=True)
```

- Issue Number: 127165
- Date filed: 22/11/2024
- Date closed: 01/12/2024
- Kind: Segmentation Fault
- Configuration: Release
- Python versions: 3.13, 3.14
- Status: Closed-Completed
- PRs (author):
  - [127199](https://github.com/python/cpython/pull/127199) (@ZeroIntensity)
  - [127463](https://github.com/python/cpython/pull/127463) (@ZeroIntensity)

<details><summary>Backtrace/error message:</summary>
<p>


```shell
#0  Py_INCREF (op=op@entry=0x0) at ./Include/refcount.h:241
#1  0x00005555557e6aa7 in _Py_NewRef (obj=0x0) at ./Include/refcount.h:492
#2  _sharednsitem_apply (item=0x555555cd55e0, ns=ns@entry=0x200028329b0, dflt=dflt@entry=0x0) at Python/crossinterp.c:1224
#3  0x00005555557e7d14 in _PyXI_ApplyNamespace (ns=ns@entry=0x555555cd55b0, nsobj=nsobj@entry=0x200028329b0, dflt=dflt@entry=0x0) at Python/crossinterp.c:1523
#4  0x00005555557e7ec8 in _PyXI_Enter (session=session@entry=0x7fffffffe040, interp=interp@entry=0x7ffff7bb8020, nsupdates=<optimized out>)
    at Python/crossinterp.c:1754
#5  0x00007ffff7e1fafd in interp_set___main___attrs (self=self@entry=0x20000966980, args=args@entry=0x20000943850, kwargs=kwargs@entry=0x20000736eb0)
    at ./Modules/_interpretersmodule.c:836
#6  0x00005555556c1565 in cfunction_call (func=func@entry=0x20000966830, args=args@entry=0x20000943850, kwargs=kwargs@entry=0x20000736eb0)
    at Objects/methodobject.c:551
#7  0x000055555566987f in _PyObject_MakeTpCall (tstate=tstate@entry=0x555555c39510 <_PyRuntime+360208>, callable=callable@entry=0x20000966830,
    args=args@entry=0x7fffffffe3c8, nargs=<optimized out>, keywords=keywords@entry=0x2000057e700) at Objects/call.c:242
#8  0x0000555555669ada in _PyObject_VectorcallTstate (tstate=0x555555c39510 <_PyRuntime+360208>, callable=callable@entry=0x20000966830,
    args=args@entry=0x7fffffffe3c8, nargsf=<optimized out>, kwnames=kwnames@entry=0x2000057e700) at ./Include/internal/pycore_call.h:165
#9  0x0000555555669b30 in PyObject_Vectorcall (callable=callable@entry=0x20000966830, args=args@entry=0x7fffffffe3c8, nargsf=<optimized out>,
    kwnames=kwnames@entry=0x2000057e700) at Objects/call.c:327
#10 0x00005555557adebb in _PyEval_EvalFrameDefault (tstate=<optimized out>, frame=0x7ffff7e6a0a0, throwflag=<optimized out>) at Python/generated_cases.c.h:1982
#11 0x00005555557c755c in _PyEval_EvalFrame (tstate=tstate@entry=0x555555c39510 <_PyRuntime+360208>, frame=<optimized out>, throwflag=throwflag@entry=0)
    at ./Include/internal/pycore_ceval.h:116
#12 0x00005555557c766a in _PyEval_Vector (tstate=tstate@entry=0x555555c39510 <_PyRuntime+360208>, func=func@entry=0x200007b3490, locals=locals@entry=0x20000737870,
    args=args@entry=0x0, argcount=argcount@entry=0, kwnames=kwnames@entry=0x0) at Python/ceval.c:1898
#13 0x00005555557c7739 in PyEval_EvalCode (co=co@entry=0x200003a3f10, globals=globals@entry=0x20000737870, locals=locals@entry=0x20000737870) at Python/ceval.c:659
#14 0x000055555588bac3 in run_eval_code_obj (tstate=tstate@entry=0x555555c39510 <_PyRuntime+360208>, co=co@entry=0x200003a3f10, globals=globals@entry=0x20000737870,
    locals=locals@entry=0x20000737870) at Python/pythonrun.c:1338
#15 0x000055555588bca3 in run_mod (mod=mod@entry=0x200007e42b0, filename=filename@entry=0x20000a462f0, globals=globals@entry=0x20000737870,
    locals=locals@entry=0x20000737870, flags=flags@entry=0x7fffffffe720, arena=arena@entry=0x200000508b0, interactive_src=0x200002338f0, generate_new_source=0)
    at Python/pythonrun.c:1423
#16 0x000055555588c6ad in _PyRun_StringFlagsWithName (
    str=str@entry=0x200002341e0 "import concurrent.futures.interpreter; w = concurrent.futures.interpreter.WorkerContext(0, {'\\x00': ''}).initialize()\n",
    name=name@entry=0x20000a462f0, start=start@entry=257, globals=globals@entry=0x20000737870, locals=locals@entry=0x20000737870, flags=flags@entry=0x7fffffffe720,
    generate_new_source=0) at Python/pythonrun.c:1222
```
</p>
</details>

----------


#### 26- [127182](https://github.com/python/cpython/issues/127182) - Assertion failure from `StringIO.__setstate__`

```python
python -c "from io import StringIO; StringIO().__setstate__((None, '', 0, {}))"
```

- Issue Number: 127182
- Date filed: 23/11/2024
- Date closed: 25/11/2024
- Kind: Abort
- Configuration: Debug
- Python versions: 3.13, 3.14
- Status: Closed-Completed
- PRs (author):
  - [127219](https://github.com/python/cpython/pull/127219) (@sobolevn)
  - [127262](https://github.com/python/cpython/pull/127262) (@sobolevn, @vstinner)
  - [127263](https://github.com/python/cpython/pull/127263) (@sobolevn, @vstinner)

<details><summary>Backtrace/error message:</summary>
<p>


```shell
python: Objects/unicodeobject.c:2542: as_ucs4: Assertion `PyUnicode_Check(string)' failed.
Aborted (core dumped)
```
</p>
</details>

----------


#### 27- [127190](https://github.com/python/cpython/issues/127190) - Segfault from `asyncio.events._running_loop.__setattr__` with invalid name

```python
import asyncio.events

class Liar1:
    def __eq__(self, other):
        return True

asyncio.events._running_loop.__setattr__(Liar1(), type)
```

- Issue Number: 127190
- Date filed: 23/11/2024
- Date closed: 28/11/2024
- Kind: Segmentation Fault
- Configuration:Release
- Python versions: 3.13, 3.14
- Status: Closed-Completed
- PRs (author):
  - [127366](https://github.com/python/cpython/pull/127366) (@vstinner)
  - [127367](https://github.com/python/cpython/pull/127367) (@vstinner)
  - [127368](https://github.com/python/cpython/pull/127368) (@vstinner)

<details><summary>Backtrace/error message:</summary>
<p>


```shell
#0  _copy_characters (to=<optimized out>, to_start=<optimized out>, from=<optimized out>,
    from_start=<optimized out>, how_many=<optimized out>, check_maxchar=0) at Objects/unicodeobject.c:1530
#1  0x000055555573497b in _copy_characters (check_maxchar=0, how_many=16842781, from_start=0,
    from=0x7ffff71a3cb0, to_start=<optimized out>, to=<optimized out>) at Objects/unicodeobject.c:1435
#2  _PyUnicode_FastCopyCharacters (how_many=16842781, from_start=0, from=0x7ffff71a3cb0,
    to_start=<optimized out>, to=<optimized out>) at Objects/unicodeobject.c:1562
#3  _PyUnicodeWriter_WriteStr (writer=0x7fffffffd660, str=0x7ffff71a3cb0) at Objects/unicodeobject.c:13635
#4  0x0000555555738abd in unicode_fromformat_arg (vargs=0x7fffffffd5d8,
    f=0x5555558d2a04 "U' is read-only", writer=0x7fffffffd660) at Objects/unicodeobject.c:2993
#5  unicode_from_format (writer=writer@entry=0x7fffffffd660,
    format=format@entry=0x5555558d29e8 "'%.100s' object attribute '%U' is read-only",
    vargs=vargs@entry=0x7fffffffd6c0) at Objects/unicodeobject.c:3167
#6  0x0000555555739a1f in PyUnicode_FromFormatV (
    format=format@entry=0x5555558d29e8 "'%.100s' object attribute '%U' is read-only",
    vargs=vargs@entry=0x7fffffffd6c0) at Objects/unicodeobject.c:3201
#7  0x00005555557c7770 in _PyErr_FormatV (vargs=0x7fffffffd6c0,
    format=0x5555558d29e8 "'%.100s' object attribute '%U' is read-only",
    exception=0x555555a89960 <_PyExc_AttributeError>, tstate=0x555555b08c10 <_PyRuntime+313456>)
    at Python/errors.c:1163
#8  PyErr_Format (exception=0x555555a89960 <_PyExc_AttributeError>,
    format=format@entry=0x5555558d29e8 "'%.100s' object attribute '%U' is read-only")
    at Python/errors.c:1198
#9  0x00005555558a613d in local_setattro (self=0x7ffff718d020, name=0x7ffff71a3cb0,
    v=0x555555a9c6e0 <PyType_Type>) at ./Modules/_threadmodule.c:1625
#10 0x00005555556dff7d in wrap_setattr (self=0x7ffff718d020, args=<optimized out>,
    wrapped=0x5555558a6070 <local_setattro>) at Objects/typeobject.c:9172
```
</p>
</details>

----------


#### 28- [127192](https://github.com/python/cpython/issues/127192) - Segfault or abort in free-threaded build calling methods from exception in threads

```python
from threading import Thread
import email.errors

alive = []
for x in range(100):
    obj = email.errors.InvalidMultipartContentTransferEncodingDefect()

    alive.append(Thread(target=obj.__getstate__, args=()))
    alive.append(Thread(target=obj.__repr__, args=()))
    for x in range(20):
        obj.__init__(["a" * (2 ** 16)])
    alive.append(Thread(target=obj.__init__, args=(["a" * (2 ** 16)],)))

for obj in alive:
    try:
        print('START', obj)
        obj.start()
    except Exception:
        pass
```

- Issue Number: 127192
- Date filed: 23/11/2024
- Date closed: 23/11/2024
- Kind: Segmentation Fault
- Configuration: Free-Threaded
- Python versions: 3.13, 3.14
- Status: Closed-Not-Planned
- PRs (author):
  - None

<details><summary>Backtrace/error message:</summary>
<p>


```shell
#0  __pthread_kill_implementation (no_tid=0, signo=6, threadid=140736531846720) at ./nptl/pthread_kill.c:44
#1  __pthread_kill_internal (signo=6, threadid=140736531846720) at ./nptl/pthread_kill.c:78
#2  __GI___pthread_kill (threadid=140736531846720, signo=signo@entry=6) at ./nptl/pthread_kill.c:89
#3  0x00007ffff7ce0476 in __GI_raise (sig=sig@entry=6) at ../sysdeps/posix/raise.c:26
#4  0x00007ffff7cc67f3 in __GI_abort () at ./stdlib/abort.c:79
#5  0x0000555555944db0 in fatal_error_exit (status=<optimized out>) at Python/pylifecycle.c:3059
#6  0x00005555559519fb in fatal_error (fd=2, header=header@entry=1,
    prefix=prefix@entry=0x555555b0bb20 <__func__.0> "PyMutex_Unlock",
    msg=msg@entry=0x555555b0b950 "unlocking mutex that is not locked", status=status@entry=-1)
    at Python/pylifecycle.c:3275
#7  0x0000555555951a6d in _Py_FatalErrorFunc (
    func=func@entry=0x555555b0bb20 <__func__.0> "PyMutex_Unlock",
    msg=msg@entry=0x555555b0b950 "unlocking mutex that is not locked") at Python/pylifecycle.c:3291
#8  0x000055555592a36f in PyMutex_Unlock (m=<optimized out>) at Python/lock.c:615
#9  0x00005555556c6e23 in _PyMutex_Unlock (m=<optimized out>) at ./Include/cpython/lock.h:60
#10 _PyCriticalSection_End (c=0x7fffc6fcc5f0) at ./Include/internal/pycore_critical_section.h:148
#11 list_repr (self=<optimized out>) at Objects/listobject.c:581
#12 0x0000555555709951 in PyObject_Repr (
    v=[<unknown at remote 0xdddddddddddddddd>, <unknown at remote 0xdddddddddddddddd>, <unknown at remote 0xdddddddddddddddd>, <unknown at remote 0xdddddddddddddddd>]) at Objects/object.c:737
#13 0x00005555557accbf in unicode_fromformat_arg (writer=writer@entry=0x7fffc6fcc750,
    f=0x555555a590bc "R)", f@entry=0x555555a590bb "%R)", vargs=vargs@entry=0x7fffc6fcc700)
    at Objects/unicodeobject.c:3048
#14 0x00005555557ad0dd in unicode_from_format (writer=writer@entry=0x7fffc6fcc750,
    format=format@entry=0x555555a590b8 "%s(%R)", vargs=vargs@entry=0x7fffc6fcc7c0)
    at Objects/unicodeobject.c:3167
#15 0x00005555557ad287 in PyUnicode_FromFormatV (format=0x555555a590b8 "%s(%R)",
    vargs=vargs@entry=0x7fffc6fcc7c0) at Objects/unicodeobject.c:3201
#16 0x00005555557ad363 in PyUnicode_FromFormat (format=format@entry=0x555555a590b8 "%s(%R)") at Objects/unicodeobject.c:3215
#17 0x00005555556986fb in BaseException_repr (self=self@entry=0x200005d2aa0) at Objects/exceptions.c:170
#18 0x000055555574c3f3 in wrap_unaryfunc (self=<InvalidMultipartContentTransferEncodingDefect(line=['aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa...(truncated), args=<optimized out>, wrapped=0x555555698672 <BaseException_repr>) at Objects/typeobject.c:8947
#19 0x0000555555691ce5 in wrapperdescr_raw_call (kwds={}, args=(), self=<optimized out>, descr=<optimized out>) at Objects/descrobject.c:531
#20 wrapper_call (self=self@entry=<method-wrapper '__repr__' of InvalidMultipartContentTransferEncodingDefect object at 0x200005d2aa0>, args=args@entry=(), kwds=kwds@entry={}) at Objects/descrobject.c:1438
#21 0x000055555567f6ef in _PyObject_Call (tstate=0x555555dd7700, callable=callable@entry=<method-wrapper '__repr__' of InvalidMultipartContentTransferEncodingDefect object at 0x200005d2aa0>, args=args@entry=(), kwargs=kwargs@entry={}) at Objects/call.c:361
#22 0x000055555567f811 in PyObject_Call (callable=callable@entry=<method-wrapper '__repr__' of InvalidMultipartContentTransferEncodingDefect object at 0x200005d2aa0>, args=args@entry=(), kwargs=kwargs@entry={}) at Objects/call.c:373
```
</p>
</details>

----------


#### 29- [127196](https://github.com/python/cpython/issues/127196) - `_interpreters.exec` with invalid dict as `shared` segfaults

```python
import _interpreters
_interpreters.exec(0, "1", {"\uFD7C\u5124\u7B91\u92E9\u1850\u39AA\u0DF2\uD82A\u2D68\uACAD\u92DE\u47C5\uFFD0\uDE0B\uAA9C\u2C17\\u6577\u4C92\uD37C": 0})
```

- Issue Number: 127196
- Date filed: 23/11/2024
- Date closed: 09/01/2025
- Kind: Segmentation Fault
- Configuration: Release
- Python versions: 3.13, 3.14
- Status: Closed-Completed
- PRs (author):
  - [127220](https://github.com/python/cpython/pull/127220) (@sobolevn)
  - [128689](https://github.com/python/cpython/pull/128689) (@sobolevn)

<details><summary>Backtrace/error message:</summary>
<p>


```shell
#0  0x00005555557c496c in _PyXI_ApplyError (error=0x0) at Python/crossinterp.c:1056
#1  0x00007ffff79db822 in _run_in_interpreter (p_excinfo=0x7fffffffd820, flags=1,
    shareables=0x7ffff7a186c0, codestrlen=<optimized out>, codestr=0x555555aceff8 <_PyRuntime+76888> "1",
    interp=0x555555ad1f18 <_PyRuntime+88952>) at ./Modules/_interpretersmodule.c:463
#2  _interp_exec (interp=interp@entry=0x555555ad1f18 <_PyRuntime+88952>, code_arg=<optimized out>,
    shared_arg=0x7ffff7a186c0, p_excinfo=p_excinfo@entry=0x7fffffffd820, self=<optimized out>)
    at ./Modules/_interpretersmodule.c:955
#3  0x00007ffff79db9b0 in interp_exec (self=<optimized out>, args=<optimized out>, kwds=<optimized out>)
    at ./Modules/_interpretersmodule.c:1000
#4  0x00005555556abb43 in cfunction_call (func=0x7ffff7a6d9e0, args=<optimized out>,
    kwargs=<optimized out>) at Objects/methodobject.c:551
#5  0x0000555555643350 in _PyObject_MakeTpCall (tstate=0x555555b08c10 <_PyRuntime+313456>,
    callable=callable@entry=0x7ffff7a6d9e0, args=args@entry=0x7ffff7fb0080, nargs=<optimized out>,
    keywords=keywords@entry=0x0) at Objects/call.c:242
#6  0x0000555555643c76 in _PyObject_VectorcallTstate (kwnames=0x0, nargsf=<optimized out>,
    args=0x7ffff7fb0080, callable=0x7ffff7a6d9e0, tstate=<optimized out>)
    at ./Include/internal/pycore_call.h:165
#7  0x00005555555d8e75 in _PyEval_EvalFrameDefault (tstate=0x555555b08c10 <_PyRuntime+313456>,
    frame=0x7ffff7fb0020, throwflag=<optimized out>) at Python/generated_cases.c.h:955
#8  0x00005555557a559c in _PyEval_EvalFrame (throwflag=0, frame=0x7ffff7fb0020,
    tstate=0x555555b08c10 <_PyRuntime+313456>) at ./Include/internal/pycore_ceval.h:116
#9  _PyEval_Vector (args=0x0, argcount=0, kwnames=0x0, locals=0x7ffff7a18680, func=0x7ffff7a033d0,
    tstate=0x555555b08c10 <_PyRuntime+313456>) at Python/ceval.c:1898
#10 PyEval_EvalCode (co=co@entry=0x7ffff7a32230, globals=globals@entry=0x7ffff7a18680,
    locals=locals@entry=0x7ffff7a18680) at Python/ceval.c:659
```
</p>
</details>

----------


#### 30- [127208](https://github.com/python/cpython/issues/127208) - `ExtensionFileLoader.load_module` aborts when initialized with a path containing null-bytes

```python
import _frozen_importlib_external

_frozen_importlib_external.ExtensionFileLoader("a", "\x00").load_module(None)
```

- Issue Number: 127208
- Date filed: 24/11/2024
- Date closed: 29/11/2024
- Kind: Abort
- Configuration: Debug
- Python versions: 3.12, 3.13, 3.14
- Status: Closed-Completed
- PRs (author):
  - [127400](https://github.com/python/cpython/pull/127400) (@vstinner)
  - [127418](https://github.com/python/cpython/pull/127418) (@vstinner)
  - [127419](https://github.com/python/cpython/pull/127419) (@vstinner)

<details><summary>Backtrace/error message:</summary>
<p>


```shell
python: Python/import.c:939: hashtable_key_from_2_strings: Assertion `strlen(key) == size - 1' failed.
Aborted
```
</p>
</details>

----------


#### 31- [127234](https://github.com/python/cpython/issues/127234) - Assertion failures from `_interpchannels._register_end_types`

```python
import _interpchannels

_interpchannels._register_end_types(int, int)
```

- Issue Number: 127234
- Date filed: 24/11/2024
- Date closed:
- Kind: Abort
- Configuration: Debug
- Python versions: 3.13, 3.14
- Status: Open
- PRs (author):
  - None yet

<details><summary>Backtrace/error message:</summary>
<p>


```shell
python: Python/crossinterp_data_lookup.h:271: _PyXIData_RegisterClass: Assertion `matched->getdata == getdata' failed.
Aborted
```
</p>
</details>

----------


#### 32- [127235](https://github.com/python/cpython/issues/127235) - Failed assertion in `Python/legacy_tracing.c:431` on a free-threading build

```python
import threading

def errback(*args, **kw):
    raise ValueError('error')

for x in range(200):
    threading._start_joinable_thread(errback)
    try:
        threading.setprofile_all_threads("")
    except:
        pass
```

- Issue Number: 127235
- Date filed: 24/11/2024
- Date closed:
- Kind: Abort
- Configuration: Free-Threaded
- Python versions: 3.14
- Status: Open
- PRs (author):
  - None yet

<details><summary>Backtrace/error message:</summary>
<p>


```shell
python: Python/legacy_tracing.c:431: is_tstate_valid: Assertion `!_PyMem_IsPtrFreed(tstate)' failed.
Aborted
```
</p>
</details>

----------


#### 33- [127316](https://github.com/python/cpython/issues/127316) - [FreeThreading] object_set_class() fails with an assertion error in _PyCriticalSection_AssertHeld()

```python
import threading

obj = threading._DummyThread()
res = obj.__reduce__()
res = obj._after_fork(1)
```

- Issue Number: 127316
- Date filed: 27/11/2024
- Date closed: 29/11/2024
- Kind: Abort
- Configuration: Free-Threaded
- Python versions: 3.13, 3.14
- Status: Closed-Completed
- PRs (author):
  - [127399](https://github.com/python/cpython/pull/127399) (@kumaraditya303)
  - [127422](https://github.com/python/cpython/pull/127422) (@kumaraditya303)

<details><summary>Backtrace/error message:</summary>
<p>


```shell
python: ./Include/internal/pycore_critical_section.h:222: _PyCriticalSection_AssertHeld: Assertion `cs != NULL && cs->_cs_mutex == mutex' failed.
Aborted (core dumped)
```
</p>
</details>

----------


#### 34- [127603](https://github.com/python/cpython/issues/127603) - Abort from `GenericAlias.__sizeof__`: `ob->ob_type != &PyLong_Type`
This issue was fixed in a PR (#127605) for another issue.

```python
from types import GenericAlias

g = GenericAlias(BaseException, Exception)
g.__sizeof__(1)
```

- Issue Number: 127603
- Date filed: 04/12/2024
- Date closed: 11/12/2024
- Kind: Abort
- Configuration: Debug
- Python versions: 3.12
- Status: Closed-Completed
- PRs (author):
  - [127605](https://github.com/python/cpython/pull/127605) (@markshannon)

<details><summary>Backtrace/error message:</summary>
<p>


```shell
python: ./Include/object.h:231: Py_SIZE: Assertion `ob->ob_type != &PyLong_Type' failed.
Aborted
```
</p>
</details>

----------


#### 35- [127836](https://github.com/python/cpython/issues/127836) - Assertion failure on finalization with `_lsprof` and `asyncio` in 3.12

```python
import asyncio
import _lsprof

obj = _lsprof.Profiler()
obj.enable()
obj._pystart_callback(lambda: 0, 0)
obj = None  # Required

loop = asyncio.get_event_loop()
```

- Issue Number: 127836
- Date filed: 11/12/2024
- Date closed: 23/02/2025
- Kind: Abort
- Configuration: Debug
- Python versions: 3.12
- Status: Closed-Not-Planned
- PRs (author):
  - None

<details><summary>Backtrace/error message:</summary>
<p>


```shell
python: Python/instrumentation.c:958: call_instrumentation_vector: Assertion `instrumentation_cross_checks(tstate->interp, code)' failed.
Aborted
```
</p>
</details>

----------


#### 36- [127870](https://github.com/python/cpython/issues/127870) - Segfaults in ctypes _as_parameter_ handling when called with `MagicMock`

```python
from unittest.mock import MagicMock
import _pyrepl._minimal_curses

obj = _pyrepl._minimal_curses.tparm(MagicMock(), 0, 0, 0, 0, 0, 0, 0)
obj = _pyrepl._minimal_curses.setupterm(MagicMock(), 0)
obj = _pyrepl._minimal_curses.tigetstr(MagicMock())
```

- Issue Number: 127870
- Date filed: 12/12/2024
- Date closed: 13/12/2024
- Kind: Segmentation Fault
- Configuration: Release
- Python versions: 3.12, 3.13, 3.14
- Status: Closed-Completed
- PRs (author):
  - [127872](https://github.com/python/cpython/pull/127872) (@vstinner)
  - [127917](https://github.com/python/cpython/pull/127917) (@vstinner)
  - [127918](https://github.com/python/cpython/pull/127918) (@vstinner)

<details><summary>Backtrace/error message:</summary>
<p>


```shell
#0  0x00005555556b04e6 in compare_unicode_unicode (mp=0x0, dk=0x55556ce6f460, ep0=0x55556ce6f500, ix=38, key=0x7ffff73ae860, hash=5657245593745306375)
    at Objects/dictobject.c:1136
#1  0x00005555556af1cb in do_lookup (mp=mp@entry=0x0, dk=dk@entry=0x55556ce6f460, key=key@entry=0x7ffff73ae860, hash=hash@entry=5657245593745306375,
    check_lookup=check_lookup@entry=0x5555556b04da <compare_unicode_unicode>) at Objects/dictobject.c:1066
#2  0x00005555556af242 in unicodekeys_lookup_unicode (dk=dk@entry=0x55556ce6f460, key=key@entry=0x7ffff73ae860, hash=hash@entry=5657245593745306375)
    at Objects/dictobject.c:1151
#3  0x00005555556b3c99 in _Py_dict_lookup (mp=0x7fffbe6a3c50, key=key@entry=0x7ffff73ae860, hash=hash@entry=5657245593745306375,
    value_addr=value_addr@entry=0x7fffff7ff0f0) at Objects/dictobject.c:1265
#4  0x00005555556b4746 in _PyDict_GetItemRef_KnownHash (op=<optimized out>, key=key@entry=0x7ffff73ae860, hash=hash@entry=5657245593745306375,
    result=result@entry=0x7fffff7ff130) at Objects/dictobject.c:2317
#5  0x00005555556ff874 in find_name_in_mro (type=type@entry=0x55556ce6cca0, name=name@entry=0x7ffff73ae860, error=error@entry=0x7fffff7ff194)
    at Objects/typeobject.c:5108
#6  0x00005555556ffa3c in _PyType_LookupRef (type=type@entry=0x55556ce6cca0, name=name@entry=0x7ffff73ae860) at Objects/typeobject.c:5260
#7  0x00005555556ca8b8 in _PyObject_GenericSetAttrWithDict (obj=obj@entry=0x7fffbe6b9920, name=0x7ffff73ae860, value=0x555555ae8100 <_Py_NoneStruct>,
    dict=dict@entry=0x0) at Objects/object.c:1773
#8  0x00005555556cab5f in PyObject_GenericSetAttr (obj=obj@entry=0x7fffbe6b9920, name=<optimized out>, value=<optimized out>) at Objects/object.c:1849
#9  0x00005555556f541e in wrap_setattr (self=0x7fffbe6b9920, args=<optimized out>, wrapped=0x5555556cab4d <PyObject_GenericSetAttr>) at Objects/typeobject.c:8792
#10 0x000055555567ee41 in wrapperdescr_raw_call (descr=descr@entry=0x7ffff7b002f0, self=self@entry=0x7fffbe6b9920, args=args@entry=0x7fffc5b5bd90,
    kwds=kwds@entry=0x0) at Objects/descrobject.c:531
#11 0x000055555567f2c5 in wrapperdescr_call (_descr=_descr@entry=0x7ffff7b002f0, args=0x7fffc5b5bd90, args@entry=0x7fffc5a48c50, kwds=kwds@entry=0x0)
    at Objects/descrobject.c:569
#12 0x0000555555672a51 in _PyObject_MakeTpCall (tstate=tstate@entry=0x555555b564c0 <_PyRuntime+299040>, callable=callable@entry=0x7ffff7b002f0,
    args=args@entry=0x7ffff7e29850, nargs=<optimized out>, keywords=keywords@entry=0x0) at Objects/call.c:242
#13 0x0000555555672c91 in _PyObject_VectorcallTstate (tstate=0x555555b564c0 <_PyRuntime+299040>, callable=callable@entry=0x7ffff7b002f0,
    args=args@entry=0x7ffff7e29850, nargsf=<optimized out>, kwnames=kwnames@entry=0x0) at ./Include/internal/pycore_call.h:166
#14 0x0000555555672ce7 in PyObject_Vectorcall (callable=callable@entry=0x7ffff7b002f0, args=args@entry=0x7ffff7e29850, nargsf=<optimized out>,
    kwnames=kwnames@entry=0x0) at Objects/call.c:327
#15 0x00005555557a293c in _PyEval_EvalFrameDefault (tstate=0x555555b564c0 <_PyRuntime+299040>, frame=0x7ffff7e297c8, throwflag=0) at Python/generated_cases.c.h:1839
#16 0x00005555557b0957 in _PyEval_EvalFrame (tstate=tstate@entry=0x555555b564c0 <_PyRuntime+299040>, frame=<optimized out>, throwflag=throwflag@entry=0)
    at ./Include/internal/pycore_ceval.h:119
#17 0x00005555557b0a76 in _PyEval_Vector (tstate=0x555555b564c0 <_PyRuntime+299040>, func=0x7ffff6a893d0, locals=locals@entry=0x0, args=0x7fffff7ff650, argcount=3,
    kwnames=0x0) at Python/ceval.c:1807
#18 0x00005555556728a2 in _PyFunction_Vectorcall (func=<optimized out>, stack=<optimized out>, nargsf=<optimized out>, kwnames=<optimized out>) at Objects/call.c:413
#19 0x00005555556f4c21 in _PyObject_VectorcallTstate (tstate=0x555555b564c0 <_PyRuntime+299040>, callable=0x7ffff6a893d0, args=0x7fffff7ff650, nargsf=3,
    kwnames=kwnames@entry=0x0) at ./Include/internal/pycore_call.h:168
#20 0x00005555556f4cd8 in vectorcall_unbound (tstate=<optimized out>, unbound=<optimized out>, func=<optimized out>, args=<optimized out>, nargs=<optimized out>)
    at Objects/typeobject.c:2566
#21 0x0000555555700c61 in vectorcall_method (name=<optimized out>, args=args@entry=0x7fffff7ff650, nargs=nargs@entry=3) at Objects/typeobject.c:2597
```
</p>
</details>

----------


#### 37- [129573](https://github.com/python/cpython/issues/129573) - Failed assertion in `_PyUnicode_Equal` from `calculate_suggestions` with non-string candidate

```python
import runpy
runpy._run_module_code("A", {0: ""}, "")
```

- Issue Number: 129573
- Date filed: 02/02/2025
- Date closed:
- Kind: Abort
- Configuration: Debug
- Python versions: 3.12, 3.13, 3.14
- Status: Open
- PRs (author):
  - [129574](https://github.com/python/cpython/pull/129574) (@devdanzin)
  - [130997](https://github.com/python/cpython/pull/130997) (@devdanzin)

<details><summary>Backtrace/error message:</summary>
<p>


```shell
python: Objects/unicodeobject.c:10799: _PyUnicode_Equal: Assertion `PyUnicode_Check(str2)' failed.
Aborted (core dumped)
```
</p>
</details>

----------


#### 38- [129766](https://github.com/python/cpython/issues/129766) - Fatal Python error from `warnings._release_lock()`

```python
import warnings
warnings._release_lock()
```

- Issue Number: 129766
- Date filed: 07/02/2025
- Date closed: 07/02/2025
- Kind: Abort
- Configuration: Debug
- Python versions: 3.14
- Status: Closed-Completed
- PRs (author):
  - [129771](https://github.com/python/cpython/pull/129771) (@sobolevn)

<details><summary>Backtrace/error message:</summary>
<p>


```shell
Fatal Python error: _PyRecursiveMutex_Unlock: unlocking a recursive mutex that is not owned by the current thread
Python runtime state: initialized

Current thread 0x0000718eb9295740 (most recent call first):
  File "<string>", line 1 in <module>
Aborted (core dumped)
```
</p>
</details>

----------


#### 39- [131580](https://github.com/python/cpython/issues/131580) - Faulthandler segfaults when called from threads
Closed in favor of #116008.

```python
import faulthandler
from threading import Thread

for x in range(20):
    Thread(target=faulthandler.dump_traceback_later, args=(1e-10,)).start()
```

- Issue Number: 131580
- Date filed: 22/03/2025
- Date closed: 25/03/2025
- Kind: Segmentation Fault
- Configuration: Free-Threaded
- Python versions: 3.14
- Status: Closed-Completed
- PRs (author):
  - None

<details><summary>Backtrace/error message:</summary>
<p>


```shell
#0  _PyFrame_GetCode (f=0xfffff7fea1f0) at ./Include/internal/pycore_frame.h:94
#1  dump_frame (fd=fd@entry=2, frame=frame@entry=0xfffff7fea1f0)
    at Python/traceback.c:914
#2  0x000000000076254c in dump_traceback (fd=fd@entry=2,
    tstate=tstate@entry=0xaeb528 <_PyRuntime+329832>,
    write_header=write_header@entry=0) at Python/traceback.c:1007
#3  0x0000000000762710 in _Py_DumpTracebackThreads (fd=2,
    interp=<optimized out>, current_tstate=current_tstate@entry=0x0)
    at Python/traceback.c:1114
#4  0x00000000007773b4 in faulthandler_thread (unused=unused@entry=0x0)
    at ./Modules/faulthandler.c:631
#5  0x000000000075e77c in pythread_wrapper (arg=<optimized out>)
    at Python/thread_pthread.h:242
#6  0x0000fffff7def188 in start_thread () from /lib64/libc.so.6
#7  0x0000fffff7e5971c in thread_start () from /lib64/libc.so.6
```
</p>
</details>

----------


#### 40- [131998](https://github.com/python/cpython/issues/131998) - The interpreter crashes when specializing bound method calls on unbound objects
A release blocker.

```python
import glob

for x in range(3):
    str_globber = glob._StringGlobber(None, None)
str_globber.selector(set())

try:
    str_globber.selector([True, True, False])
except:
    pass

globber_base = glob._GlobberBase(0, 0, 0, 0)
globber_base.selector(list)
```

- Issue Number: 131998
- Date filed: 02/04/2025
- Date closed: 08/04/2025
- Kind: Segmentation Fault
- Configuration: Release
- Python versions: 3.13, 3.14
- Status: Closed-Completed
- PRs (author):
  - [132000](https://github.com/python/cpython/pull/132000) (@ZeroIntensity)
  - [132262](https://github.com/python/cpython/pull/132262) (@ZeroIntensity, @sobolevn, @vstinner, @markshannon)

<details><summary>Backtrace/error message:</summary>
<p>


```shell
Program received signal SIGSEGV, Segmentation fault.
_PyEval_EvalFrameDefault (tstate=tstate@entry=0x555555c6b558 <_PyRuntime+330424>, frame=0x7ffff7fb00a0, frame@entry=0x7ffff7fb0020, throwflag=throwflag@entry=0) at ./Include/object.h:270
270             return ob->ob_type;
(gdb) bt
#0  _PyEval_EvalFrameDefault (tstate=tstate@entry=0x555555c6b558 <_PyRuntime+330424>, frame=0x7ffff7fb00a0,
    frame@entry=0x7ffff7fb0020, throwflag=throwflag@entry=0) at ./Include/object.h:270
#1  0x000055555585db58 in _PyEval_EvalFrame (throwflag=0, frame=0x7ffff7fb0020, tstate=0x555555c6b558 <_PyRuntime+330424>)
    at ./Include/internal/pycore_ceval.h:119
#2  _PyEval_Vector (tstate=tstate@entry=0x555555c6b558 <_PyRuntime+330424>, func=func@entry=0x7ffff7a91b50,
    locals=locals@entry={'__name__': '__main__', '__doc__': None, '__package__': None, '__loader__': <SourceFileLoader(name='__main__', path='/home/fusil/runs/python-12/glob-cpu_load-invalid_mem_access-0x0000000000000008/source2.py') at remote 0x7ffff7a95b90>, '__spec__': None, '__builtins__': <module at remote 0x7ffff7befef0>, '__file__': '/home/fusil/runs/python-12/glob-cpu_load-invalid_mem_access-0x0000000000000008/source2.py', '__cached__': None, 'glob': <module at remote 0x7ffff7ad0170>, 'x': 2, 'str_globber': <_StringGlobber(sep=None, case_sensitive=None, case_pedantic=False, recursive=False) at remote 0x7ffff78ef630>, 'globber_base': <_GlobberBase(case_pedantic=0, case_sensitive=0, recursive=0, sep=0) at remote 0x7ffff7a7e6e0>}, args=args@entry=0x0, argcount=argcount@entry=0,
    kwnames=kwnames@entry=0x0) at Python/ceval.c:1908
#3  0x000055555585dc57 in PyEval_EvalCode (co=co@entry=<code at remote 0x7ffff7b5db60>,
    globals=globals@entry={'__name__': '__main__', '__doc__': None, '__package__': None, '__loader__': <SourceFileLoader(name='__main__', path='/home/fusil/runs/python-12/glob-cpu_load-invalid_mem_access-0x0000000000000008/source2.py') at remote 0x7ffff7a95b90>, '__spec__': None, '__builtins__': <module at remote 0x7ffff7befef0>, '__file__': '/home/fusil/runs/python-12/glob-cpu_load-invalid_mem_access-0x0000000000000008/source2.py', '__cached__': None, 'glob': <module at remote 0x7ffff7ad0170>, 'x': 2, 'str_globber': <_StringGlobber(sep=None, case_sensitive=None, case_pedantic=False, recursive=False) at remote 0x7ffff78ef630>, 'globber_base': <_GlobberBase(case_pedantic=0, case_sensitive=0, recursive=0, sep=0) at remote 0x7ffff7a7e6e0>},
    locals=locals@entry={'__name__': '__main__', '__doc__': None, '__package__': None, '__loader__': <SourceFileLoader(name='__main__', path='/home/fusil/runs/python-12/glob-cpu_load-invalid_mem_access-0x0000000000000008/source2.py') at remote 0x7ffff7a95b90>, '__spec__': None, '__builtins__': <module at remote 0x7ffff7befef0>, '__file__': '/home/fusil/runs/python-12/glob-cpu_load-invalid_mem_access-0x0000000000000008/source2.py', '__cached__': None, 'glob': <module at remote 0x7ffff7ad0170>, 'x': 2, 'str_globber': <_StringGlobber(sep=None, case_sensitive=None, case_pedantic=False, recursive=False) at remote 0x7ffff78ef630>, 'globber_base': <_GlobberBase(case_pedantic=0, case_sensitive=0, recursive=0, sep=0) at remote 0x7ffff7a7e6e0>}) at Python/ceval.c:836
#4  0x00005555558eb82e in run_eval_code_obj (tstate=tstate@entry=0x555555c6b558 <_PyRuntime+330424>, co=co@entry=0x7ffff7b5db60,
    globals=globals@entry={'__name__': '__main__', '__doc__': None, '__package__': None, '__loader__': <SourceFileLoader(name='__main__', path='/home/fusil/runs/python-12/glob-cpu_load-invalid_mem_access-0x0000000000000008/source2.py') at remote 0x7ffff7a95b90>, '__spec__': None, '__builtins__': <module at remote 0x7ffff7befef0>, '__file__': '/home/fusil/runs/python-12/glob-cpu_load-invalid_mem_access-0x0000000000000008/source2.py', '__cached__': None, 'glob': <module at remote 0x7ffff7ad0170>, 'x': 2, 'str_globber': <_StringGlobber(sep=None, case_sensitive=None, case_pedantic=False, recursive=False) at remote 0x7ffff78ef630>, 'globber_base': <_GlobberBase(case_pedantic=0, case_sensitive=0, recursive=0, sep=0) at remote 0x7ffff7a7e6e0>},
    locals=locals@entry={'__name__': '__main__', '__doc__': None, '__package__': None, '__loader__': <SourceFileLoader(name='__main__', path='/home/fusil/runs/python-12/glob-cpu_load-invalid_mem_access-0x0000000000000008/source2.py') at remote 0x7ffff7a95b90>, '__spec__': None, '__builtins__': <module at remote 0x7ffff7befef0>, '__file__': '/home/fusil/runs/python-12/glob-cpu_load-invalid_mem_access-0x0000000000000008/source2.py', '__cached__': None, 'glob': <module at remote 0x7ffff7ad0170>, 'x': 2, 'str_globber': <_StringGlobber(sep=None, case_sensitive=None, case_pedantic=False, recursive=False) at remote 0x7ffff78ef630>, 'globber_base': <_GlobberBase(case_pedantic=0, case_sensitive=0, recursive=0, sep=0) at remote 0x7ffff7a7e6e0>}) at Python/pythonrun.c:1365
#5  0x00005555558ec92e in run_mod (mod=mod@entry=0x555555e0e230, filename=filename@entry='/home/fusil/runs/python-12/glob-cpu_load-invalid_mem_access-0x0000000000000008/source2.py', globals=globals@entry={'__name__': '__main__', '__doc__': None, '__package__': None, '__loader__': <SourceFileLoader(name='__main__', path='/home/fusil/runs/python-12/glob-cpu_load-invalid_mem_access-0x0000000000000008/source2.py') at remote 0x7ffff7a95b90>, '__spec__': None, '__builtins__': <module at remote 0x7ffff7befef0>, '__file__': '/home/fusil/runs/python-12/glob-cpu_load-invalid_mem_access-0x0000000000000008/source2.py', '__cached__': None, 'glob': <module at remote 0x7ffff7ad0170>, 'x': 2, 'str_globber': <_StringGlobber(sep=None, case_sensitive=None, case_pedantic=False, recursive=False) at remote 0x7ffff78ef630>, 'globber_base': <_GlobberBase(case_pedantic=0, case_sensitive=0, recursive=0, sep=0) at remote 0x7ffff7a7e6e0>}, locals=locals@entry={'__name__': '__main__', '__doc__': None, '__package__': None, '__loader__': <SourceFileLoader(name='__main__', path='/home/fusil/runs/python-12/glob-cpu_load-invalid_mem_access-0x0000000000000008/source2.py') at remote 0x7ffff7a95b90>, '__spec__': None, '__builtins__': <module at remote 0x7ffff7befef0>, '__file__': '/home/fusil/runs/python-12/glob-cpu_load-invalid_mem_access-0x0000000000000008/source2.py', '__cached__': None, 'glob': <module at remote 0x7ffff7ad0170>, 'x': 2, 'str_globber': <_StringGlobber(sep=None, case_sensitive=None, case_pedantic=False, recursive=False) at remote 0x7ffff78ef630>, 'globber_base': <_GlobberBase(case_pedantic=0, case_sensitive=0, recursive=0, sep=0) at remote 0x7ffff7a7e6e0>}, flags=flags@entry=0x7fffffffdb68, arena=arena@entry=0x7ffff7ab3f40, interactive_src=0x0, generate_new_source=0) at Python/pythonrun.c:1436
#6  0x00005555558eccdb in pyrun_file (fp=fp@entry=0x555555df2410, filename=filename@entry='/home/fusil/runs/python-12/glob-cpu_load-invalid_mem_access-0x0000000000000008/source2.py', start=start@entry=257, globals=globals@entry={'__name__': '__main__', '__doc__': None, '__package__': None, '__loader__': <SourceFileLoader(name='__main__', path='/home/fusil/runs/python-12/glob-cpu_load-invalid_mem_access-0x0000000000000008/source2.py') at remote 0x7ffff7a95b90>, '__spec__': None, '__builtins__': <module at remote 0x7ffff7befef0>, '__file__': '/home/fusil/runs/python-12/glob-cpu_load-invalid_mem_access-0x0000000000000008/source2.py', '__cached__': None, 'glob': <module at remote 0x7ffff7ad0170>, 'x': 2, 'str_globber': <_StringGlobber(sep=None, case_sensitive=None, case_pedantic=False, recursive=False) at remote 0x7ffff78ef630>, 'globber_base': <_GlobberBase(case_pedantic=0, case_sensitive=0, recursive=0, sep=0) at remote 0x7ffff7a7e6e0>}, locals=locals@entry={'__name__': '__main__', '__doc__': None, '__package__': None, '__loader__': <SourceFileLoader(name='__main__', path='/home/fusil/runs/python-12/glob-cpu_load-invalid_mem_access-0x0000000000000008/source2.py') at remote 0x7ffff7a95b90>, '__spec__': None, '__builtins__': <module at remote 0x7ffff7befef0>, '__file__': '/home/fusil/runs/python-12/glob-cpu_load-invalid_mem_access-0x0000000000000008/source2.py', '__cached__': None, 'glob': <module at remote 0x7ffff7ad0170>, 'x': 2, 'str_globber': <_StringGlobber(sep=None, case_sensitive=None, case_pedantic=False, recursive=False) at remote 0x7ffff78ef630>, 'globber_base': <_GlobberBase(case_pedantic=0, case_sensitive=0, recursive=0, sep=0) at remote 0x7ffff7a7e6e0>}, closeit=closeit@entry=1, flags=0x7fffffffdb68) at Python/pythonrun.c:1293
#7  0x00005555558eeff1 in _PyRun_SimpleFileObject (fp=fp@entry=0x555555df2410, filename=filename@entry='/home/fusil/runs/python-12/glob-cpu_load-invalid_mem_access-0x0000000000000008/source2.py', closeit=closeit@entry=1, flags=flags@entry=0x7fffffffdb68) at Python/pythonrun.c:521
#8  0x00005555558ef2ba in _PyRun_AnyFileObject (fp=fp@entry=0x555555df2410, filename=filename@entry='/home/fusil/runs/python-12/glob-cpu_load-invalid_mem_access-0x0000000000000008/source2.py', closeit=closeit@entry=1, flags=flags@entry=0x7fffffffdb68) at Python/pythonrun.c:81
#9  0x000055555591ebd4 in pymain_run_file_obj (program_name=program_name@entry='/home/danzin/projects/cpython/python', filename=filename@entry='/home/fusil/runs/python-12/glob-cpu_load-invalid_mem_access-0x0000000000000008/source2.py', skip_source_first_line=0) at Modules/main.c:396
#10 0x000055555591ef72 in pymain_run_file (config=config@entry=0x555555c36688 <_PyRuntime+113640>) at Modules/main.c:415
#11 0x000055555592050d in pymain_run_python (exitcode=exitcode@entry=0x7fffffffdcf4) at Modules/main.c:680
#12 0x000055555592056e in Py_RunMain () at Modules/main.c:761
#13 0x00005555559205e5 in pymain_main (args=args@entry=0x7fffffffdd50) at Modules/main.c:791
#14 0x00005555559206a8 in Py_BytesMain (argc=<optimized out>, argv=<optimized out>) at Modules/main.c:815
#15 0x00005555555d7926 in main (argc=<optimized out>, argv=<optimized out>) at ./Programs/python.c:15
```
</p>
</details>

----------


#### 41- [132002](https://github.com/python/cpython/issues/132002) - Segfault deallocating a `ContextVar` built with `str` subclass

```python
from _contextvars import ContextVar

class weird_str(str):
    def __eq__(self, other):
        pass

ContextVar(weird_str())
```

- Issue Number: 132002
- Date filed: 02/04/2025
- Date closed: 02/04/2025
- Kind: Segmentation Fault
- Configuration: Release
- Python versions: 3.12, 3.13, 3.14
- Status: Closed-Completed
- PRs (author):
  - [132003](https://github.com/python/cpython/pull/132003) (@sobolevn)
  - [132007](https://github.com/python/cpython/pull/132007) (@sobolevn)
  - [132008](https://github.com/python/cpython/pull/132008) (@sobolevn)

<details><summary>Backtrace/error message:</summary>
<p>


```shell
Program received signal SIGSEGV, Segmentation fault.
contextvar_tp_clear (op=op@entry=<_contextvars.ContextVar at remote 0x7ffff7ac7150>) at Python/context.c:935
935         Py_CLEAR(self->var_name);
(gdb) bt
#0  contextvar_tp_clear (op=op@entry=<_contextvars.ContextVar at remote 0x7ffff7ac7150>) at Python/context.c:935
#1  0x000055555587e395 in contextvar_tp_dealloc (self=<_contextvars.ContextVar at remote 0x7ffff7ac7150>) at Python/context.c:958
#2  0x00005555556ffa08 in _Py_Dealloc (op=op@entry=<_contextvars.ContextVar at remote 0x7ffff7ac7150>) at Objects/object.c:3021
#3  0x000055555587e672 in Py_DECREF (op=<_contextvars.ContextVar at remote 0x7ffff7ac7150>, lineno=883,
    filename=0x555555a49efe "Python/context.c") at ./Include/refcount.h:416
#4  contextvar_new (name=<weird_str() at remote 0x7ffff7bc7260>, def=0x0) at Python/context.c:883
#5  0x000055555587e6fe in contextvar_tp_new (type=<optimized out>, args=<optimized out>, kwds=<optimized out>)
    at Python/context.c:928
#6  0x000055555574692f in type_call (self=<type at remote 0x555555bff380>, args=(<weird_str() at remote 0x7ffff7bc7260>,), kwds=0x0)
    at Objects/typeobject.c:2244
#7  0x000055555567b9a7 in _PyObject_MakeTpCall (tstate=tstate@entry=0x555555c69558 <_PyRuntime+330424>,
    callable=callable@entry=<type at remote 0x555555bff380>, args=args@entry=0x7fffffffd7c8, nargs=<optimized out>,
    keywords=keywords@entry=0x0) at Objects/call.c:242
#8  0x000055555567bdc8 in _PyObject_VectorcallTstate (tstate=0x555555c69558 <_PyRuntime+330424>,
    callable=<type at remote 0x555555bff380>, args=0x7fffffffd7c8, nargsf=<optimized out>, kwnames=0x0)
    at ./Include/internal/pycore_call.h:167
#9  0x000055555567bdf4 in PyObject_Vectorcall (callable=callable@entry=<type at remote 0x555555bff380>,
    args=args@entry=0x7fffffffd7c8, nargsf=<optimized out>, kwnames=kwnames@entry=0x0) at Objects/call.c:327
#10 0x000055555582f4c0 in _PyEval_EvalFrameDefault (tstate=tstate@entry=0x555555c69558 <_PyRuntime+330424>,
    frame=frame@entry=0x7ffff7fb0020, throwflag=throwflag@entry=0) at Python/generated_cases.c.h:1366
#11 0x000055555585cd69 in _PyEval_EvalFrame (throwflag=0, frame=0x7ffff7fb0020, tstate=0x555555c69558 <_PyRuntime+330424>)
    at ./Include/internal/pycore_ceval.h:119
```
</p>
</details>

----------


#### 42- [132011](https://github.com/python/cpython/issues/132011) - Failed assertion in `_PyEval_EvalFrameDefault`: `self_o != NULL`

```python
l = []

def lappend(l, x, y):
    l.append((x, y))

try:
    for x in range(3):
        lappend(l, None, None)
except:
    pass

lappend(list, None, None)
```

- Issue Number: 132011
- Date filed: 02/04/2025
- Date closed: 06/04/2025
- Kind: Abort
- Configuration: Debug
- Python versions: 3.13, 3.14
- Status: Closed-Completed
- PRs (author):
  - [132018](https://github.com/python/cpython/pull/132018) (@sobolevn)
  - [132161](https://github.com/python/cpython/pull/132161) (@sobolevn)

<details><summary>Backtrace/error message:</summary>
<p>


```shell
python: Python/generated_cases.c.h:3345: _PyEval_EvalFrameDefault: Assertion `self_o != NULL' failed.

Program received signal SIGABRT, Aborted.
__pthread_kill_implementation (no_tid=0, signo=6, threadid=140737350580032) at ./nptl/pthread_kill.c:44
44      ./nptl/pthread_kill.c: No such file or directory.
(gdb) bt
#0  __pthread_kill_implementation (no_tid=0, signo=6, threadid=140737350580032) at ./nptl/pthread_kill.c:44
#1  __pthread_kill_internal (signo=6, threadid=140737350580032) at ./nptl/pthread_kill.c:78
#2  __GI___pthread_kill (threadid=140737350580032, signo=signo@entry=6) at ./nptl/pthread_kill.c:89
#3  0x00007ffff7ce0476 in __GI_raise (sig=sig@entry=6) at ../sysdeps/posix/raise.c:26
#4  0x00007ffff7cc67f3 in __GI_abort () at ./stdlib/abort.c:79
#5  0x00007ffff7cc671b in __assert_fail_base (fmt=0x7ffff7e7b130 "%s%s%s:%u: %s%sAssertion `%s' failed.\n%n",
    assertion=0x555555a43bc6 "self_o != NULL", file=0x555555a43993 "Python/generated_cases.c.h", line=3345,
    function=<optimized out>) at ./assert/assert.c:94
#6  0x00007ffff7cd7e96 in __GI___assert_fail (assertion=assertion@entry=0x555555a43bc6 "self_o != NULL",
    file=file@entry=0x555555a43993 "Python/generated_cases.c.h", line=line@entry=3345,
    function=function@entry=0x555555a44980 <__PRETTY_FUNCTION__.81> "_PyEval_EvalFrameDefault") at ./assert/assert.c:103
#7  0x0000555555837189 in _PyEval_EvalFrameDefault (tstate=tstate@entry=0x555555c6b558 <_PyRuntime+330424>, frame=0x7ffff7fb00a0,
    frame@entry=0x7ffff7fb0020, throwflag=throwflag@entry=0) at Python/generated_cases.c.h:3345
#8  0x000055555585db58 in _PyEval_EvalFrame (throwflag=0, frame=0x7ffff7fb0020, tstate=0x555555c6b558 <_PyRuntime+330424>)
    at ./Include/internal/pycore_ceval.h:119
#9  _PyEval_Vector (tstate=tstate@entry=0x555555c6b558 <_PyRuntime+330424>, func=func@entry=0x7ffff7a8db50,
    locals=locals@entry={'__name__': '__main__', '__doc__': None, '__package__': None, '__loader__': <SourceFileLoader(name='__main__', path='/home/fusil/runs/python-12/difflib-abort-assertion/source2.py') at remote 0x7ffff7a95b90>, '__spec__': None, '__builtins__': <module at remote 0x7ffff7befef0>, '__file__': '/home/fusil/runs/python-12/difflib-abort-assertion/source2.py', '__cached__': None, 'difflib': <module at remote 0x7ffff7acc110>, 'obj': <HtmlDiff(_charjunk=None, _linejunk=None, _tabsize=None, _wrapcolumn=None) at remote 0x7ffff7a7be40>, 'x': 2}, args=args@entry=0x0, argcount=argcount@entry=0, kwnames=kwnames@entry=0x0) at Python/ceval.c:1908
#10 0x000055555585dc57 in PyEval_EvalCode (co=co@entry=<code at remote 0x7ffff7bce400>,
    globals=globals@entry={'__name__': '__main__', '__doc__': None, '__package__': None, '__loader__': <SourceFileLoader(name='__main__', path='/home/fusil/runs/python-12/difflib-abort-assertion/source2.py') at remote 0x7ffff7a95b90>, '__spec__': None, '__builtins__': <module at remote 0x7ffff7befef0>, '__file__': '/home/fusil/runs/python-12/difflib-abort-assertion/source2.py', '__cached__': None, 'difflib': <module at remote 0x7ffff7acc110>, 'obj': <HtmlDiff(_charjunk=None, _linejunk=None, _tabsize=None, _wrapcolumn=None) at remote 0x7ffff7a7be40>, 'x': 2},
    locals=locals@entry={'__name__': '__main__', '__doc__': None, '__package__': None, '__loader__': <SourceFileLoader(name='__main__', path='/home/fusil/runs/python-12/difflib-abort-assertion/source2.py') at remote 0x7ffff7a95b90>, '__spec__': None, '__builtins__': <module at remote 0x7ffff7befef0>, '__file__': '/home/fusil/runs/python-12/difflib-abort-assertion/source2.py', '__cached__': None, 'difflib': <module at remote 0x7ffff7acc110>, 'obj': <HtmlDiff(_charjunk=None, _linejunk=None, _tabsize=None, _wrapcolumn=None) at remote 0x7ffff7a7be40>, 'x': 2}) at Python/ceval.c:836
#11 0x00005555558eb82e in run_eval_code_obj (tstate=tstate@entry=0x555555c6b558 <_PyRuntime+330424>, co=co@entry=0x7ffff7bce400,
    globals=globals@entry={'__name__': '__main__', '__doc__': None, '__package__': None, '__loader__': <SourceFileLoader(name='__main__', path='/home/fusil/runs/python-12/difflib-abort-assertion/source2.py') at remote 0x7ffff7a95b90>, '__spec__': None, '__builtins__': <module at remote 0x7ffff7befef0>, '__file__': '/home/fusil/runs/python-12/difflib-abort-assertion/source2.py', '__cached__': None, 'difflib': <module at remote 0x7ffff7acc110>, 'obj': <HtmlDiff(_charjunk=None, _linejunk=None, _tabsize=None, _wrapcolumn=None) at remote 0x7ffff7a7be40>, 'x': 2},
    locals=locals@entry={'__name__': '__main__', '__doc__': None, '__package__': None, '__loader__': <SourceFileLoader(name='__main__', path='/home/fusil/runs/python-12/difflib-abort-assertion/source2.py') at remote 0x7ffff7a95b90>, '__spec__': None, '__builtins__': <module at remote 0x7ffff7befef0>, '__file__': '/home/fusil/runs/python-12/difflib-abort-assertion/source2.py', '__cached__': None, 'difflib': <module at remote 0x7ffff7acc110>, 'obj': <HtmlDiff(_charjunk=None, _linejunk=None, _tabsize=None, _wrapcolumn=None) at remote 0x7ffff7a7be40>, 'x': 2}) at Python/pythonrun.c:1365
```
</p>
</details>

----------


#### 43- [132171](https://github.com/python/cpython/issues/132171) - Assertion failure calling `_interpreters.run_string` with a string subclass instance

```python
import _interpreters

class weird_str(str): pass

_interpreters.create()
_interpreters.run_string(1, weird_str('1'))
```

- Issue Number: 132171
- Date filed: 06/04/2025
- Date closed: 07/04/2025
- Kind: Abort
- Configuration: Debug
- Python versions: 3.13, 3.14
- Status: Closed-Completed
- PRs (author):
  - [132173](https://github.com/python/cpython/pull/132173) (@sobolevn)
  - [132219](https://github.com/python/cpython/pull/132219) (@sobolevn)

<details><summary>Backtrace/error message:</summary>
<p>


```shell
python: ./Modules/_interpretersmodule.c:333: get_code_str: Assertion `PyUnicode_CheckExact(arg) && (check_code_str((PyUnicodeObject *)arg) == NULL)' failed.
Aborted (core dumped)
```
</p>
</details>

----------


#### 44- [132176](https://github.com/python/cpython/issues/132176) - Abort when using a tuple subclass instance as the `bases` parameter for `type`

```python
class weird_tuple(tuple): pass

c = type("c", weird_tuple((str,)), {})
```

- Issue Number: 132176
- Date filed: 06/04/2025
- Date closed: 15/04/2025
- Kind: Abort
- Configuration: Debug
- Python versions: 3.13, 3.14
- Status: Closed-Completed
- PRs (author):
  - [132212](https://github.com/python/cpython/pull/132212) (@sobolevn)
  - [132548](https://github.com/python/cpython/pull/132548) (@sobolevn)

<details><summary>Backtrace/error message:</summary>
<p>


```shell
python: Objects/typeobject.c:500: set_tp_bases: Assertion `PyTuple_CheckExact(bases)' failed.
Aborted (core dumped)
```
</p>
</details>

----------


#### 45- [132250](https://github.com/python/cpython/issues/132250) - `_ccall_callback` method of `_lsprof.Profiler` causes Fatal Python error

```python
import _lsprof

prof = _lsprof.Profiler()
prof.enable()

def mismatch(first, second):
    first.find(second())

mismatch(bytes, str)
# mismatch(str, bytes)
# mismatch(str, list)
```

- Issue Number: 132250
- Date filed: 08/04/2025
- Date closed: 08/04/2025
- Kind: Abort
- Configuration: Debug
- Python versions: 3.13, 3.14
- Status: Closed-Completed
- PRs (author):
  - [132251](https://github.com/python/cpython/pull/132251) (@gaogaotiantian)
  - [132281](https://github.com/python/cpython/pull/132281) (@gaogaotiantian)

<details><summary>Backtrace/error message:</summary>
<p>


```shell
Fatal Python error: _Py_CheckFunctionResult: a function returned a result with an exception set
Python runtime state: initialized
TypeError: descriptor 'find' for 'bytes' objects doesn't apply to a 'str' object

The above exception was the direct cause of the following exception:

SystemError: <built-in method _ccall_callback of _lsprof.Profiler object at 0x20000922f10> returned a result with an exception set

Stack (most recent call first):
  File "/mnt/c/Users/ddini/crashers/main/cProfile-fatal_python_error-abort/source2.py", line 7 in mismatch
  File "/mnt/c/Users/ddini/crashers/main/cProfile-fatal_python_error-abort/source2.py", line 9 in <module>

Program received signal SIGABRT, Aborted.
```
</p>
</details>

----------


#### 46- [132296](https://github.com/python/cpython/issues/132296) - Concurrent deallocation of threads while calling `PyEval_SetTrace`

```python
import threading

threading._start_joinable_thread(lambda: None)
threading._start_joinable_thread(lambda: None)
threading._start_joinable_thread(lambda: None)
threading._start_joinable_thread(lambda: None)
for x in range(100):
    try:
        threading.settrace_all_threads(())
    except Exception:
        pass
```

- Issue Number: 132296
- Date filed: 09/04/2025
- Date closed:
- Kind: Segmentation Fault
- Configuration: Free-Threaded
- Python versions: 3.14
- Status: Open
- PRs (author):
  - [132298](https://github.com/python/cpython/pull/132298) (@ZeroIntensity)

<details><summary>Backtrace/error message:</summary>
<p>


```shell
Thread 1 "python" received signal SIGSEGV, Segmentation fault.
0x000055555594b3fb in setup_tracing (tstate=tstate@entry=0x555555e29760, func=func@entry=0x5555559984b0 <trace_trampoline>, arg=arg@entry=(), old_traceobj=old_traceobj@entry=0x7fffffffd380) at Python/legacy_tracing.c:588
588         tstate->interp->sys_tracing_threads += delta;
(gdb) bt
#0  0x000055555594b3fb in setup_tracing (tstate=tstate@entry=0x555555e29760, func=func@entry=0x5555559984b0 <trace_trampoline>,
    arg=arg@entry=(), old_traceobj=old_traceobj@entry=0x7fffffffd380) at Python/legacy_tracing.c:588
#1  0x000055555594c141 in _PyEval_SetTrace (tstate=tstate@entry=0x555555e29760, func=func@entry=0x5555559984b0 <trace_trampoline>,
    arg=arg@entry=()) at Python/legacy_tracing.c:610
#2  0x000055555584cd32 in PyEval_SetTraceAllThreads (func=0x5555559984b0 <trace_trampoline>, arg=()) at Python/ceval.c:2473
#3  0x000055555599698e in sys__settraceallthreads (module=<optimized out>, arg=<optimized out>) at ./Python/sysmodule.c:1187
#4  0x00005555557110b6 in cfunction_vectorcall_O (
    func=<built-in method _settraceallthreads of module object at remote 0x20000259930>, args=<optimized out>,
    nargsf=<optimized out>, kwnames=<optimized out>) at Objects/methodobject.c:537
#5  0x00005555556817dd in _PyObject_VectorcallTstate (tstate=0x555555d8a858 <_PyRuntime+361432>,
    callable=<built-in method _settraceallthreads of module object at remote 0x20000259930>, args=0x7fffffffd708,
    nargsf=9223372036854775809, kwnames=0x0) at ./Include/internal/pycore_call.h:169
#6  0x00005555556818fc in PyObject_Vectorcall (
    callable=callable@entry=<built-in method _settraceallthreads of module object at remote 0x20000259930>,
    args=args@entry=0x7fffffffd708, nargsf=<optimized out>, kwnames=kwnames@entry=0x0) at Objects/call.c:327
#7  0x000055555585575c in _PyEval_EvalFrameDefault (tstate=tstate@entry=0x555555d8a858 <_PyRuntime+361432>, frame=0x7ffff7fb0098,
    frame@entry=0x7ffff7fb0020, throwflag=throwflag@entry=0) at Python/generated_cases.c.h:1434
#8  0x0000555555888b6d in _PyEval_EvalFrame (throwflag=0, frame=0x7ffff7fb0020, tstate=0x555555d8a858 <_PyRuntime+361432>)
    at ./Include/internal/pycore_ceval.h:119
```
</p>
</details>

----------


#### 47- [132386](https://github.com/python/cpython/issues/132386) - Segfault or failed assertion (`obj != NULL`) in `PyStackRef_FromPyObjectSteal`

```python
class WeirdDict(dict): pass

ns = {}
exec("def __create_fn__():\n return a", WeirdDict({None: None}), ns)
ns['__create_fn__']()
```

- Issue Number: 132386
- Date filed: 11/04/2025
- Date closed: 11/04/2025
- Kind: Segmentation Fault
- Configuration: Release
- Python versions: 3.14
- Status: Closed-Completed
- PRs (author):
  - [132412](https://github.com/python/cpython/pull/132412) (@tomasr8)

<details><summary>Backtrace/error message:</summary>
<p>


```shell
Program received signal SIGSEGV, Segmentation fault.
_PyEval_LoadGlobalStackRef (globals=<optimized out>, builtins=<optimized out>, name=0x555555aeace0 <_PyRuntime+80128>, writeto=0x7ffff7fb00f8) at Python/ceval.c:3317
3317            *writeto = PyStackRef_FromPyObjectSteal(res);
(gdb) bt
#0  _PyEval_LoadGlobalStackRef (globals=<optimized out>, builtins=<optimized out>,
    name=0x555555aeace0 <_PyRuntime+80128>, writeto=0x7ffff7fb00f8) at Python/ceval.c:3317
#1  0x00005555555e22f2 in _PyEval_EvalFrameDefault (tstate=0x555555b24178 <_PyRuntime+314776>,
    frame=<optimized out>, throwflag=<optimized out>) at Python/generated_cases.c.h:9073
#2  0x00005555557ab807 in _PyEval_EvalFrame (throwflag=0, frame=0x7ffff7fb0020,
    tstate=0x555555b24178 <_PyRuntime+314776>) at ./Include/internal/pycore_ceval.h:119
#3  _PyEval_Vector (args=0x0, argcount=0, kwnames=0x0, locals=0x7ffff7a4d240, func=0x7ffff7a50f60,
    tstate=0x555555b24178 <_PyRuntime+314776>) at Python/ceval.c:1913
#4  PyEval_EvalCode (co=co@entry=0x7ffff7bf5920, globals=globals@entry=0x7ffff7a4d240,
    locals=locals@entry=0x7ffff7a4d240) at Python/ceval.c:829
#5  0x000055555581f3bc in run_eval_code_obj (locals=0x7ffff7a4d240, globals=0x7ffff7a4d240,
    co=0x7ffff7bf5920, tstate=0x555555b24178 <_PyRuntime+314776>) at Python/pythonrun.c:1365
#6  run_mod (mod=<optimized out>, filename=filename@entry=0x7ffff7a066b0,
    globals=globals@entry=0x7ffff7a4d240, locals=locals@entry=0x7ffff7a4d240,
    flags=flags@entry=0x7fffffffdc18, arena=arena@entry=0x7ffff7b5e210, interactive_src=0x0,
    generate_new_source=0) at Python/pythonrun.c:1436
#7  0x0000555555821456 in pyrun_file (flags=0x7fffffffdc18, closeit=1, locals=0x7ffff7a4d240,
    globals=0x7ffff7a4d240, start=257, filename=0x7ffff7a066b0, fp=0x555555b97510)
    at Python/pythonrun.c:1293
```
</p>
</details>

----------


#### 48- [132461](https://github.com/python/cpython/issues/132461) - Abort from calling `OrderedDict.setdefault` with an invalid value

```python
from abc import ABCMeta
from random import randint

large_num = 2**64
class WeirdBase(ABCMeta):
  def __hash__(self):
    return randint(0, large_num)


class weird_bytes(bytes, metaclass=WeirdBase):
    pass

from collections import OrderedDict

obj = OrderedDict()

for x in range(100):
    obj.setdefault(weird_bytes, None)
```

- Issue Number: 132461
- Date filed: 13/04/2025
- Date closed:
- Kind: Abort
- Configuration: Debug
- Python versions: 3.14
- Status: Open
- PRs (author):
  - [132462](https://github.com/python/cpython/pull/132462) (@dura0ok)

<details><summary>Backtrace/error message:</summary>
<p>


```shell
python: Objects/odictobject.c:1036: OrderedDict_setdefault_impl: Assertion `_odict_find_node(self, key) == NULL' failed.

Program received signal SIGABRT, Aborted.
```
</p>
</details>

----------


#### 49- [132551](https://github.com/python/cpython/issues/132551) - Segfault/abort from calling `BytesIO` `unshare_buffer` in threads on a free-threaded build

```python
from io import BytesIO
from threading import Thread
from time import sleep


def call_getbuffer(obj: BytesIO) -> None:
    obj.getvalue()
    obj.getbuffer()
    obj.getbuffer()
    sleep(0.001)
    obj.getbuffer()
    obj.getbuffer()
    obj.getbuffer()
    sleep(0.006)
    obj.getbuffer()
    obj.getvalue()

for x in range(100):
    alive = []

    obj = BytesIO()
    for x in range(50):
        alive.append(Thread(target=call_getbuffer, args=(obj,)))
        alive.append(Thread(target=call_getbuffer, args=(obj,)))
        alive.append(Thread(target=call_getbuffer, args=(obj,)))

    alive.append(Thread(target=obj.__exit__, args=(None, None, None)))
    alive.append(Thread(target=call_getbuffer, args=(obj,)))
    alive.append(Thread(target=call_getbuffer, args=(obj,)))
    alive.append(Thread(target=call_getbuffer, args=(obj,)))

    for t in alive:
        t.start()
    for t in alive:
        t.join()
```

- Issue Number: 132551
- Date filed: 15/04/2025
- Date closed: 08/05/2025
- Kind: Segmentation Fault
- Configuration: Free-Threaded
- Python versions: 3.13, 3.14
- Status: Closed-Completed
- PRs (author):
  - [132616](https://github.com/python/cpython/pull/132616) (@tom-pytel)

<details><summary>Backtrace/error message:</summary>
<p>


```shell
Thread 613 "Thread-612 (cal" received signal SIGSEGV, Segmentation fault.

bytesiobuf_getbuffer (op=0x48ec60f00f0, view=0x48ec61101b0, flags=284) at ./Modules/_io/bytesio.c:1090
1090        if (b->exports == 0 && SHARED_BUF(b)) {

#0  bytesiobuf_getbuffer (op=0x48ec60f00f0, view=0x48ec61101b0, flags=284) at ./Modules/_io/bytesio.c:1090
#1  0x00005555556c6519 in _PyManagedBuffer_FromObject (flags=284, base=0x48ec60f00f0)
    at Objects/memoryobject.c:97
#2  PyMemoryView_FromObjectAndFlags (flags=284, v=0x48ec60f00f0) at Objects/memoryobject.c:813
#3  PyMemoryView_FromObject (v=v@entry=0x48ec60f00f0) at Objects/memoryobject.c:856
#4  0x00005555558b98bf in _io_BytesIO_getbuffer_impl (cls=<optimized out>, self=0x48ebe9f8020)
    at ./Modules/_io/bytesio.c:337
#5  _io_BytesIO_getbuffer (self=0x48ebe9f8020, cls=<optimized out>, args=<optimized out>,
    nargs=<optimized out>, kwnames=<optimized out>) at ./Modules/_io/clinic/bytesio.c.h:103
#6  0x0000555555652cb7 in _PyObject_VectorcallTstate (kwnames=<optimized out>, nargsf=<optimized out>,
    args=<optimized out>, callable=0x48ebe3e6ae0, tstate=0x555555c0bb70)
    at ./Include/internal/pycore_call.h:169
#7  PyObject_Vectorcall (callable=0x48ebe3e6ae0, args=<optimized out>, nargsf=<optimized out>,
    kwnames=<optimized out>) at Objects/call.c:327
#8  0x00005555555e9486 in _PyEval_EvalFrameDefault (tstate=<optimized out>, frame=<optimized out>,
    throwflag=<optimized out>) at Python/generated_cases.c.h:3850
#9  0x00005555557d01de in _PyEval_EvalFrame (throwflag=0, frame=<optimized out>, tstate=0x555555c0bb70)
    at ./Include/internal/pycore_ceval.h:119
#10 _PyEval_Vector (tstate=0x555555c0bb70, func=0x48ebe713f00, locals=0x0, args=0x7fff85791958,
    argcount=<optimized out>, kwnames=<optimized out>) at Python/ceval.c:1913
#11 0x0000555555656b23 in _PyObject_VectorcallTstate (kwnames=0x0, nargsf=1, args=0x7fff85791958,
    callable=0x48ebe713f00, tstate=0x555555c0bb70) at ./Include/internal/pycore_call.h:169
#12 method_vectorcall (method=<optimized out>, args=0x7fff85791c68, nargsf=<optimized out>, kwnames=0x0)
    at Objects/classobject.c:72
#13 0x00005555557eeac6 in _PyObject_VectorcallTstate (kwnames=0x0, nargsf=0, args=0x7fff85791c68,
    callable=0x48ec60d0100, tstate=0x555555c0bb70) at ./Include/internal/pycore_call.h:169
#14 context_run (self=0x48ebea12fc0, args=<optimized out>, nargs=<optimized out>, kwnames=<optimized out>)
    at Python/context.c:728
#15 0x00005555555ee959 in _PyEval_EvalFrameDefault (tstate=<optimized out>, frame=<optimized out>,
    throwflag=<optimized out>) at Python/generated_cases.c.h:3521
#16 0x00005555557d01de in _PyEval_EvalFrame (throwflag=0, frame=<optimized out>, tstate=0x555555c0bb70)
    at ./Include/internal/pycore_ceval.h:119
#17 _PyEval_Vector (tstate=0x555555c0bb70, func=0x48ebe713fc0, locals=0x0, args=0x7fff85791da8,
    argcount=<optimized out>, kwnames=<optimized out>) at Python/ceval.c:1913
#18 0x0000555555656b23 in _PyObject_VectorcallTstate (kwnames=0x0, nargsf=1, args=0x7fff85791da8,
    callable=0x48ebe713fc0, tstate=0x555555c0bb70) at ./Include/internal/pycore_call.h:169
#19 method_vectorcall (method=<optimized out>, args=0x555555b41890 <_PyRuntime+114512>,
    nargsf=<optimized out>, kwnames=0x0) at Objects/classobject.c:72
#20 0x00005555558f0221 in thread_run (boot_raw=0x555555c07040) at ./Modules/_threadmodule.c:353
#21 0x000055555586c03b in pythread_wrapper (arg=<optimized out>) at Python/thread_pthread.h:242
#22 0x00007ffff7d32ac3 in start_thread (arg=<optimized out>) at ./nptl/pthread_create.c:442
#23 0x00007ffff7dc4850 in clone3 () at ../sysdeps/unix/sysv/linux/x86_64/clone3.S:81
```
</p>
</details>

----------


#### 50- [132707](https://github.com/python/cpython/issues/132707) - Segfault in free-threaded build from interaction of nested list/tuple repr

```python
import sys

# Not sure what this weird_cls dance is doing, but it seems necessary somehow
class weird_cls(int): pass
weird_instances = {"weird_int_empty": weird_cls()}
weird_classes = {"weird_int": weird_cls}
weird_instances["weird_int_10**default_max_str_digits+1"] = weird_classes["weird_int"](10 ** (sys.int_info.default_max_str_digits + 1))

import gc
from threading import Thread
from time import sleep

def stress_list():
    sleep(0.1)
    target.append(None)
    repr(gc.get_objects())
    target.append(None)

for x in range(40):
    target = []
    alive = []
    for x in range(15):
        alive.append(Thread(target=stress_list, args=()))
    for t in alive:
        t.start()
    gc.collect()
```

- Issue Number: 132707
- Date filed: 18/04/2025
- Date closed: 18/04/2025
- Kind: Segmentation Fault
- Configuration: Free-Threaded
- Python versions: 3.14
- Status: Closed-Not-Planned
- PRs (author):
  - None

<details><summary>Backtrace/error message:</summary>
<p>


```shell
Thread 82 "Thread-81 (stre" received signal SIGSEGV, Segmentation fault.
[Switching to Thread 0x7fff8c0ac640 (LWP 3996396)]
0x0000555555cc0686 in _Py_TYPE (ob=0x0) at ./Include/object.h:270
270             return ob->ob_type;

#0  0x0000555555cc0686 in _Py_TYPE (ob=0x0) at ./Include/object.h:270
#1  PyUnicodeWriter_WriteRepr (writer=writer@entry=0x7fff4a090850, obj=0x0)
    at Objects/unicodeobject.c:13947
#2  0x0000555555bfaebb in tuple_repr (self=(<str_ascii_iterator at remote 0x7fff440f0a60>, 0x0))
    at Objects/tupleobject.c:271
#3  0x0000555555b8949a in PyObject_Repr (v=(<str_ascii_iterator at remote 0x7fff440f0a60>, 0x0))
    at Objects/object.c:776
#4  0x0000555555cc06a1 in PyUnicodeWriter_WriteRepr (writer=writer@entry=0x7fff4a0907f0, obj=0x0)
    at Objects/unicodeobject.c:13951
#5  0x0000555555aeba03 in list_repr_impl (v=0x7fff4a0c1d50) at Objects/listobject.c:606
#6  list_repr (
    self=[<Name(id='self', ctx=<Load at remote 0x7fffb63421e0>, lineno=1, col_offset=18, end_lineno=1, end_col_offset=22) at remote 0x7fff44450620>, <Attribute(value=<...>, attr='run', ctx=<...>, lineno=1, col_offset=18, end_lineno=1, end_col_offset=26) at remote 0x7fff444505c0>, <Name(id='self', ctx=<...>, lineno=1, col_offset=0, end_lineno=1, end_col_offset=4) at remote 0x7fff44450560>, <Attribute(value=<...>, attr='_context', ctx=<...>, lineno=1, col_offset=0, end_lineno=1, end_col_offset=13) at remote 0x7fff44450500>, <Attribute(value=<...>, attr='run', ctx=<...>, lineno=1, col_offset=0, end_lineno=1, end_col_offset=17) at remote 0x7fff444504a0>, <Call(func=<...>, args=[<...>], keywords=[], lineno=1, col_offset=0, end_lineno=1, end_col_offset=27) at remote 0x7fff44450440>, <Expr(value=<...>, lineno=1, col_offset=0, end_lineno=1, end_col_offset=27) at remote 0x7fff444503e0>, <Module(body=[<...>], type_ignores=[]) at remote 0x7fff44450380>, <suppress(_exceptions=(<type at remote 0x555556550d00>, <type at remote 0x55...(truncated)) at Objects/listobject.c:633
#7  0x0000555555b8949a in PyObject_Repr (
    v=[<Name(id='self', ctx=<Load at remote 0x7fffb63421e0>, lineno=1, col_offset=18, end_lineno=1, end_col_offset=22) at remote 0x7fff44450620>, <Attribute(value=<...>, attr='run', ctx=<...>, lineno=1, col_offset=18, end_lineno=1, end_col_offset=26) at remote 0x7fff444505c0>, <Name(id='self', ctx=<...>, lineno=1, col_offset=0, end_lineno=1, end_col_offset=4) at remote 0x7fff44450560>, <Attribute(value=<...>, attr='_context', ctx=<...>, lineno=1, col_offset=0, end_lineno=1, end_col_offset=13) at remote 0x7fff44450500>, <Attribute(valu--Type <RET> for more, q to quit, c to continue without paging--c
e=<...>, attr='run', ctx=<...>, lineno=1, col_offset=0, end_lineno=1, end_col_offset=17) at remote 0x7fff444504a0>, <Call(func=<...>, args=[<...>], keywords=[], lineno=1, col_offset=0, end_lineno=1, end_col_offset=27) at remote 0x7fff44450440>, <Expr(value=<...>, lineno=1, col_offset=0, end_lineno=1, end_col_offset=27) at remote 0x7fff444503e0>, <Module(body=[<...>], type_ignores=[]) at remote 0x7fff44450380>, <suppress(_exceptions=(<type at remote 0x555556550d00>, <type at remote 0x55...(truncated)) at Objects/object.c:776
#8  0x0000555555e07abf in _PyEval_EvalFrameDefault (tstate=<optimized out>, frame=<optimized out>, throwflag=<optimized out>) at Python/generated_cases.c.h:2306
#9  0x0000555555ddcf53 in _PyEval_EvalFrame (tstate=0x52900037a210, frame=0x5290003c5328, throwflag=0) at ./Include/internal/pycore_ceval.h:119
#10 _PyEval_Vector (tstate=0x52900037a210, func=0x7fffb4a9a110, locals=0x0, args=<optimized out>, argcount=1, kwnames=0x0) at Python/ceval.c:1917
#11 0x0000555555a4f42b in _PyObject_VectorcallTstate (tstate=0x52900037a210, callable=<function at remote 0x7fffb4a9a110>, args=0x0, nargsf=0, nargsf@entry=1, kwnames=kwnames@entry=0x0) at ./Include/internal/pycore_call.h:169
#12 0x0000555555a4ccbf in method_vectorcall (method=<optimized out>, args=<optimized out>, nargsf=<optimized out>, kwnames=<optimized out>) at Objects/classobject.c:72
#13 0x0000555555e8005b in _PyObject_VectorcallTstate (tstate=0x52900037a210, callable=<method at remote 0x7fff4a0c0790>, args=0x7fff8c0ab6d8, nargsf=0, kwnames=0x0) at ./Include/internal/pycore_call.h:169
#14 context_run (self=<_contextvars.Context at remote 0x7fffb4675a70>, args=<optimized out>, nargs=<optimized out>, kwnames=0x0) at Python/context.c:728
#15 0x0000555555e0a3e7 in _PyEval_EvalFrameDefault (tstate=<optimized out>, frame=<optimized out>, throwflag=<optimized out>) at Python/generated_cases.c.h:3551
#16 0x0000555555ddcf53 in _PyEval_EvalFrame (tstate=0x52900037a210, frame=0x5290003c5220, throwflag=0) at ./Include/internal/pycore_ceval.h:119
#17 _PyEval_Vector (tstate=0x52900037a210, func=0x7fffb4a9a1f0, locals=0x0, args=<optimized out>, argcount=1, kwnames=0x0) at Python/ceval.c:1917
#18 0x0000555555a4f42b in _PyObject_VectorcallTstate (tstate=0x52900037a210, callable=<function at remote 0x7fffb4a9a1f0>, args=0x0, nargsf=0, nargsf@entry=1, kwnames=kwnames@entry=0x0) at ./Include/internal/pycore_call.h:169
#19 0x0000555555a4ccbf in method_vectorcall (method=<optimized out>, args=<optimized out>, nargsf=<optimized out>, kwnames=<optimized out>) at Objects/classobject.c:72
#20 0x000055555612e2ee in thread_run (boot_raw=boot_raw@entry=0x507000006770) at ./Modules/_threadmodule.c:353
#21 0x0000555555fe7a8d in pythread_wrapper (arg=<optimized out>) at Python/thread_pthread.h:242
#22 0x000055555585cd47 in asan_thread_start(void*) ()
#23 0x00007ffff7cfeac3 in start_thread (arg=<optimized out>) at ./nptl/pthread_create.c:442
#24 0x00007ffff7d90850 in clone3 () at ../sysdeps/unix/sysv/linux/x86_64/clone3.S:81
```
</p>
</details>

----------


#### 51- [132713](https://github.com/python/cpython/issues/132713) - Segfault in `union_repr` from `list_repr_impl` in free-threaded build

```python
import abc
import builtins
import collections.abc
import itertools
import types
import typing
from functools import reduce
from operator import or_

abc_types = [cls for cls in abc.__dict__.values() if isinstance(cls, type)]
builtins_types = [cls for cls in builtins.__dict__.values() if isinstance(cls, type)]
collections_abc_types = [cls for cls in collections.abc.__dict__.values() if isinstance(cls, type)]
collections_types = [cls for cls in collections.__dict__.values() if isinstance(cls, type)]
itertools_types = [cls for cls in itertools.__dict__.values() if isinstance(cls, type)]
types_types = [cls for cls in types.__dict__.values() if isinstance(cls, type)]
typing_types = [cls for cls in typing.__dict__.values() if isinstance(cls, type)]

all_types = (abc_types + builtins_types + collections_abc_types + collections_types + itertools_types
             + types_types + typing_types)
all_types = [t for t in all_types if not issubclass(t, BaseException)]
BIG_UNION = reduce(or_, all_types, int)

from threading import Thread
from time import sleep

for x in range(100):
    union_list = [int | BIG_UNION] * 17

    def stress_list():
        for x in range(3):
            try:
                union_list.pop()
            except Exception:
                pass
            repr(union_list)
            sleep(0.006)
        union_list.__getitem__(None, None)

    alive = []
    for x in range(25):
        alive.append(Thread(target=stress_list, args=()))

    for t in alive:
        t.start()
```

- Issue Number: 132713
- Date filed: 19/04/2025
- Date closed: 23/04/2025
- Kind: Segmentation Fault
- Configuration: Free-Threaded
- Python versions: 3.13, 3.14
- Status: Closed-Completed
- PRs (author):
  - [132801](https://github.com/python/cpython/pull/132801) (@vstinner)
  - [132802](https://github.com/python/cpython/pull/132802) (@vstinner)
  - [132809](https://github.com/python/cpython/pull/132809) (@vstinner)
  - [132811](https://github.com/python/cpython/pull/132811) (@vstinner)
  - [132839](https://github.com/python/cpython/pull/132839) (@vstinner)
  - [132899](https://github.com/python/cpython/pull/132899) (@vstinner)

<details><summary>Backtrace/error message:</summary>
<p>


```shell
Thread 60 "Thread-59 (stre" received signal SIGSEGV, Segmentation fault.

0x0000555555d21751 in _Py_TYPE (ob=<unknown at remote 0xdddddddddddddddd>) at ./Include/object.h:270
270             return ob->ob_type;

#0  0x0000555555d21751 in _Py_TYPE (ob=<unknown at remote 0xdddddddddddddddd>) at ./Include/object.h:270
#1  union_repr (self=<optimized out>) at Objects/unionobject.c:296
#2  0x0000555555b8949a in PyObject_Repr (v=<unknown at remote 0x7fffb48464b0>) at Objects/object.c:776
#3  0x0000555555cc06a1 in PyUnicodeWriter_WriteRepr (writer=writer@entry=0x7fff660907f0,
    obj=<unknown at remote 0x207c>) at Objects/unicodeobject.c:13951
#4  0x0000555555aeba03 in list_repr_impl (v=0x7fffb4a8dc90) at Objects/listobject.c:606
#5  list_repr (self=[]) at Objects/listobject.c:633
#6  0x0000555555b8949a in PyObject_Repr (v=[]) at Objects/object.c:776
#7  0x0000555555e07abf in _PyEval_EvalFrameDefault (tstate=<optimized out>, frame=<optimized out>,
    throwflag=<optimized out>) at Python/generated_cases.c.h:2306
#8  0x0000555555ddcf53 in _PyEval_EvalFrame (tstate=0x529000325210, frame=0x529000384328, throwflag=0)
    at ./Include/internal/pycore_ceval.h:119
#9  _PyEval_Vector (tstate=0x529000325210, func=0x7fffb4828dd0, locals=0x0, args=<optimized out>,
    argcount=1, kwnames=0x0) at Python/ceval.c:1917
#10 0x0000555555a4f42b in _PyObject_VectorcallTstate (tstate=0x529000325210,
    callable=<function at remote 0x7fffb4828dd0>, args=0x207c, nargsf=3, nargsf@entry=1,
    kwnames=<unknown at remote 0x7fff66090450>, kwnames@entry=0x0) at ./Include/internal/pycore_call.h:169
#11 0x0000555555a4ccbf in method_vectorcall (method=<optimized out>, args=<optimized out>,
    nargsf=<optimized out>, kwnames=<optimized out>) at Objects/classobject.c:72
#12 0x0000555555e8005b in _PyObject_VectorcallTstate (tstate=0x529000325210,
    callable=<method at remote 0x7fff660c0eb0>, args=0x7fff93df06d8, nargsf=0, kwnames=0x0)
    at ./Include/internal/pycore_call.h:169
#13 context_run (self=<_contextvars.Context at remote 0x7fffb4a8ebf0>, args=<optimized out>,
    nargs=<optimized out>, kwnames=0x0) at Python/context.c:728
#14 0x0000555555e0a3e7 in _PyEval_EvalFrameDefault (tstate=<optimized out>, frame=<optimized out>,
    throwflag=<optimized out>) at Python/generated_cases.c.h:3551
```
</p>
</details>

----------


#### 52- [133441](https://github.com/python/cpython/issues/133441) - 3.13: Abort from failed assertion in `_PyEval_EvalFrameDefault`

```python
import copy

class Node:
    def __init__(self):
        self._parents = {}

    def __getstate__(self):
        return {'_parents': {}}

    def __setstate__(self, data_dict):
        self.__dict__ = data_dict
        self._parents = {}

    def call_copy(self):
        copy.copy(super())

class D(dict): pass

obj = Node()
obj.call_copy()
obj.call_copy()
obj.__setstate__(D())
```

- Issue Number: 133441
- Date filed: 05/05/2025
- Date closed:
- Kind: Abort
- Configuration: Debug
- Python versions: 3.13
- Status: Open
- PRs (author):
  - [133446](https://github.com/python/cpython/pull/133446) (@vstinner)

<details><summary>Backtrace/error message:</summary>
<p>


```shell
python: Python/generated_cases.c.h:5594: _PyEval_EvalFrameDefault: Assertion `PyDict_CheckExact((PyObject *)dict)' failed.

#0  __pthread_kill_implementation (threadid=<optimized out>, signo=6, no_tid=0)
    at ./nptl/pthread_kill.c:44
#1  __pthread_kill_internal (threadid=<optimized out>, signo=6) at ./nptl/pthread_kill.c:78
#2  __GI___pthread_kill (threadid=<optimized out>, signo=signo@entry=6)
    at ./nptl/pthread_kill.c:89
#3  0x00007ffff7c4519e in __GI_raise (sig=sig@entry=6) at ../sysdeps/posix/raise.c:26
#4  0x00007ffff7c28902 in __GI_abort () at ./stdlib/abort.c:79
#5  0x00007ffff7c2881e in __assert_fail_base (
    fmt=0x7ffff7dde2a0 "%s%s%s:%u: %s%sAssertion `%s' failed.\n%n",
    assertion=assertion@entry=0x55555590a6c0 "PyDict_CheckExact((PyObject *)dict)",
    file=file@entry=0x5555558cbb1f "Python/generated_cases.c.h", line=line@entry=5594,
    function=function@entry=0x555555964500 <__PRETTY_FUNCTION__.72> "_PyEval_EvalFrameDefault")
    at ./assert/assert.c:96
#6  0x00007ffff7c3b7c7 in __assert_fail (
    assertion=assertion@entry=0x55555590a6c0 "PyDict_CheckExact((PyObject *)dict)",
    file=file@entry=0x5555558cbb1f "Python/generated_cases.c.h", line=line@entry=5594,
    function=function@entry=0x555555964500 <__PRETTY_FUNCTION__.72> "_PyEval_EvalFrameDefault")
    at ./assert/assert.c:105
#7  0x00005555557b1e76 in _PyEval_EvalFrameDefault (tstate=0x555555b604c0 <_PyRuntime+299040>,
    frame=0x7ffff7fb0090, throwflag=0) at Python/generated_cases.c.h:5594
#8  0x00005555557b4b05 in _PyEval_EvalFrame (
    tstate=tstate@entry=0x555555b604c0 <_PyRuntime+299040>, frame=<optimized out>,
    throwflag=throwflag@entry=0) at ./Include/internal/pycore_ceval.h:119
#9  0x00005555557b4c34 in _PyEval_Vector (tstate=tstate@entry=0x555555b604c0 <_PyRuntime+299040>,
    func=func@entry=0x7ffff74674d0, locals=locals@entry=0x7ffff7463d70, args=args@entry=0x0,
    argcount=argcount@entry=0, kwnames=kwnames@entry=0x0) at Python/ceval.c:1816
#10 0x00005555557b4cf7 in PyEval_EvalCode (co=co@entry=0x7ffff7566d40,
    globals=globals@entry=0x7ffff7463d70, locals=locals@entry=0x7ffff7463d70)
    at Python/ceval.c:604
#11 0x00005555558225c5 in run_eval_code_obj (
    tstate=tstate@entry=0x555555b604c0 <_PyRuntime+299040>, co=co@entry=0x7ffff7566d40,
    globals=globals@entry=0x7ffff7463d70, locals=locals@entry=0x7ffff7463d70)
    at Python/pythonrun.c:1381
```
</p>
</details>

----------

