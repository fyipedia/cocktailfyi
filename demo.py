from cocktailfyi import (
    compute_difficulty,
    estimate_abv,
    parse_measure_ml,
)

G = "\033[32m"
C = "\033[36m"
Y = "\033[33m"
B = "\033[1m"
D = "\033[2m"
R = "\033[0m"

# 1. Parse measures
print(f"{B}{Y}Measure Parsing{R}")
for m in ["2 oz", "1 cl", "1/2 tsp", "dash"]:
    print(f"  {C}{m:>8}{R} → {G}{parse_measure_ml(m)} ml{R}")

print()

# 2. Estimate ABV (Margarita-like)
ingredients = [
    {"abv": 40, "measure": "2 oz"},  # Tequila
    {"abv": 30, "measure": "1 oz"},  # Triple sec
    {"abv": 0, "measure": "1 oz"},  # Lime juice
]
abv = estimate_abv(ingredients)
print(f"{B}{Y}ABV Estimate{R} {D}(Margarita){R}")
print(f"  {C}Tequila{R}    40% × 2 oz")
print(f"  {C}Triple sec{R} 30% × 1 oz")
print(f"  {C}Lime juice{R}  0% × 1 oz")
print(f"  {C}Result{R}     {B}{G}{abv}%{R}")

print()

# 3. Difficulty
diff = compute_difficulty(5, ["muddling", "layering"])
print(f"{B}{Y}Difficulty{R}")
print(f"  {C}5 ingredients + muddling, layering{R}")
print(f"  {C}Result{R} {G}{diff}{R}")
