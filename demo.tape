# cocktailfyi — Python Cocktail Engine Demo
Output demo.gif

Set FontSize 20
Set Width 1000
Set Height 580
Set Shell "zsh"
Set Theme "Catppuccin Mocha"
Set TypingSpeed 30ms
Set Padding 24

Type "uv run --with cocktailfyi python3"
Enter
Sleep 2s

Type "from cocktailfyi import parse_measure_ml, estimate_abv"
Enter
Sleep 1s

Type "# Parse cocktail measures"
Enter
Sleep 0.5s

Type "parse_measure_ml('2 oz')"
Enter
Sleep 1.5s

Type "parse_measure_ml('1 1/2 oz')"
Enter
Sleep 1.5s

Type "# Estimate ABV (Margarita)"
Enter
Sleep 0.5s

Type "estimate_abv([{'abv': 40, 'measure': '2 oz'}, {'abv': 30, 'measure': '1 oz'}, {'abv': 0, 'measure': '1 oz'}])"
Enter
Sleep 2.5s

Type "exit()"
Enter
Sleep 1s
