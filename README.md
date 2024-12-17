# aoc-nvim

A Neovim plugin for Advent of Code that helps with downloading inputs, submitting solutions, and more!

## Features

- Automatically download input files
- Submit solutions directly from Neovim
- Execution timing for operations
- Directory-based day/year detection
- Session cookie management

## Installation

Using [lazy.nvim](https://github.com/folke/lazy.nvim):

```lua
{
    'yourusername/aoc-nvim',
    dependencies = {
        'neovim/pynvim',
    },
    config = function()
        -- Optional: Set your session cookie here
        vim.g.aoc_session_cookie = 'your_cookie_here'
    end
}
```

## Requirements

- Neovim >= 0.8.0
- Python >= 3.11
- pynvim

## Setup

1. Install the plugin using your package manager
2. Install pynvim: `pip install pynvim`
3. Set your Advent of Code session cookie:
   - Either in your config: `vim.g.aoc_session_cookie = 'your_cookie'`
   - Or using the command: `:AocSetCookie your_cookie`

To get your session cookie:

1. Log into Advent of Code in your browser
2. Open DevTools (F12)
3. Go to Application/Storage > Cookies
4. Copy the value of the 'session' cookie

## Usage

The plugin expects your working directory to be structured as:

```shell
parent/
  aoc2023/
    day1/
    day2/
    ...
  aoc2024/
    day1/
    day2/
    ...
```

### Commands

- `:AocDownload` - Download input for the current day
- `:AocSubmit 1` - Submit the current line/selection as solution for part 1
- `:AocSubmit 2` - Submit the current line/selection as solution for part 2
- `:AocSetCookie <cookie>` - Set your session cookie

### Example Workflow

1. Create a new day directory: `mkdir -p aoc2024/day1`
2. CD into it: `cd aoc2024/day1`
3. Run `:AocDownload` to get your input
4. Solve the puzzle
5. Submit your answer with `:AocSubmit 1` or `:AocSubmit 2`

## License

MIT
