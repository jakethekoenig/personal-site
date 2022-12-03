
You can see my complete vim/zsh/tmux configurations [here](https://github.com/jakethekoenig/dotfiles). Maintaining them has become sort of a hobby and I wanted to discuss some of my favorite additions. Some men garden and others have dotfiles.

Note a lot of them are copied from other places and were often discovered when I wanted to do X and searched around for X. Some of the best sources I learned from more comprehensively are [Learn Vimscript the Hard Way](https://learnvimscriptthehardway.stevelosh.com/) and [History and Effective Use of Vim](https://begriffs.com/posts/2019-07-19-history-use-vim.html#history).

My most important configurations are those that let me quickly edit my configurations. The first one's acronyms were chosen as mneumonics "edit vimrc" and "source vimrc" the others were chosen to match.
```
" ~/.vimrc
nnoremap &lt;leader&gt;ev :split $MYVIMRC&lt;cr&gt;
nnoremap &lt;leader&gt;sv :source $MYVIMRC&lt;cr&gt;
```
```
&#35; ~/.tmux.conf
bind s source-file ~/.tmux.conf
bind e split-window -vb 'vi ~/.tmux.conf'
```
```
&#35; ~/.zshrc
alias ev='vi ~/.zshrc'
alias sv='source ~/.zshrc'
```

I edit my vimrc so often I even added a little autocmd to source it automatically
```
" ~/.vim/ftplugin/vim.vim
augroup source
	autocmd!
	autocmd BufWritePost $MYVIMRC source $MYVIMRC
augroup END
```

My second most important configurations are the ones that make zsh and tmux behave like vim.
```
&#35; ~/.zshrc
bindkey -v
bindkey jk vi-cmd-mode &#35; Chosen to match a very ergonomic vim setting
```
```
&#35; ~/.tmux.conf
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

The rest are relatively minor quality of life improvements:
```
&#35; ~/.zshrc
HISTSIZE=100000
SAVEHIST=100000
HISTFILE=~/.zsh_history
```
By default zsh only saves the previous 1000 commands. Over time you'll lose access to commands you used and you'll lose access to them just when your memory is losing access as well. My value of a million is intended to be infinity. Writing this I realize I should probably add more zeros.

A related pro tip is the existence of the zsh_history file. Generally I use `jk/` to search up in zsh (remember I've rebound to vim controls. If you don't it's `C-R`) but sometimes I can't remember enough characters of what I'm looking for to make a useful search. But I can remember something like "I used this command in such and such directory" or "I usually ran this command before or after this other command". If I remember something like that I can open the history file, search for what I remember, and then read the commands around it.

```
&#35; ~/.zshrc
alias gs='git status'
alias gst='git stash'
alias gc='git commit'
alias gco='git checkout'
alias ga='git add'
alias gd='git diff'
alias gp='git pull'
alias gpu='git push'
alias gl='git log'
```
Self explanatory. Gotta git git gud.
```
&#35; ~/.tmux.conf
bind '"' split-window -c "&#35;{pane_current_path}"
bind % split-window -h -c "&#35;{pane_current_path}"
bind c new-window -c "&#35;{pane_current_path}"
```
I feel like tmux should have a setting to enable this behavior but it doesn't. Generally when I start a new terminal I want it's working directory to be the same as the last one and this accomplishes that.

```
&#35; ~/.tmux.conf
set-option -g prefix2 Escape
```
I find `&lt;Esc&gt;` much more ergonomic than `C-B`. I'd rather avoid using two keypresses for leader. Since I've rebound enter insert mode in vim I don't really use escape for anything.

```
&#35; ~/.tmux.conf
set -g base-index 1
```
Sort of a weird one but I like to switch between windows with `Leader+index` and I'd like the index to match the physical arrangement of the keyboard. Therefore I have the index start at 1.

```
" ~/.vimrc
nnoremap &lt;C-v&gt; :set paste&lt;CR&gt;"+p:set nopaste&lt;CR&gt;
inoremap &lt;C-v&gt; &lt;Esc&gt;:set paste&lt;CR&gt;"+p:set nopaste&lt;CR&gt;a
```
These make paste work normally in insert and normal mode. The fact that they're necessary is sort of the epitome of why terminal based editors are a weird choice in 2022. Side note I haven't found a good way to copy to the clipboard from tmux. Right now I paste from a register into vim and then copy to the system register with `+` from vim. It's a lot of keypresses though and there must be a better way. All the suggestions I see involve pbcopy which I'd rather avoid if possible.

```
" ~/.vimrc
iabbrev tf therefore
iabbrev wo without
iabbrev ew elsewhere
iabbrev bc because
iabbrev sa such as
iabbrev ow otherwise
iabbrev fn function
iabbrev st such that
iabbrev te there exists
iabbrev fa for all
iabbrev wo without
```
This is just a few of the abbreviations I have in my vimrc. I actually defined [a function](https://github.com/jakethekoenig/dotfiles/blob/40634a98e3a2daf8e0379b73392436e121fd07d2/vim/vimrc#L177) which does pluralizations and capitalization abbreviations automatically as well. I don't think they actually speed up my writing that much but they're fun. 

```
" ~/.vim/ftplugin/gitcommit.vim as well we markdown.vim, tex.vim and text.vim
colorscheme morning
set spell
```

I like to keep a different vibe between "writing" and "programming" so I changed the colorscheme of filetypes I consider writing.

Once vim is in your fingers I also highly recommend [vimium](https://vimium.github.io/). It's got a lot of features but I find jk for scroll and f to click links particularly helpful. I used to supress it on sites which have their own keyboard shortcuts but now I just use i for insert mode.
