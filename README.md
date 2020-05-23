# pylivemaker-tools
These loose scripts can be used to work with the [pylivemaker project](https://github.com/pmrowla/pylivemaker).

googletranslate.py
------------------

This script translates CSV files created with *lmlsb* with the help of google translate
Disclaimer: This script uses an inofficial API. Use at own risk.

extractstrings.py and insertstrings.py
--------------------------------------

These two scripts extract and patch all possible string constants of an lsb file. The format of the CSV file used is very similar to the format of the lmlsb tool.
Make sure that you do not change / translate texts that you cannot assign to an in-game text. It could be that string constants are also used for in-game functions. In this case, a translation can break the game.
In any case, test your game thoroughly after the translation.
