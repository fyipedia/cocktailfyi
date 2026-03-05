# cocktailfyi — Interactive Python REPL Demo
Output demo.gif

Set FontSize 14
Set Width 920
Set Height 620
Set Shell "zsh"
Set Theme "Catppuccin Mocha"
Set TypingSpeed 30ms
Set Padding 20

# Install + REPL in one command (uv creates temp env)
Type "uv run --with cocktailfyi python3"
Enter
Sleep 2.5s

# Import
Type "from cocktailfyi import parse_measure_ml, estimate_abv, compute_difficulty"
Enter
Sleep 1.5s

# Measure parsing
Type "parse_measure_ml('2 oz')"
Enter
Sleep 1.5s

Type "parse_measure_ml('1 1/2 oz')"
Enter
Sleep 1.5s

# ABV estimation (Margarita)
Type "estimate_abv([{'abv': 40, 'measure': '2 oz'}, {'abv': 30, 'measure': '1 oz'}, {'abv': 0, 'measure': '1 oz'}])"
Enter
Sleep 2s

# Difficulty scoring
Type "compute_difficulty(5, ['muddling', 'layering'])"
Enter
Sleep 2s

Type "exit()"
Enter
Sleep 1s
