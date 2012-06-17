Repl Any
========
Use `repla` to convert any command into a shell. Think of it as a
generic repl. Or an interactive xargs. Think less typing. Think
awesomeness!

- Do you use an awesome command that has lot's of subcommands, but no
  shell?  (e.g. git, gpg) `repla` saves the day!
- Do you frequently call a certain command again and again? (e.g. make)
  `repla` saves you typing!
- Do you need to retype the same long, boring arguments to a command
  again and again, but with other options that vary? `repla` will slash
  away the repetition!

Miss your shell, and don't wanna go cold turkey? Precede your command
with a bang and it gets passed to `sh` as-is: `!rm -rf bonkers blue`

And if you use screen or [tmux][4], so much the better: Go ahead and dedicate
a window for git, or make, or whatever: Then leave repla open and ready
to go! (By the way, you should really be using [tmux][5]!)

`repla` was born of my annoyance with retyping `git cmd` all of the
time. So the focus of it's development is to make `git` (or any command)
less annoying. And it does.


How does it work?
-----------------
Simple: When you enter a line, `repla` prepends the name of the currently
wrapped command, and executes the resulting command line. Further, you
can specify a list of prefix or postfix args that get added to the
command every time.

Suddenly,

```sh
    bash$ git --work-tree=temp-tree log --stat topic_branch -- file1 file2 somedir
    bash$ git --work-tree=temp-tree diff --cached ntopic_branch -- file1 file2 somedir
    bash$ git --work-tree=temp-tree add --patch -- file1 file2 somedir
```

(211 chars)

becomes

```sh
    git: %set prefix='--work-tree=temp-tree'
    git: %set postfix='topic_branch -- file1 file2 somedir'
    git: log --stat
    git: diff --cached
    git: add --patch
```

(125 chars)

NOTE: `git: ` is the prompt; you don't have to type that!

But there's more
----------------
You can simply and easily extend `repla`'s vocabulary, by writing a
short Python class defining custom builtin methods and sticking it on
the Python path. It's as simple as writing:

```python
    from repla.command import CmdBase

    class AwesomeCommands(CmdBase):
      def cmdHello(self, args):
	self.show("Hello, world!")

      def cmdFoo(self, args):
	if len(args) == 0:
	  self.show("Nyhh!")
	elif len(args) > 1:
	  self.show("Bahh!")
	else:
	  self.show("Foo bar.")
```

and then in `repla`:

```sh
    git: %import python.path.module
    git: %hello
    Hello, world!
```

See [this][2] for details.

Features
========
- wrap any command: `%set wrapped='/path/to/my/command'`
- automatically send prefix/postfix args to the wrapped command
- Execute sh commands: `!cmd args`
- Built-in commands: `%cd`, `%pwd`, etc.
- Extensible! You can make your own built-ins with Python.

TODOs
=====
- completion functions. Preferably without duplicating half of bash's
  source. ([Suggestions?][3])
- help builtin. What use are all those shiny builtins without
  documentation? (On the way)
- allow custom builtins to execute other builtins or arbitrary command
  lines. (easy)

LICENSE
=======
`repla` is licensed under the terms of the GNU General Public License,
version 2. Please see [LICENSE][1] for details.

[1]: https://github.com/jpaugh64/repla/blob/master/LICENSE
[2]: https://github.com/jpaugh64/repla/commit/c5cca2902e526df2f09ee310ac9afc68a17ff91a
  "Importing custom commands"
[3]: https://github.com/jpaugh64/repla/issues/1
[4]: http://tmux.sourceforge.net/
[5]: http://tmux.svn.sourceforge.net/viewvc/tmux/trunk/FAQ
