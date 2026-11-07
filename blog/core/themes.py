from functools import lru_cache


THEMES = {
    'default': {
        'label': 'Clásico',
        'light': {'bg': '#ffffff', 'fg': '#212121', 'accent': '#212121'},
        'dark': {'bg': '#121212', 'fg': '#f5f5f5', 'accent': '#f5f5f5'},
    },
    'dracula': {
        'label': 'Dracula',
        'light': {'bg': '#f8f8f2', 'fg': '#282a36', 'accent': '#7c3aed'},
        'dark': {'bg': '#282a36', 'fg': '#f8f8f2', 'accent': '#bd93f9'},
    },
    'monokai-pro': {
        'label': 'Monokai Pro',
        'light': {'bg': '#fafafa', 'fg': '#2d2a2e', 'accent': '#e2456b'},
        'dark': {'bg': '#2d2a2e', 'fg': '#fcfcfa', 'accent': '#ff6188'},
    },
    'nord': {
        'label': 'Nord',
        'light': {'bg': '#eceff4', 'fg': '#2e3440', 'accent': '#5e81ac'},
        'dark': {'bg': '#2e3440', 'fg': '#eceff4', 'accent': '#88c0d0'},
    },
    'material-blue': {
        'label': 'Material Blue',
        'light': {'bg': '#f5f7fa', 'fg': '#1f2d3d', 'accent': '#2196f3'},
        'dark': {'bg': '#0f1720', 'fg': '#eceff1', 'accent': '#42a5f5'},
    },
    'material-green': {
        'label': 'Material Green',
        'light': {'bg': '#f4f8f4', 'fg': '#1b2e1f', 'accent': '#43a047'},
        'dark': {'bg': '#0e1a12', 'fg': '#e8f5e9', 'accent': '#66bb6a'},
    },
    'material-pink': {
        'label': 'Material Pink',
        'light': {'bg': '#fdf3f7', 'fg': '#331f28', 'accent': '#ec407a'},
        'dark': {'bg': '#1f1218', 'fg': '#fce4ec', 'accent': '#f06292'},
    },
    'solarized': {
        'label': 'Solarized',
        'light': {'bg': '#fdf6e3', 'fg': '#586e75', 'accent': '#268bd2'},
        'dark': {'bg': '#002b36', 'fg': '#eee8d5', 'accent': '#b58900'},
    },
    'tango': {
        'label': 'Tango',
        'light': {'bg': '#f7f7f7', 'fg': '#2e3436', 'accent': '#3465a4'},
        'dark': {'bg': '#2e3436', 'fg': '#eeeeec', 'accent': '#729fcf'},
    },
    'borland': {
        'label': 'Borland',
        'light': {'bg': '#fdfdfd', 'fg': '#000040', 'accent': '#0000a0'},
        'dark': {'bg': '#000040', 'fg': '#ffffcc', 'accent': '#ff8000'},
    },
    'vscode': {
        'label': 'VS Code',
        'light': {'bg': '#ffffff', 'fg': '#1f1f1f', 'accent': '#007acc'},
        'dark': {'bg': '#1e1e1e', 'fg': '#d4d4d4', 'accent': '#569cd6'},
    },
    'ciapre': {
        'label': 'Ciapre',
        'light': {'bg': '#f4efe7', 'fg': '#3b2e2a', 'accent': '#9a5b4b'},
        'dark': {'bg': '#191919', 'fg': '#d6cdc1', 'accent': '#d98e63'},
    },
    'cobalt': {
        'label': 'Cobalt',
        'light': {'bg': '#f0f2f7', 'fg': '#193549', 'accent': '#0f6fde'},
        'dark': {'bg': '#193549', 'fg': '#e1efff', 'accent': '#4aa8ff'},
    },
    'fairy-floss': {
        'label': 'Fairy Floss',
        'light': {'bg': '#fdf6ff', 'fg': '#3d2b4f', 'accent': '#c026d3'},
        'dark': {'bg': '#2a1b33', 'fg': '#ffe9ff', 'accent': '#ff79c6'},
    },
    'flat': {
        'label': 'Flat',
        'light': {'bg': '#f4f7f8', 'fg': '#2c3e50', 'accent': '#1abc9c'},
        'dark': {'bg': '#1f2b33', 'fg': '#ecf0f1', 'accent': '#1abc9c'},
    },
    'tokyo-night': {
        'label': 'Tokyo Night',
        'light': {'bg': '#f2f4f8', 'fg': '#1a1b26', 'accent': '#3d59a1'},
        'dark': {'bg': '#1a1b26', 'fg': '#c0caf5', 'accent': '#7aa2f7'},
    },
    'horizon': {
        'label': 'Horizon',
        'light': {'bg': '#fdf0ed', 'fg': '#1c1e26', 'accent': '#da103f'},
        'dark': {'bg': '#1c1e26', 'fg': '#fdf0ed', 'accent': '#e95678'},
    },
    'everforest': {
        'label': 'Everforest',
        'light': {'bg': '#fdf6e3', 'fg': '#2f3b34', 'accent': '#8da101'},
        'dark': {'bg': '#2b3339', 'fg': '#d3c6aa', 'accent': '#a7c080'},
    },
    'gruvbox': {
        'label': 'Gruvbox',
        'light': {'bg': '#fbf1c7', 'fg': '#3c3836', 'accent': '#d65d0e'},
        'dark': {'bg': '#282828', 'fg': '#ebdbb2', 'accent': '#fe8019'},
    },
    'github': {
        'label': 'GitHub',
        'light': {'bg': '#ffffff', 'fg': '#24292f', 'accent': '#0969da'},
        'dark': {'bg': '#0d1117', 'fg': '#c9d1d9', 'accent': '#58a6ff'},
    },
    'lunaria': {
        'label': 'Lunaria',
        'light': {'bg': '#fdf7f0', 'fg': '#2e2438', 'accent': '#b96b8f'},
        'dark': {'bg': '#1f1a26', 'fg': '#f5e7ef', 'accent': '#e6a6c0'},
    },
    'novel': {
        'label': 'Novel',
        'light': {'bg': '#fbf6ec', 'fg': '#3b2f2f', 'accent': '#9c6644'},
        'dark': {'bg': '#221c18', 'fg': '#f2e6d8', 'accent': '#d4a373'},
    },
    'catppuccin': {
        'label': 'Catppuccin',
        'light': {'bg': '#eff1f5', 'fg': '#4c4f69', 'accent': '#8839ef'},
        'dark': {'bg': '#1e1e2e', 'fg': '#cdd6f4', 'accent': '#cba6f7'},
    },
    'one-dark': {
        'label': 'One Dark',
        'light': {'bg': '#fafafa', 'fg': '#383a42', 'accent': '#4078f2'},
        'dark': {'bg': '#282c34', 'fg': '#abb2bf', 'accent': '#61afef'},
    },
    'ayu': {
        'label': 'Ayu',
        'light': {'bg': '#fafafa', 'fg': '#242936', 'accent': '#fa8d3e'},
        'dark': {'bg': '#0b0e14', 'fg': '#bfbdb6', 'accent': '#e6b450'},
    },
    'rose-pine': {
        'label': 'Rosé Pine',
        'light': {'bg': '#faf4ed', 'fg': '#575279', 'accent': '#907aa9'},
        'dark': {'bg': '#191724', 'fg': '#e0def4', 'accent': '#c4a7e7'},
    },
    'kanagawa': {
        'label': 'Kanagawa',
        'light': {'bg': '#f5ede3', 'fg': '#1f1f28', 'accent': '#4a6fa5'},
        'dark': {'bg': '#1f1f28', 'fg': '#dcd7ba', 'accent': '#7e9cd8'},
    },
    'night-owl': {
        'label': 'Night Owl',
        'light': {'bg': '#f6f6f6', 'fg': '#011627', 'accent': '#2aa298'},
        'dark': {'bg': '#011627', 'fg': '#d6deeb', 'accent': '#82aaff'},
    },
    'shades-of-purple': {
        'label': 'Shades of Purple',
        'light': {'bg': '#f7f2ff', 'fg': '#2d1b4e', 'accent': '#9c27b0'},
        'dark': {'bg': '#1e1e3f', 'fg': '#e3dfff', 'accent': '#d8a0ff'},
    },
    'synthwave': {
        'label': 'Synthwave',
        'light': {'bg': '#fdf5ff', 'fg': '#2b1d3a', 'accent': '#c026a3'},
        'dark': {'bg': '#241b2f', 'fg': '#f0e6ff', 'accent': '#ff7edb'},
    },
    'palenight': {
        'label': 'Palenight',
        'light': {'bg': '#f5f7ff', 'fg': '#292d3e', 'accent': '#6d4aff'},
        'dark': {'bg': '#292d3e', 'fg': '#a6accd', 'accent': '#82aaff'},
    },
    'oceanic-next': {
        'label': 'Oceanic Next',
        'light': {'bg': '#f4f8f8', 'fg': '#1b2b34', 'accent': '#1f8f9c'},
        'dark': {'bg': '#1b2b34', 'fg': '#c0c5ce', 'accent': '#6699cc'},
    },
    'spacegray': {
        'label': 'Spacegray',
        'light': {'bg': '#f4f4f4', 'fg': '#2f343d', 'accent': '#5c7d9e'},
        'dark': {'bg': '#2f343d', 'fg': '#d8dee9', 'accent': '#7d9aba'},
    },
    'tomorrow': {
        'label': 'Tomorrow',
        'light': {'bg': '#ffffff', 'fg': '#4d4d4c', 'accent': '#4271ae'},
        'dark': {'bg': '#1d1f21', 'fg': '#c5c8c6', 'accent': '#81a2be'},
    },
    'zenburn': {
        'label': 'Zenburn',
        'light': {'bg': '#f0f0e8', 'fg': '#3f3f3f', 'accent': '#8f6f4e'},
        'dark': {'bg': '#3f3f3f', 'fg': '#dcdccc', 'accent': '#cc9393'},
    },
    'oceanic': {
        'label': 'Oceanic',
        'light': {'bg': '#f0f5f8', 'fg': '#2c3e50', 'accent': '#16876f'},
        'dark': {'bg': '#16232b', 'fg': '#d8e3ea', 'accent': '#1abc9c'},
    },
    'dusk': {
        'label': 'Dusk',
        'light': {'bg': '#f5f1ee', 'fg': '#2d2a2e', 'accent': '#b45309'},
        'dark': {'bg': '#1f1b1e', 'fg': '#ede7e3', 'accent': '#d98e48'},
    },
    'moonlight': {
        'label': 'Moonlight',
        'light': {'bg': '#f2f4fb', 'fg': '#1f2433', 'accent': '#4f6cf0'},
        'dark': {'bg': '#151824', 'fg': '#dbe2ff', 'accent': '#6f8cff'},
    },
    'papercolor': {
        'label': 'PaperColor',
        'light': {'bg': '#f7f7f7', 'fg': '#1c1c1c', 'accent': '#d75f00'},
        'dark': {'bg': '#1c1c1c', 'fg': '#eeeeee', 'accent': '#d78700'},
    },
}

DEFAULT_PALETTE = {
    'light': {
        'paper': '#ffffff', 'surface': '#ffffff', 'surface-alt': '#f4f4f4',
        'ink': '#212121', 'ink-soft': '#3d3d3d', 'muted': '#6a6a6a',
        'line': '#e5e5e5', 'line-strong': '#c7c7c7', 'accent': '#212121',
        'accent-hover': '#000000', 'accent-soft': '#f0f0f0',
        'on-accent': '#ffffff', 'focus': '#14509b',
    },
    'dark': {
        'paper': '#121212', 'surface': '#1b1b1b', 'surface-alt': '#242424',
        'ink': '#f5f5f5', 'ink-soft': '#d6d6d6', 'muted': '#a3a3a3',
        'line': '#333333', 'line-strong': '#4d4d4d', 'accent': '#f5f5f5',
        'accent-hover': '#ffffff', 'accent-soft': '#2a2a2a',
        'on-accent': '#121212', 'focus': '#8ab6ff',
    },
}


def _rgb(value):
    value = value.lstrip('#')
    if len(value) == 3:
        value = ''.join(ch * 2 for ch in value)
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def _hex(rgb):
    return '#%02x%02x%02x' % tuple(max(0, min(255, round(c))) for c in rgb)


def _blend(a, b, amount):
    ar, ag, ab = _rgb(a)
    br, bg, bb = _rgb(b)
    return _hex((
        ar + (br - ar) * amount,
        ag + (bg - ag) * amount,
        ab + (bb - ab) * amount,
    ))


def _luminance(color):
    r, g, b = (c / 255 for c in _rgb(color))

    def channel(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def _on_color(color):
    return '#111111' if _luminance(color) > 0.45 else '#ffffff'


def palette(base):
    bg = base['bg']
    fg = base['fg']
    accent = base['accent']
    dark = _luminance(bg) < 0.4

    if dark:
        surface = _blend(bg, '#ffffff', 0.06)
        surface_alt = _blend(bg, '#ffffff', 0.12)
        line = _blend(bg, '#ffffff', 0.18)
        line_strong = _blend(bg, '#ffffff', 0.3)
        ink_soft = _blend(fg, bg, 0.25)
        muted = _blend(fg, bg, 0.5)
        accent_soft = _blend(bg, accent, 0.28)
        accent_hover = _blend(accent, '#ffffff', 0.18)
    else:
        surface = _blend(bg, '#ffffff', 0.65)
        surface_alt = _blend(bg, fg, 0.08)
        line = _blend(bg, fg, 0.14)
        line_strong = _blend(bg, fg, 0.28)
        ink_soft = _blend(fg, bg, 0.2)
        muted = _blend(fg, bg, 0.45)
        accent_soft = _blend(bg, accent, 0.16)
        accent_hover = _blend(accent, '#000000', 0.15)

    return {
        'paper': bg,
        'surface': surface,
        'surface-alt': surface_alt,
        'ink': fg,
        'ink-soft': ink_soft,
        'muted': muted,
        'line': line,
        'line-strong': line_strong,
        'accent': accent,
        'accent-hover': accent_hover,
        'accent-soft': accent_soft,
        'on-accent': _on_color(accent),
        'focus': accent,
    }


def themes_for_display():
    result = []
    for name, theme in THEMES.items():
        if name == 'default':
            light = DEFAULT_PALETTE['light']
            dark = DEFAULT_PALETTE['dark']
        else:
            light = palette(theme['light'])
            dark = palette(theme['dark'])
        result.append({
            'name': name,
            'label': theme['label'],
            'light': light,
            'dark': dark,
        })
    return result


@lru_cache(maxsize=1)
def theme_css():
    blocks = []
    for name, theme in THEMES.items():
        if name == 'default':
            continue
        light = palette(theme['light'])
        dark = palette(theme['dark'])
        light_vars = ''.join(f'  --{key}: {value};\n' for key, value in light.items())
        dark_vars = ''.join(f'  --{key}: {value};\n' for key, value in dark.items())
        blocks.append(f'html[data-theme-style="{name}"]:not([data-theme="dark"]) {{\n{light_vars}}}')
        blocks.append(f'html[data-theme-style="{name}"][data-theme="dark"] {{\n{dark_vars}}}')
    return '\n\n'.join(blocks)
