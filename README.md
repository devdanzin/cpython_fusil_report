# Fuzzing CPython with fusil

A technical report about fuzzing CPython using fusil

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
