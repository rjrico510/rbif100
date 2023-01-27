mkdir -p exomesCohort && cat clinical_data.txt | cut -f3,6 | awk '$1 >=20 && $1 <= 30' |
 cut -f2 | xargs -n 1 -I {} cp exomes/{}.fasta exomesCohort/{}.fasta
