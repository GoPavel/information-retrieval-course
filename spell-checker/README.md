### build 

```
$ poetry install
$ poetry shell
$ export PYTHONPATH=src

$ python eval_submission.py --help                                                                                                       
usage: eval_submission.py [-h] --train TRAIN --words WORDS [--output OUTPUT]
                          --input INPUT

optional arguments:
  -h, --help       show this help message and exit
  --train TRAIN    train csv
  --words WORDS    words csv
  --output OUTPUT  name of output file
  --input INPUT    no_fix csv for queries



$ python eval_submission.py --input data/no_fix.submission.csv --output data/submission.csv --train data/train.csv --words data/words.csv

```