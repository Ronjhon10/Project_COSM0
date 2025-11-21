import cosmo
from cosmo import *

while True:
    text = input(Colors.BLUE + "COSMO |>")
    result, error = cosmo.run('<stdin>', text)

    if error: print(Colors.RED + error.as_string())
    else: print(result)