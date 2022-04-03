# La TeXtractor – Get your LaTeX zipped up!

Do you find yourself sometimes in need of a neat and clean zip archive with the
essential artefacts of your LaTeX project? Maybe to submit it along with the
camera-ready PDF of your paper?

**The times when you manually cleaned out your project directory are over!**

We present: **La TeXtractor** a tool that takes care of everything for you (no
warranty!!)


## Usage

Simply run `textract -m paper.tex camera-ready.zip` and you are done.

Really, that's almost it. Check out `textract --help` for the more advanced
power-user features like

- include additional files (like a copyright form)
- get a directory with all files in the zip for extra reassurance

## How it works

To be honest: It's not hard. LaTeX's `-recorder` option does the heavy lifting
by listing all files that are accessed during a build run.
La TeXtractor just takes all (non-global) build assets from that list and zips
them up.
To make sure that everything that is needed for a build is included, La
TeXtractor test the build on a copy of the zip,
and prints a reassuring success message if all goes right.
