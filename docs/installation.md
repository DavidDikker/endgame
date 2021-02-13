# Installation

* pip3

```bash
pip3 install --user endgame
```

* Homebrew (this will not work until the repository is public)

```bash
brew tap salesforce/endgame https://github.com/salesforce/endgame
brew install endgame
```

Now you should be able to execute `endgame` from command line by running `endgame --help`.

#### Shell Completion

* To enable Bash completion, put this in your `~/.bashrc`:

```bash
eval "$(_ENDGAME_COMPLETE=source endgame)"
```

* To enable ZSH completion, put this in your `~/.zshrc`:

```bash
eval "$(_ENDGAME_COMPLETE=source_zsh endgame)"
```
