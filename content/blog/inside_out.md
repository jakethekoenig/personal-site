For the longest time I've used vim and tmux together for development. But in 2024 terminal support in vim and neovim is very good and there is very little reason to use tmux [[I wanted to give this post a more clickbaity subheading like "ditching tmux" but I still open all my vim sessions in tmux. Partly to handle flaky terminal sessions (I'm not sshing anywhere mostly but I have a lot of ctrl-W muscle memory and alacritty doesn't give you any kind of confirmation), to enable switching terminals later and just in case I actually do want to use it to make a split.]]. In vim or neovim you can open a new terminal by running `:term`. The exact bindings to do things like switch back to normal mode differ between the two. Commands in this post are only confirmed to work for neovim.

Opening your terminal sessions in vim feels like a small change but makes many things possible:
* When you run a command that outputs file names e.g. grep, pytest, you can go to that file by positioning your cursor on the sting and typing `gf`. What is the best way to do this with tmux? Yank the file to the buffer, go to your vim session and write `:e &lt;prefix&gt;p`? Seems horrible.
* You can have the same colorscheme and settings like relative line numbers in your vim and terminal session.
* It's so much easier to get things into the system clipboard register `+` on vim then on tmux. It appears people recommend plugins with a startling number of lines to get this same basic functionality. I don't want to talk about how I did it, it's embarrassing.
* It's generally more pleasant to yank/paste between vim and the terminal this way.
* Text completion can now complete words that appear in the terminal as well as in file buffers.
* You can make things like `*` work in tmux copy mode by setting `copy-mode-vi` but when your terminal is actually opened in vim the search history is shared.

Part of the reason I find this such an unlock is a skill issue: I never learned even 5% of the affordances tmux provides. You can make this issue less pronounced by adding a bunch of things to your tmux config:
```
# ~/.tmux.conf
# vim-like pane switching
set-window-option -g mode-keys vi
bind-key -T copy-mode-vi v send-keys -X begin-selection
bind-key -T copy-mode-vi y send-keys -X copy-selection
unbind p
bind p paste-buffer
bind -r k select-pane -U 
bind -r j select-pane -D 
bind -r h select-pane -L 
bind -r l select-pane -R 
bind -r ^ select-window -l
```
But I find there are subtle differences in the behavior between the vim motions in vim and tmux. And some vim motions I've come to rely on like `&lt;C-o&gt;` and `&lt;C-i&gt;` don't work in tmux.

## Customization

The default chord to enter normal mode from a terminal `&lt;C-\&gt;&lt;C-n&gt;` is a little painful so I recommend a bunch of vimrc settings to make it more pleasant to work with neovim's terminal. I personally use `&lt;C-x&gt;` to open a new terminal and to go from terminal mode to normal mode. And I rebind all the ctrl commands that I use in normal mode to work in terminal mode. Some of these conflict with the default emacs mode shell bindings so I recommend you switch to vim mode if you're already a vim user. You can see how to do that in my [vim tmux zsh tips post](/blog/vimuxsh). Or customize the bindings to what makes sense for your workflow.
```
" ~/.config/nvim/init.vim
nnoremap &lt;C-x&gt; :vsp&lt;CR&gt;:term&lt;CR&gt;
tnoremap &lt;C-x&gt; &lt;C-\&gt;&lt;C-n&gt;
tnoremap &lt;C-p&gt; &lt;C-\&gt;&lt;C-n&gt;:CtrlP&lt;CR&gt;
tnoremap &lt;C-o&gt; &lt;C-\&gt;&lt;C-n&gt;&lt;C-o&gt;
tnoremap &lt;C-h&gt; &lt;C-\&gt;&lt;C-n&gt;&lt;C-w&gt;&lt;C-h&gt;
tnoremap &lt;C-j&gt; &lt;C-\&gt;&lt;C-n&gt;&lt;C-w&gt;&lt;C-j&gt;
tnoremap &lt;C-k&gt; &lt;C-\&gt;&lt;C-n&gt;&lt;C-w&gt;&lt;C-k&gt;
tnoremap &lt;C-l&gt; &lt;C-\&gt;&lt;C-n&gt;&lt;C-w&gt;&lt;C-l&gt;

function! RenameTerminalBufferToCurrentCommand()
  let l:historyFile = "~/.zsh_history"
  let l:mostRecentCommand = system("tail -1 " . l:historyFile . " | cut -f2- -d\\;")
  let l:mostRecentCommand = fnameescape(trim(l:mostRecentCommand))
  if (l:mostRecentCommand == "q" || l:mostRecentCommand == "quit" || l:mostRecentCommand == "exit")
      exec "q"
      return
  endif

  " i prepend "term" for easy buffer searching
  let l:newFileName = "term " . l:mostRecentCommand

  silent! execute "keepalt file " . l:newFileName
  normal a

endfunction
tnoremap &lt;Enter&gt; &lt;Enter&gt;&lt;C-\&gt;&lt;C-n&gt;:call RenameTerminalBufferToCurrentCommand()&lt;Enter&gt;
```

The point of `RenameTerminalBufferToCurrentCommand` is to make it easy to find terminals with vim. If you start some long running commend e.g. your server, `npm run start`, a database connection, `psql` whatever  you can then close the buffer and later find it with CtrlP and it will be named after the last command you ran in it.

One last tip: if you write python you can add the following cool line to your vimrc:
```
nnoremap <leader>i :let currentfile = @% \| new \| execute 'terminal python -i '.currentfile<CR>i
```
What it does is open a python interpreter with the current file loaded when you type `&lt;leader&gt;i`. Very useful for iterative development.
