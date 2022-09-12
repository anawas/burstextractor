year=2020

# the burst type to process
# use "I", "II", "III", "IV", "V", or "all"
type="V"

for i in 1 2 3 4 5 6 7 8 9 10 11 12
do
python main.py --year $year --month $i --type $type
done
