qfconvert.py -mkey -t"s/r/i 2e rotcw 2s flipv fliph" ..\blueprints\tests\obama.xlsx -PCSX > test.out
@ffind /m /e"Total key cost" test.out
@ffind /m /e"function calls" test.out