Intuitively one might think that vim is less useful in the age of LLMs. The logical chain, which I used to believe, is this:

1. vim is mostly about editing text
2. LLMs will write the text for you
3. Therefore, vim is less useful

But the actual insertion step, after you've positioned your cursor, entered insert mode if necessary and type the code is essentially the same in vim, vscode or any other editor. To the extent chatgpt or copilot or whatever is writing the code for you, you actually spend more time yanking text around, exploring the codebase, and debugging than you do typing. And that is where vim could plausibly make you more productive. Not in the actual typing of code.

Perhaps one day you'll mutate your codebase without ever touching an editor just giving a high level request like "Add a button with this functionality" and the LLM will figure out where in the code base to add the button, the front and backend functionality, the tests, and any other changes your change requires. [[That's what we're working on with [mentat](https://mentat.ai) but we're still a ways away and I'm still not certain such as thing will actually be possible in the short term. Seems inevitable in the log run]] . But while we're in a hybrid regime where it's still necessary to write and understand the code you just have a smart but low context and creativity assistant, vim is actually more useful.

Another perk for vim in the age of LLMs is that it's never been easier to learn vim. LLMs are familiar with the history and all the commands and motions. And if you want a more complicated behavior your llm will be happy to chain the functions together for you. For instance last week I was curious how many lines [[895791 lines were open if you're curious. Big "that's it" moment.]] I had open across buffers so I asked Claude-3.5 Sonnet and it gave me the following command:

```
:echo reduce(filter(map(range(1, bufnr('$')), 'buflisted(v:val) && linebufnr(v:val) &gt; 0 ? linebufnr(v:val) : 0'), 'v:val'), {acc, l &gt; acc + l}, 0)
```

I asked how to get the same functionality in VSCode and it gave me an 8 step process that started with "Install Node.js" and ended with "Load your extension". Good luck!

This is sort of a toy example. But for toy examples a gain in efficiency is the difference between satisfying your curiosity or not doing it. Two other more valuable recent scripts that I got from my LLM and you may find useful are copying github links and copying markdown blocks. I use them both most days now and simply wouldn't have spent the ~30 minutes necessary to write them unassisted.

## Copy Github Link

The following command copies a link to the line of code on github. Claude one shotted this except for the branch name which it hard coded to main before I asked it to use git and the mapping to run the function which I added myself.

```
" Github
function! CopyGithubLink() abort
  " Save the current working directory
  let l:original_cwd = getcwd()

  " Change to the directory of the current file
  let l:buffer_dir = expand('%:p:h')
  execute 'cd' fnameescape(l:buffer_dir)

  " Get the current file path relative to the repo's root
  let l:file_path = system('git ls-files --full-name ' . shellescape(expand('%')))

  if v:shell_error
    echo "Not a git repository or file not tracked"
    execute 'cd' fnameescape(l:original_cwd)
    return
  endif
  let l:file_path = trim(l:file_path)

  " Get the line number
  let l:line_number = line(".")

  " Get the origin URL from git
  let l:origin_url = system("git config --get remote.origin.url")
  if v:shell_error
    echo "Not a git repository or no origin remote"
    execute 'cd' fnameescape(l:original_cwd)
    return
  endif

  " Get the current branch name
  let l:branch_name = system("git rev-parse --abbrev-ref HEAD")
  if v:shell_error
    echo "Could not determine the current branch"
    execute 'cd' fnameescape(l:original_cwd)
    return
  endif
  let l:branch_name = trim(l:branch_name)

  " Sanitizing the origin URL
  " Trim newline and other trailing whitespace
  let l:origin_url = trim(l:origin_url)

  " Convert SSH URL to HTTPS URL if needed
  if l:origin_url =~? '^git@'
    let l:origin_url = substitute(l:origin_url, '^git@\(.*\):\(.*\)$', 'https://\1/\2', '')
  endif

  " Remove ".git" suffix if present
  let l:origin_url = substitute(l:origin_url, '.git$', '', '')

  " Construct the URL to the specific line in the file
  let l:github_link = l:origin_url . '/blob/' . l:branch_name . '/' . l:file_path . '#L' . l:line_number

  " Copy the GitHub link to the system clipboard
  let @+ = l:github_link
  echo "Copied to clipboard: " . l:github_link

  " Restore the original working directory
  execute 'cd' fnameescape(l:original_cwd)
endfunction

" Create a command to call the function
command! CopyGithubLinkToClipboard call CopyGithubLink()
nnoremap &lt;leader&gt;gh :CopyGithubLinkToClipboard&lt;CR&gt;
```

## Copy markdown block

The following copies code in markdown with `yi&#96;` while preserving the default vim behavior which doesn't work across lines. It's extremely useful when you're talking to an LLM in vim [[Which I recommend doing. I use [this plugin I wrote](https://github.com/jakethekoenig/ChatVim) to talk to my LLMs in vim. It's pretty simple so you should plausibly just write your own. Or rather ask Claude to write it for you]] because they tend to use markdown code blocks to box their code snippets. The LLM almost one shotted it but it had an off by one error, I had to tell it to not count triple apostrophes that don't start the line and it was a lot of work to get it to treat registers correctly so for instance `"ayi&#96;` would copy the text to the `a` register. It kept hardcoding the register. Maybe I wasn't asking clearly. Or maybe people usually don't make their personal mappings work with registers so there's not that much training data.

```
" Function to yank markdown code block or inline code
function! YankInlineOrBlock(register) abort
    " Save current cursor position
    let l:save_pos = getpos('.')

    " Decide behavior based on current line's content
    if getline('.') =~ '\m^\s*&#96;&#96;&#96;'
        echo "Invalid position for yi&#96; command"
        return
    endif

    " Check for the presence of backticks on current line
    if getline('.') =~ '\m&#96;'
        " Yank inside inline backticks and respect register
        execute "normal! " . a:register . "vi&#96;y"
    else
        " Yank inside triple backtick block

        " Move cursor to the nearest opening triple backtick above
        let l:line = search('^\s*&#96;&#96;&#96;', 'bnW')

        " Check if we're in a proper markdown block
        if getline(l:line) !~ '^\s*&#96;&#96;&#96;'
            echo "Not inside a markdown code block"
            call setpos('.', l:save_pos)
            return
        endif

        " Move cursor to the start of the block content
        call cursor(l:line + 1, 1)

        " Yank until the closing triple backtick
        let l:end_line = search('^\s*&#96;&#96;&#96;', 'nW')

        " Check if we found the closing triple backtick
        if getline(l:end_line) !~ '^\s*&#96;&#96;&#96;'
            echo "Unmatched markdown code block"
            call setpos('.', l:save_pos)
            return
        endif

        " Put the block content into a register (default register " and for operations)
        let lines = getline(l:line + 1, l:end_line - 1)
        call setreg(a:register, lines, 'l')
        " Restore cursor position
        call setpos('.', l:save_pos)
    endif
endfunction

" Remap yi&#96; to call the function, allowing for explicit register use
nmap <silent> yi&#96; :call YankInlineOrBlock(v:register)<CR>
```

# Wider Significance

This and anthropic artifacts make me think the future of code could involve a lot of bespoke software made just for one individual's use case. Making software has historically been so expensive that for all but a few use cases one should take the off the shelf solution even if this involves significant compromises. But this balance is shifting. And software that lends itself to customization and plugins is therefore more valuable.
