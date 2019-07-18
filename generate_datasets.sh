echo "Calling scripts/generation/generate_dataset.py"
python scripts/generation/generate_dataset.py
echo "Calling scripts/generation/find_outliers.r"
Rscript scripts/generation/find_outliers.r
echo "Calling scripts/generation/filter_dataset.py"
python scripts/generation/filter_dataset.py
echo "Calling scripts/generation/impute_dataset.r"
Rscript scripts/generation/impute_dataset.r