# puzzle-formatter
Simple script to format puzzles for printing


## Usage

```
usage: puzzle-formatter.py [-h] [--game GAME] [--output OUTPUT] n

Create a printable pdf of paper games.

positional arguments:
  n                number of pages desired

optional arguments:
  -h, --help       show this help message and exit
  --game GAME      game desired, choices are 'ksudoku', 'nurikabe',
                   'dominosa', 'loop'
  --output OUTPUT  Path and filename for pdf output
 ```

## Example result
<img src="before.png" width=300 height=300 style="vertical-align:middle" /> => <img src="after.png" width=300 height=330 style="vertical-align:middle" />
