set -o errexit

if (( $# != 1 ))
then
  echo "Usage: bash generate_datasets.sh project"
  exit 1
fi

echo "Calling scripts/generation/generate_dataset.py"
python scripts/generation/generate_dataset.py $1
echo "Calling scripts/generation/surv_split.r"
Rscript scripts/generation/surv_split.r $1
echo "Calling scripts/generation/find_outliers.r"
Rscript scripts/generation/find_outliers.r $1
echo "Calling scripts/generation/filter_dataset.py"
python scripts/generation/filter_dataset.py $1
echo "Calling scripts/generation/impute_dataset.r"
Rscript scripts/generation/impute_dataset.r $1